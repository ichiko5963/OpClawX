/**
 * Numbers (.numbers) File Parser
 * Extracts data from Apple's Numbers binary format (.iwa files)
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

/**
 * Parse a single .iwa file (snappy-compressed protobuf)
 * Returns array of records found
 */
function parseIWA(buffer) {
  const records = [];
  let offset = 0;
  
  while (offset < buffer.length) {
    // Read chunk header
    const chunkLen = buffer.readUInt32LE(offset);
    offset += 4;
    
    if (offset + chunkLen > buffer.length) break;
    
    const chunk = buffer.slice(offset, offset + chunkLen);
    offset += chunkLen;
    
    // Try to decompress (snappy-like compression)
    try {
      const decompressed = zlib.inflateSync(chunk);
      records.push(...extractStrings(decompressed));
    } catch {
      // If inflate fails, try raw extraction
      records.push(...extractStrings(chunk));
    }
  }
  
  return records;
}

/**
 * Extract readable strings from binary data
 */
function extractStrings(buffer) {
  const strings = [];
  let current = '';
  
  for (let i = 0; i < buffer.length; i++) {
    const byte = buffer[i];
    // Printable ASCII or common UTF-8 ranges
    if ((byte >= 0x20 && byte <= 0x7E) || 
        (byte >= 0xC0 && byte <= 0xDF) || // UTF-8 2-byte start
        (byte >= 0xE0 && byte <= 0xEF) || // UTF-8 3-byte start
        (byte === 0x09) || // tab
        (byte === 0x0A)) { // newline
      current += String.fromCharCode(byte);
    } else if (byte === 0x00 && current.length > 3) {
      // Null terminator with valid string
      strings.push(current);
      current = '';
    } else {
      if (current.length > 10) {
        strings.push(current);
      }
      current = '';
    }
  }
  
  if (current.length > 10) strings.push(current);
  return strings;
}

/**
 * Extract tabular data from Numbers archive
 */
function extractFromNumbers(zipPath) {
  const AdmZip = require('adm-zip');
  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries();
  
  const allStrings = [];
  const dataLists = [];
  
  for (const entry of entries) {
    if (entry.entryName.endsWith('.iwa')) {
      const buffer = entry.getData();
      const strings = extractStrings(buffer);
      allStrings.push(...strings);
      
      // DataList files contain table data
      if (entry.entryName.includes('DataList')) {
        dataLists.push({
          name: entry.entryName,
          strings: strings.filter(s => s.length > 5)
        });
      }
    }
  }
  
  // Try to reconstruct table structure
  // Look for patterns: dates, numbers, tweet-like text
  const posts = [];
  const textPattern = /.{20,280}/; // X post length range
  const datePattern = /\d{4}[-/]\d{2}[-/]\d{2}/;
  const numberPattern = /\d+/;
  
  // Find potential post texts
  const candidates = allStrings.filter(s => 
    textPattern.test(s) && 
    (s.includes('http') || s.includes('@') || s.includes('#') || s.length > 30)
  );
  
  // Try to find corresponding metrics
  for (let i = 0; i < candidates.length; i++) {
    const text = candidates[i];
    
    // Look for nearby numbers that could be metrics
    const nearbyStrings = allStrings.slice(
      Math.max(0, allStrings.indexOf(text) - 10),
      Math.min(allStrings.length, allStrings.indexOf(text) + 10)
    );
    
    const numbers = nearbyStrings
      .map(s => parseInt(s.replace(/,/g, '')))
      .filter(n => !isNaN(n) && n > 0 && n < 1000000);
    
    if (numbers.length >= 3) {
      posts.push({
        text: text.slice(0, 500), // Limit length
        likes: numbers[0] || 0,
        retweets: numbers[1] || 0,
        replies: numbers[2] || 0,
        impressions: numbers[3] || 0,
        source: 'numbers_extract'
      });
    }
  }
  
  return {
    posts: posts.slice(0, 100), // Limit to 100 posts
    rawStrings: allStrings.slice(0, 1000),
    dataLists: dataLists.length
  };
}

/**
 * Alternative: Extract via command line if numbers-cli available
 */
async function exportNumbersToCSV(numbersPath, outputPath) {
  return new Promise((resolve, reject) => {
    const { exec } = require('child_process');
    
    // Try using macOS Numbers app via AppleScript
    const script = `
      tell application "Numbers"
        open POSIX file "${numbersPath}"
        tell front document
          export to POSIX file "${outputPath}" as CSV
          close
        end tell
      end tell
    `;
    
    exec(`osascript -e '${script}'`, (error) => {
      if (error) {
        // Fallback: manual extraction
        const result = extractFromNumbers(numbersPath);
        fs.writeFileSync(outputPath, convertToCSV(result.posts));
        resolve(result.posts);
      } else {
        // Read the exported CSV
        const csv = fs.readFileSync(outputPath, 'utf8');
        resolve(parseCSV(csv));
      }
    });
  });
}

function convertToCSV(posts) {
  const headers = ['text', 'likes', 'retweets', 'replies', 'impressions', 'source'];
  const rows = posts.map(p => [
    `"${p.text.replace(/"/g, '""')}"`,
    p.likes,
    p.retweets,
    p.replies,
    p.impressions,
    p.source
  ].join(','));
  
  return [headers.join(','), ...rows].join('\n');
}

function parseCSV(csv) {
  const lines = csv.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
  
  return lines.slice(1).map(line => {
    const obj = {};
    const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
    headers.forEach((h, i) => {
      obj[h] = isNaN(values[i]) ? values[i] : parseInt(values[i]) || 0;
    });
    return obj;
  });
}

module.exports = {
  extractFromNumbers,
  exportNumbersToCSV,
  parseIWA,
  extractStrings
};
