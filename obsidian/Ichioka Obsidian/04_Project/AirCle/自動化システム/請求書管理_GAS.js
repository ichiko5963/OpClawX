/**
 * AirCle 請求書管理システム
 * Google Apps Script
 * 
 * 機能:
 * 1. LINE Webhook受信
 * 2. 画像をGoogle Driveに保存
 * 3. スプレッドシートに記録
 * 4. 承認時にLINE通知送信
 */

// ============================================
// 設定（ここを編集）
// ============================================

const CONFIG = {
  // LINE Messaging API
  CHANNEL_ACCESS_TOKEN: 'YOUR_CHANNEL_ACCESS_TOKEN_HERE',
  CHANNEL_SECRET: 'YOUR_CHANNEL_SECRET_HERE',
  
  // Google Drive フォルダID（画像保存先）
  // 新規作成する場合は空文字のままでOK（自動作成される）
  DRIVE_FOLDER_ID: '',
  
  // スプレッドシートID（このスクリプトがバインドされているシートを使う場合は空）
  SPREADSHEET_ID: '',
  
  // シート名
  SHEET_NAME: '請求書'
};

// ============================================
// LINE Webhook 受信
// ============================================

function doPost(e) {
  try {
    const events = JSON.parse(e.postData.contents).events;
    
    for (const event of events) {
      handleEvent(event);
    }
    
    return ContentService.createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    console.error('doPost error:', error);
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput('AirCle Invoice System is running.');
}

// ============================================
// イベント処理
// ============================================

function handleEvent(event) {
  if (event.type !== 'message') return;
  
  const userId = event.source.userId;
  const replyToken = event.replyToken;
  
  // ユーザープロフィール取得
  const profile = getLineProfile(userId);
  const displayName = profile ? profile.displayName : 'Unknown';
  
  if (event.message.type === 'image') {
    // 画像メッセージ
    handleImageMessage(event, userId, displayName, replyToken);
    
  } else if (event.message.type === 'text') {
    // テキストメッセージ（金額・内訳の入力）
    handleTextMessage(event, userId, displayName, replyToken);
  }
}

// ============================================
// 画像メッセージ処理
// ============================================

function handleImageMessage(event, userId, displayName, replyToken) {
  try {
    // 画像を取得
    const messageId = event.message.id;
    const imageBlob = getLineMessageContent(messageId);
    
    // Google Driveに保存
    const folder = getOrCreateFolder();
    const timestamp = Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyyMMdd_HHmmss');
    const fileName = `invoice_${displayName}_${timestamp}.jpg`;
    const file = folder.createFile(imageBlob.setName(fileName));
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    const imageUrl = file.getUrl();
    
    // 一時保存（次のテキストメッセージで金額入力を待つ）
    savePendingInvoice(userId, {
      displayName: displayName,
      imageUrl: imageUrl,
      timestamp: new Date().toISOString()
    });
    
    // 返信
    replyMessage(replyToken, [
      {
        type: 'text',
        text: `📸 画像を受け取りました！\n\n次に、金額と内訳を送ってください。\n\n例: 12000円 動画編集3本`
      }
    ]);
    
  } catch (error) {
    console.error('handleImageMessage error:', error);
    replyMessage(replyToken, [
      {
        type: 'text',
        text: '⚠️ 画像の処理中にエラーが発生しました。もう一度お試しください。'
      }
    ]);
  }
}

// ============================================
// テキストメッセージ処理
// ============================================

function handleTextMessage(event, userId, displayName, replyToken) {
  const text = event.message.text;
  
  // 保留中の請求書があるか確認
  const pending = getPendingInvoice(userId);
  
  if (pending) {
    // 金額と内訳を解析
    const parsed = parseAmountAndDescription(text);
    
    if (parsed.amount > 0) {
      // スプレッドシートに記録
      addInvoiceToSheet({
        timestamp: new Date(),
        displayName: pending.displayName,
        lineUserId: userId,
        amount: parsed.amount,
        description: parsed.description,
        imageUrl: pending.imageUrl
      });
      
      // 保留データを削除
      clearPendingInvoice(userId);
      
      // 返信
      const withholdingAmount = Math.round(parsed.amount * 0.8979);
      replyMessage(replyToken, [
        {
          type: 'text',
          text: `✅ 請求書を受け付けました！\n\n━━━━━━━━━━━━━━━━━\n📝 ${parsed.description}\n💰 ${parsed.amount.toLocaleString()}円\n💵 源泉徴収後: ${withholdingAmount.toLocaleString()}円\n━━━━━━━━━━━━━━━━━\n\n承認されるとお知らせします！`
        }
      ]);
      
    } else {
      // 金額が解析できなかった
      replyMessage(replyToken, [
        {
          type: 'text',
          text: '⚠️ 金額を認識できませんでした。\n\n「12000円 動画編集3本」のように送ってください。'
        }
      ]);
    }
    
  } else {
    // 保留中の請求書がない
    replyMessage(replyToken, [
      {
        type: 'text',
        text: '📋 請求書を送るには、まず請求書の画像を送ってください。'
      }
    ]);
  }
}

// ============================================
// 金額・内訳解析
// ============================================

function parseAmountAndDescription(text) {
  // 金額パターン: 12000円, 12,000円, 1万2000円, etc.
  let amount = 0;
  let description = text;
  
  // 「〇万」パターン
  const manPattern = /(\d+)万(\d*)/;
  const manMatch = text.match(manPattern);
  if (manMatch) {
    amount = parseInt(manMatch[1]) * 10000 + (manMatch[2] ? parseInt(manMatch[2]) : 0);
  }
  
  // 通常の数字パターン
  if (amount === 0) {
    const numPattern = /(\d{1,3}(?:,\d{3})*|\d+)\s*円?/;
    const numMatch = text.match(numPattern);
    if (numMatch) {
      amount = parseInt(numMatch[1].replace(/,/g, ''));
    }
  }
  
  // 金額部分を除いた説明
  description = text
    .replace(/(\d{1,3}(?:,\d{3})*|\d+)\s*円?/g, '')
    .replace(/(\d+)万(\d*)/g, '')
    .trim();
  
  if (!description) {
    description = '（内訳なし）';
  }
  
  return { amount, description };
}

// ============================================
// スプレッドシート操作
// ============================================

function getSheet() {
  let ss;
  if (CONFIG.SPREADSHEET_ID) {
    ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  } else {
    ss = SpreadsheetApp.getActiveSpreadsheet();
  }
  return ss.getSheetByName(CONFIG.SHEET_NAME);
}

function addInvoiceToSheet(data) {
  const sheet = getSheet();
  const withholdingAmount = Math.round(data.amount * 0.8979);
  
  sheet.appendRow([
    Utilities.formatDate(data.timestamp, 'Asia/Tokyo', 'yyyy-MM-dd HH:mm:ss'),
    data.displayName,
    data.lineUserId,
    data.amount,
    data.description,
    withholdingAmount,
    data.imageUrl,
    false,  // 承認
    false,  // 通知済
    ''      // メモ
  ]);
}

// ============================================
// 承認時の通知（onEdit トリガー）
// ============================================

function onEdit(e) {
  const sheet = e.source.getActiveSheet();
  if (sheet.getName() !== CONFIG.SHEET_NAME) return;
  
  const range = e.range;
  const col = range.getColumn();
  const row = range.getRow();
  
  // H列（承認）が編集された場合
  if (col === 8 && row >= 2) {
    const isApproved = range.getValue();
    const isNotified = sheet.getRange(row, 9).getValue();
    
    if (isApproved && !isNotified) {
      // 通知を送信
      const lineUserId = sheet.getRange(row, 3).getValue();
      const amount = sheet.getRange(row, 4).getValue();
      const withholdingAmount = sheet.getRange(row, 6).getValue();
      const description = sheet.getRange(row, 5).getValue();
      
      const success = sendApprovalNotification(lineUserId, amount, withholdingAmount, description);
      
      if (success) {
        // 通知済みフラグを立てる
        sheet.getRange(row, 9).setValue(true);
      }
    }
  }
}

function sendApprovalNotification(userId, amount, withholdingAmount, description) {
  try {
    const message = {
      type: 'text',
      text: `✅ 請求書が承認されました！\n\n━━━━━━━━━━━━━━━━━\n📝 ${description}\n💰 ${amount.toLocaleString()}円\n💵 振込額: ${withholdingAmount.toLocaleString()}円\n━━━━━━━━━━━━━━━━━\n\n振込は月末に行います。\nありがとうございました！`
    };
    
    pushMessage(userId, [message]);
    return true;
    
  } catch (error) {
    console.error('sendApprovalNotification error:', error);
    return false;
  }
}

// ============================================
// LINE API ヘルパー
// ============================================

function getLineProfile(userId) {
  try {
    const url = `https://api.line.me/v2/bot/profile/${userId}`;
    const response = UrlFetchApp.fetch(url, {
      headers: {
        'Authorization': `Bearer ${CONFIG.CHANNEL_ACCESS_TOKEN}`
      }
    });
    return JSON.parse(response.getContentText());
  } catch (error) {
    console.error('getLineProfile error:', error);
    return null;
  }
}

function getLineMessageContent(messageId) {
  const url = `https://api-data.line.me/v2/bot/message/${messageId}/content`;
  const response = UrlFetchApp.fetch(url, {
    headers: {
      'Authorization': `Bearer ${CONFIG.CHANNEL_ACCESS_TOKEN}`
    }
  });
  return response.getBlob();
}

function replyMessage(replyToken, messages) {
  const url = 'https://api.line.me/v2/bot/message/reply';
  UrlFetchApp.fetch(url, {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${CONFIG.CHANNEL_ACCESS_TOKEN}`
    },
    payload: JSON.stringify({
      replyToken: replyToken,
      messages: messages
    })
  });
}

function pushMessage(userId, messages) {
  const url = 'https://api.line.me/v2/bot/message/push';
  UrlFetchApp.fetch(url, {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${CONFIG.CHANNEL_ACCESS_TOKEN}`
    },
    payload: JSON.stringify({
      to: userId,
      messages: messages
    })
  });
}

// ============================================
// Google Drive ヘルパー
// ============================================

function getOrCreateFolder() {
  if (CONFIG.DRIVE_FOLDER_ID) {
    return DriveApp.getFolderById(CONFIG.DRIVE_FOLDER_ID);
  }
  
  // フォルダがなければ作成
  const folderName = 'AirCle_請求書画像';
  const folders = DriveApp.getFoldersByName(folderName);
  
  if (folders.hasNext()) {
    return folders.next();
  } else {
    return DriveApp.createFolder(folderName);
  }
}

// ============================================
// 一時保存（PropertiesService使用）
// ============================================

function savePendingInvoice(userId, data) {
  const props = PropertiesService.getScriptProperties();
  props.setProperty(`pending_${userId}`, JSON.stringify(data));
}

function getPendingInvoice(userId) {
  const props = PropertiesService.getScriptProperties();
  const data = props.getProperty(`pending_${userId}`);
  return data ? JSON.parse(data) : null;
}

function clearPendingInvoice(userId) {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty(`pending_${userId}`);
}

// ============================================
// テスト用関数
// ============================================

function testParseAmount() {
  const testCases = [
    '12000円 動画編集3本',
    '1万2000円 サムネ作成',
    '4,000円 講義編集',
    '8000 イベント運営',
  ];
  
  for (const tc of testCases) {
    const result = parseAmountAndDescription(tc);
    console.log(`Input: "${tc}" → Amount: ${result.amount}, Description: "${result.description}"`);
  }
}
