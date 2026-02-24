#!/usr/bin/env python3
"""
X (Twitter) API Client for AirCle Automation
 handles posting, fetching, media extraction
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

class XAPIClient:
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or os.path.expanduser("~/.config/x-automation/credentials.json")
        self.bearer_token = None
        self.api_key = None
        self.api_secret = None
        self.access_token = None
        self.access_token_secret = None
        self.load_credentials()
    
    def load_credentials(self):
        """Load credentials from file or environment"""
        cred_file = Path(self.credentials_path)
        if cred_file.exists():
            with open(cred_file) as f:
                creds = json.load(f)
                self.bearer_token = creds.get("bearer_token")
                self.api_key = creds.get("api_key")
                self.api_secret = creds.get("api_secret")
                self.access_token = creds.get("access_token")
                self.access_token_secret = creds.get("access_token_secret")
        else:
            # Try environment variables
            self.bearer_token = os.getenv("X_BEARER_TOKEN")
            self.api_key = os.getenv("X_API_KEY")
            self.api_secret = os.getenv("X_API_SECRET")
            self.access_token = os.getenv("X_ACCESS_TOKEN")
            self.access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    def get_headers(self):
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
    
    def fetch_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """Fetch recent tweets from a user"""
        # First get user ID
        user_id = self.get_user_id(username)
        if not user_id:
            return []
        
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url,type,variant"
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 200:
                data = response.json()
                return self._parse_tweets(data)
        except Exception as e:
            print(f"Error fetching tweets: {e}")
        return []
    
    def get_user_id(self, username: str) -> Optional[str]:
        """Get Twitter user ID from username"""
        # Remove @ if present
        username = username.lstrip("@")
        
        url = "https://api.twitter.com/2/users/by"
        params = {"username": username}
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("id")
        except Exception as e:
            print(f"Error getting user ID: {e}")
        return None
    
    def _parse_tweets(self, data: Dict) -> List[Dict]:
        """Parse Twitter API response"""
        tweets = data.get("data", [])
        includes = data.get("includes", {})
        media_map = {}
        
        # Build media map
        if "media" in includes:
            for m in includes["media"]:
                media_map[m["media_key"]] = m
        
        parsed = []
        for tweet in tweets:
            parsed_tweet = {
                "id": tweet.get("id"),
                "text": tweet.get("text"),
                "created_at": tweet.get("created_at"),
                "likes": tweet.get("public_metrics", {}).get("like_count", 0),
                "retweets": tweet.get("public_metrics", {}).get("retweet_count", 0),
                "replies": tweet.get("public_metrics", {}).get("reply_count", 0),
                "media": []
            }
            
            # Add media
            if "attachments" in tweet:
                for key in tweet["attachments"].get("media_keys", []):
                    if key in media_map:
                        m = media_map[key]
                        parsed_tweet["media"].append({
                            "type": m.get("type"),
                            "url": m.get("url") or m.get("preview_image_url"),
                            "variant": m.get("variant", {}).get("url") if m.get("type") == "video" else None
                        })
            
            parsed.append(parsed_tweet)
        
        return parsed
    
    def search_recent_tweets(
        self,
        query: str,
        max_results: int = 100,
        min_likes: int = 1000,
        hours_ahead: int = 24
    ) -> List[Dict]:
        """Search recent tweets with filters"""
        # Build query
        search_query = f"{query} lang:ja OR lang:en -is:retweet"
        
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {
            "query": search_query,
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,attachments",
            "expansions": "attachments.media_keys",
            "media.fields": "url,preview_image_url,type,variant"
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            if response.status_code == 200:
                data = response.json()
                tweets = self._parse_tweets(data)
                # Filter by likes
                return [t for t in tweets if t["likes"] >= min_likes]
        except Exception as e:
            print(f"Error searching tweets: {e}")
        return []
    
    def post_tweet(self, text: str, media_ids: List[str] = None, reply_to: str = None) -> Optional[Dict]:
        """Post a new tweet"""
        url = "https://api.twitter.com/2/tweets"
        
        payload = {"text": text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}
        
        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error posting: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error posting tweet: {e}")
        return None
    
    def upload_media(self, media_path: str) -> Optional[str]:
        """Upload media and return media ID"""
        # This requires OAuth 1.0a or OAuth 2.0 with write permissions
        # For now, return None - will be implemented with proper auth
        print(f"Media upload not implemented yet: {media_path}")
        return None
    
    def download_media(self, url: str, output_path: str) -> bool:
        """Download media from URL"""
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                return True
        except Exception as e:
            print(f"Error downloading media: {e}")
        return False


# Monitored accounts
MONITORED_ACCOUNTS = [
    "openclaw",
    "cursor_ai", 
    "vercel",
    "antigravity",
    "AnthropicAI",
    "geminicli",
    "OpenAI"
]

# Keywords for trending search
TRENDING_KEYWORDS = [
    "ClaudeCode",
    "Opus",
    "Antigravity",
    "GeminiCLI",
    "Codex",
    "Cursor",
    "vercel",
    "supabase",
    "Next.js",
    "react",
    "Vibe Coding",
    "OpenClaw"
]


if __name__ == "__main__":
    client = XAPIClient()
    
    # Test: Get user ID
    print("Testing X API Client...")
    user_id = client.get_user_id("openclaw")
    print(f"OpenClaw User ID: {user_id}")
