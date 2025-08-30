#!/usr/bin/env python3
"""
Robust Spotify, YouTube, Instagram, and Discord data collection script
Fixed to correctly parse all monthly listener counts including 0
"""

import base64
import requests
import json
import pandas
from datetime import datetime
import os
import re
import time
import random
import logging
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------ CONFIGURATION ------------------

# Spotify API Credentials
CLIENT_ID = '737e719bb4c4413dab75709796eea4f5'
CLIENT_SECRET = '2257b35c9acb46ea817f4a99cf833a8c'

# YouTube API Key
YOUTUBE_API_KEY = 'AIzaSyCgffLM7bMJ2vqw-VBGaNNJWkMQPEfNfgk'

# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN = 'EAAKuuZBZAgOugBPRZBLNB5fqOaOhKgFXEcux7msZCrsBjfkYeXnj6EhIShff6faTrNu9xEYS4hk3EoikuSI74YJvIyaGRsyEBYEDupLwnHsAJ6LGnTbtdurlbI9sSthCqHthpAV3LKaoSljRhKMTZAuf4xbTlCWrfm5vGTZB3tpl4DEbm1Ttc6TafK8fNmXJtIqgZDZD'
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841404800001416'
INSTAGRAM_API_VERSION = 'v18.0'

# Discord Bot Credentials
DISCORD_BOT_TOKEN = 'YOUR_DISCORD_BOT_TOKEN_HERE'  # Replace with your bot token
DISCORD_GUILD_ID = '1000913895415877712'  # Your Discord server ID

# List of artists with their platform IDs
artists = [
    {
        'name': 'Casa 24',
        'spotify_id': '2QpRYjtwNg9z6KwD4fhC5h',
        'youtube_id': 'UCshvYG0n1I_gXbM8htuANAg',
        'instagram_username': 'casa24records',
    },
    {
        'name': 'Chef Lino',
        'spotify_id': '56tisU5xMB4CYyzG99hyBN',
        'youtube_id': 'UCTH5Cs-r1YShzfARJLQ5Hzw',
        'instagram_username': 'chef_lino99',
    },
    {
        'name': 'PYRO',
        'spotify_id': '5BsYYsSnFsE9SoovY7aQV0',
        'youtube_id': None,
        'instagram_username': 'PYRO_0201',
    },
    {
        'name': 'bo.wlie',
        'spotify_id': '2DqDBHhQzNE3KHZq6yKG96',
        'youtube_id': 'UCWnUHb8KCdprdkBBts9GxSA',
        'instagram_username': 'the.bowlieexperience',
    },
    {
        'name': 'Mango Blade',
        'spotify_id': '4vYClJG7K1FGWMMalEW5Hg',
        'youtube_id': 'UCkKr9JaItuEsGRn8QEy5HjA',
        'instagram_username': 'mangobladesonics',
    },
    {
        'name': 'ZACKO',
        'spotify_id': '3gXXs7vEDPmeJ2HAOCGi8e',
        'youtube_id': None,
        'instagram_username': 'zacko.____',
    },
    {
        'name': 'ARANDA',
        'spotify_id': '7DFovnGo8GZX5PuEyXh6LV',
        'youtube_id': None,
        'instagram_username': 'arandajrr',
    },
    {
        'name': 'Casa 24Beats',
        'spotify_id': None,  # No Spotify presence
        'youtube_id': 'UCg3IuQwjIBbkvEbDVJZd8VQ',
        'instagram_username': None,
    }
]

# ------------------ HELPER CLASSES ------------------

class AntiDetectionManager:
    """Manages anti-detection measures for web scraping"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    ]
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Generate realistic browser headers"""
        return {
            'User-Agent': random.choice(AntiDetectionManager.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    
    @staticmethod
    def get_delay(base_delay: float = 1.0) -> float:
        """Generate random delay to mimic human behavior"""
        return random.uniform(base_delay, base_delay * 1.5)

# ------------------ DISCORD FUNCTIONS ------------------

def get_discord_member_count() -> Dict:
    """
    Fetch Discord server member count using bot API.
    
    Returns:
        Dict with Discord server metrics
    """
    if not DISCORD_BOT_TOKEN or DISCORD_BOT_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        logging.warning("Discord bot token not configured, skipping Discord data collection")
        return {
            'member_count': 0,
            'online_count': 0,
            'server_name': None,
            'server_id': None
        }
    
    try:
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        url = f'https://discord.com/api/v10/guilds/{DISCORD_GUILD_ID}?with_counts=true'
        
        logging.info(f"Fetching Discord server member count...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            member_count = data.get('approximate_member_count', 0)
            online_count = data.get('approximate_presence_count', 0)
            server_name = data.get('name', 'Unknown')
            
            logging.info(f"✓ Discord server '{server_name}': {member_count:,} members ({online_count:,} online)")
            
            return {
                'member_count': member_count,
                'online_count': online_count,
                'server_name': server_name,
                'server_id': DISCORD_GUILD_ID
            }
        elif response.status_code == 401:
            logging.error("Discord bot token is invalid")
        elif response.status_code == 403:
            logging.error("Discord bot doesn't have access to this guild")
        elif response.status_code == 404:
            logging.error("Discord guild not found")
        else:
            logging.error(f"Discord API error: {response.status_code}")
            
    except Exception as e:
        logging.error(f"Error getting Discord data: {e}")
    
    return {
        'member_count': 0,
        'online_count': 0,
        'server_name': None,
        'server_id': None
    }

# ------------------ INSTAGRAM FUNCTIONS ------------------

def get_instagram_data(username: str, artist_name: str) -> Dict:
    """
    Fetch Instagram data for a single artist using Business Discovery API.
    """
    if not username:
        logging.info(f"{artist_name} has no Instagram username, skipping Instagram data collection")
        return {
            'followers': 0,
            'media_count': 0,
            'username': None,
            'name': None
        }
    
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_BUSINESS_ACCOUNT_ID:
        logging.warning(f"Instagram credentials not configured for {artist_name}")
        return {
            'followers': 0,
            'media_count': 0,
            'username': username,
            'name': artist_name
        }
    
    try:
        clean_username = username.lstrip('@')
        time.sleep(random.uniform(0.5, 0.75))
        
        url = f"https://graph.facebook.com/{INSTAGRAM_API_VERSION}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}"
        
        params = {
            'fields': f'business_discovery.username({clean_username}){{followers_count,media_count,username,name,biography}}',
            'access_token': INSTAGRAM_ACCESS_TOKEN
        }
        
        logging.info(f"Fetching Instagram data for @{clean_username}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'business_discovery' in data:
                discovery_data = data['business_discovery']
                followers = discovery_data.get('followers_count', 0)
                logging.info(f"✓ Successfully fetched Instagram data for {artist_name}: {followers:,} followers")
                return {
                    'followers': followers,
                    'media_count': discovery_data.get('media_count', 0),
                    'username': discovery_data.get('username', clean_username),
                    'name': discovery_data.get('name', artist_name)
                }
            else:
                logging.warning(f"No business_discovery data found for @{clean_username}")
        elif response.status_code == 400:
            logging.warning(f"Bad request for @{clean_username} - account may be private or not exist")
        elif response.status_code == 429:
            logging.warning(f"Rate limit hit for Instagram API")
            time.sleep(5)
        else:
            logging.error(f"HTTP {response.status_code} error for @{clean_username}")
    
    except Exception as e:
        logging.error(f"Error getting Instagram data for {artist_name}: {e}")
    
    return {
        'followers': 0,
        'media_count': 0,
        'username': username,
        'name': artist_name
    }

# ------------------ SPOTIFY SCRAPING FUNCTIONS (FIXED) ------------------

def parse_listener_number(text: str) -> Optional[int]:
    """
    Parse monthly listeners - properly handles 0, small numbers, and K/M/B notation
    """
    if not text:
        return None
    
    # Clean the text
    text = text.strip()
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u202f', ' ')
    text = text.replace('\\u00B7', '·')
    text = text.replace('\xa0', ' ')
    text = text.replace('&nbsp;', ' ')
    
    # Special handling for "0 monthly listeners"
    if re.search(r'\b0\s*monthly\s*listeners?\b', text, re.IGNORECASE):
        logging.debug(f"Found 0 monthly listeners in text: '{text}'")
        return 0
    
    # Look for K/M/B notation FIRST (with word boundaries to avoid partial matches)
    kmb_patterns = [
        r'\b(\d+(?:[.,]\d+)?)\s*([KMB])\s*monthly\s*listeners?\b',
        r'Artist\s*[·•]\s*(\d+(?:[.,]\d+)?)\s*([KMB])\s*monthly\s*listeners?\b',
    ]
    
    for pattern in kmb_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            number_str = match.group(1).replace(',', '.')
            try:
                number = float(number_str)
                multiplier = match.group(2).upper()
                
                multipliers = {
                    'K': 1000,
                    'M': 1000000,
                    'B': 1000000000
                }
                
                result = int(number * multipliers.get(multiplier, 1))
                logging.debug(f"Parsed K/M/B notation from '{text}': {result}")
                return result
            except ValueError:
                continue
    
    # Now look for raw numbers (including those with commas/periods as separators)
    raw_patterns = [
        r'\b(\d{1,3}(?:[,.\s]\d{3})*)\s*monthly\s*listeners?\b',  # Numbers with separators
        r'\b(\d+)\s*monthly\s*listeners?\b',  # Simple numbers
        r'Artist\s*[·•]\s*(\d{1,3}(?:[,.\s]\d{3})*)\s*monthly\s*listeners?\b',
        r'Artist\s*[·•]\s*(\d+)\s*monthly\s*listeners?\b',
    ]
    
    for pattern in raw_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            number_str = match.group(1).strip()
            
            # Remove separators
            clean_number = re.sub(r'[,.\s]', '', number_str)
            
            try:
                value = int(clean_number)
                if 0 <= value <= 1000000000:  # Valid range
                    logging.debug(f"Parsed raw number from '{text}': {value}")
                    return value
            except ValueError:
                continue
    
    return None

def extract_monthly_listeners_from_html(html_content: str, artist_name: str) -> Optional[int]:
    """
    Extract monthly listeners with improved parsing for all cases including 0
    """
    
    # Clean HTML content
    html_content = html_content.replace('\u00a0', ' ')
    html_content = html_content.replace('\u202f', ' ')
    html_content = html_content.replace('\\u00B7', '·')
    html_content = html_content.replace('\xa0', ' ')
    html_content = html_content.replace('&nbsp;', ' ')
    
    # Strategy 1: Look in meta tags (most reliable)
    meta_patterns = [
        r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"',
        r'<meta[^>]*content="([^"]*)"[^>]*property="og:description"',
        r'<meta[^>]*name="description"[^>]*content="([^"]*)"',
        r'<meta[^>]*content="([^"]*)"[^>]*name="description"',
        r'<meta[^>]*name="twitter:description"[^>]*content="([^"]*)"',
        r'<meta[^>]*content="([^"]*)"[^>]*name="twitter:description"',
    ]
    
    for pattern in meta_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            match = html.unescape(match)
            if 'monthly listener' in match.lower():
                # Extract just the part with monthly listeners
                listener_match = re.search(r'(\d+(?:[.,]\d+)?(?:\s*[KMB])?|\b0)\s*monthly\s*listeners?', match, re.IGNORECASE)
                if listener_match:
                    full_text = listener_match.group(0)
                    listeners = parse_listener_number(full_text)
                    if listeners is not None:
                        logging.info(f"Found {artist_name} listeners in meta tag: {listeners:,} from text: '{full_text}'")
                        return listeners
    
    # Strategy 2: Look for JSON data
    json_patterns = [
        r'"monthlyListeners"\s*:\s*(\d+)',
        r'"monthly_listeners"\s*:\s*(\d+)',
        r'monthlyListeners["\']?\s*:\s*(\d+)',
        r'"stats"\s*:\s*\{[^}]*"monthlyListeners"\s*:\s*(\d+)',
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            try:
                listeners = int(match.group(1))
                logging.info(f"Found {artist_name} listeners in JSON: {listeners:,}")
                return listeners
            except ValueError:
                pass
    
    # Strategy 3: Look in the page text with BeautifulSoup
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Look for monthly listeners in the text
        listener_matches = re.finditer(r'(\d+(?:[.,]\d+)?(?:\s*[KMB])?|\b0)\s*monthly\s*listeners?', text, re.IGNORECASE)
        
        for match in listener_matches:
            full_text = match.group(0)
            listeners = parse_listener_number(full_text)
            if listeners is not None:
                logging.info(f"Found {artist_name} listeners in page text: {listeners:,}")
                return listeners
                
    except Exception as e:
        logging.debug(f"BeautifulSoup parsing error for {artist_name}: {e}")
    
    # Strategy 4: Check for patterns in script tags (React/Next.js apps)
    script_pattern = r'<script[^>]*>(.*?)</script>'
    script_matches = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for script in script_matches:
        if 'monthly' in script.lower() and 'listener' in script.lower():
            # Look for patterns in scripts
            listener_match = re.search(r'(\d+(?:[.,]\d+)?(?:\s*[KMB])?|\b0)\s*monthly\s*listeners?', script, re.IGNORECASE)
            if listener_match:
                full_text = listener_match.group(0)
                listeners = parse_listener_number(full_text)
                if listeners is not None:
                    logging.info(f"Found {artist_name} listeners in script: {listeners:,}")
                    return listeners
    
    # Strategy 5: Look for any occurrence of monthly listeners with flexible spacing
    flexible_patterns = [
        r'(\d+)\s+monthly\s+listeners',
        r'(\d+)\s*monthly\s*listeners',
        r'monthly\s+listeners[:\s]+(\d+)',
        r'has\s+(\d+)\s+monthly\s+listeners',
    ]
    
    for pattern in flexible_patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            try:
                listeners = int(match.group(1))
                if 0 <= listeners <= 1000000000:
                    logging.info(f"Found {artist_name} listeners with flexible pattern: {listeners:,}")
                    return listeners
            except:
                pass
    
    return None

def find_listeners_in_json(obj, depth=0, max_depth=10):
    """Recursively search for monthly listeners in JSON object"""
    if depth > max_depth:
        return None
    
    if isinstance(obj, dict):
        # Check for direct monthly listeners keys
        for key in ['monthly_listeners', 'monthlyListeners', 'listeners', 'monthly']:
            if key in obj:
                if isinstance(obj[key], (int, float)):
                    return int(obj[key])
                elif isinstance(obj[key], str) and obj[key].isdigit():
                    return int(obj[key])
                elif isinstance(obj[key], dict) and 'monthly' in obj[key]:
                    if isinstance(obj[key]['monthly'], (int, float)):
                        return int(obj[key]['monthly'])
        
        # Recursively search
        for value in obj.values():
            result = find_listeners_in_json(value, depth + 1, max_depth)
            if result is not None:
                return result
    
    elif isinstance(obj, list):
        for item in obj:
            result = find_listeners_in_json(item, depth + 1, max_depth)
            if result is not None:
                return result
    
    return None

def create_session_with_retry():
    """Create a session with retry strategy"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_status=False
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_maxsize=10,
        pool_block=True
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def scrape_monthly_listeners(artist_id: str, artist_name: str) -> str:
    """
    Scrapes monthly listeners from Spotify's public artist page
    """
    if not artist_id:
        return "N/A"
    
    try:
        url = f"https://open.spotify.com/artist/{artist_id}"
        
        # Create session with retries
        session = create_session_with_retry()
        
        # Try multiple attempts with different headers
        for attempt in range(3):
            headers = AntiDetectionManager.get_headers()
            
            # Add Spotify-specific headers
            headers.update({
                'Referer': 'https://open.spotify.com/',
                'Origin': 'https://open.spotify.com',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"'
            })
            
            # Vary Accept header
            if attempt == 1:
                headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            elif attempt == 2:
                headers['Accept'] = '*/*'
            
            logging.info(f"Fetching Spotify page for {artist_name} (attempt {attempt + 1}/3)...")
            
            try:
                response = session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                # Extract monthly listeners
                listeners = extract_monthly_listeners_from_html(response.text, artist_name)
                
                if listeners is not None:
                    logging.info(f"✓ Successfully found {artist_name} monthly listeners: {listeners:,}")
                    return str(listeners)
                
                # Add delay before retry
                if attempt < 2:
                    time.sleep(AntiDetectionManager.get_delay(1.5))
                    
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request error on attempt {attempt + 1} for {artist_name}: {e}")
                if attempt < 2:
                    time.sleep(2)
        
        # Final attempt with mobile user agent
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        logging.info(f"Trying mobile user agent for {artist_name}...")
        response = session.get(url, headers=mobile_headers, timeout=10)
        listeners = extract_monthly_listeners_from_html(response.text, artist_name)
        
        if listeners is not None:
            logging.info(f"✓ Found {artist_name} listeners with mobile UA: {listeners:,}")
            return str(listeners)
        
        # Save debug HTML for problematic artists
        if artist_name in ['Casa 24', 'ZACKO', 'Chef Lino']:
            debug_file = f"debug_{artist_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            logging.warning(f"Could not find monthly listeners for {artist_name}. Debug HTML saved to {debug_file}")
            
            # Extra debugging - look for any numbers near "monthly"
            monthly_regions = re.finditer(r'.{0,100}monthly.{0,100}', response.text, re.IGNORECASE)
            for i, match in enumerate(monthly_regions):
                if i < 3:  # First 3 occurrences
                    logging.debug(f"Context around 'monthly' #{i+1}: {repr(match.group())}")
        
        logging.warning(f"✗ Could not find monthly listeners for {artist_name} after all attempts")
        return "N/A"
        
    except Exception as e:
        logging.error(f"Unexpected error scraping {artist_name}: {e}")
        return "N/A"
    finally:
        if 'session' in locals():
            session.close()

def get_spotify_token():
    """Gets an access token from Spotify API."""
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

    headers = {'Authorization': f'Basic {auth_header}'}
    data = {'grant_type': 'client_credentials'}

    try:
        response = requests.post(auth_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        response_data = response.json()
        
        return response_data['access_token']
    except Exception as e:
        logging.error(f"Failed to get Spotify token: {e}")
        raise

def get_spotify_artist_data(artist_id, token, artist_name):
    """Gets name, popularity, followers, and monthly listeners for a Spotify artist."""
    if not artist_id:
        return {
            'popularity_score': 0,
            'followers': 0,
            'monthly_listeners': "N/A",
            'genres': [],
            'top_tracks': []
        }
        
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        artist_data = response.json()

        # Get artist's top tracks
        tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
        tracks_response = requests.get(tracks_url, headers=headers, timeout=10)
        tracks_response.raise_for_status()
        tracks_data = tracks_response.json()
        
        top_tracks = []
        if 'tracks' in tracks_data:
            for track in tracks_data['tracks'][:5]:
                top_tracks.append({
                    'name': track['name'],
                    'popularity': track['popularity'],
                    'preview_url': track.get('preview_url', '')
                })

        # Scrape monthly listeners
        logging.info(f"Scraping monthly listeners for {artist_name}...")
        monthly_listeners = scrape_monthly_listeners(artist_id, artist_name)
        
        # Add a small delay to be respectful
        time.sleep(AntiDetectionManager.get_delay(0.5))

        return {
            'popularity_score': artist_data.get('popularity', 0),
            'followers': artist_data.get('followers', {}).get('total', 0),
            'monthly_listeners': monthly_listeners,
            'genres': artist_data.get('genres', []),
            'top_tracks': top_tracks
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logging.error(f"Spotify API authentication failed for {artist_name}")
        else:
            logging.error(f"HTTP error getting Spotify data for {artist_name}: {e}")
        return {
            'popularity_score': 0,
            'followers': 0,
            'monthly_listeners': "N/A",
            'genres': [],
            'top_tracks': []
        }
    except Exception as e:
        logging.error(f"Error getting Spotify data for {artist_name}: {e}")
        return {
            'popularity_score': 0,
            'followers': 0,
            'monthly_listeners': "N/A",
            'genres': [],
            'top_tracks': []
        }

# ------------------ YOUTUBE FUNCTIONS ------------------

def get_youtube_channel_data(channel_id):
    """Gets YouTube channel stats and top videos."""
    if not channel_id:
        return {'subscribers': 0, 'total_views': 0, 'video_count': 0, 'top_videos': []}

    channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
    
    try:
        response = requests.get(channel_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'items' in data and len(data['items']) > 0:
            stats = data['items'][0]['statistics']
            channel_data = {
                'subscribers': int(stats.get('subscriberCount', 0)),  
                'total_views': int(stats.get('viewCount', 0)),        
                'video_count': int(stats.get('videoCount', 0)),
                'top_videos': []
            }
            
            # Get top videos
            playlist_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={YOUTUBE_API_KEY}"
            playlist_response = requests.get(playlist_url, timeout=10)
            playlist_response.raise_for_status()
            playlist_data = playlist_response.json()
            
            if 'items' in playlist_data and len(playlist_data['items']) > 0:
                uploads_playlist_id = playlist_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=50&key={YOUTUBE_API_KEY}"
                videos_response = requests.get(videos_url, timeout=10)
                videos_response.raise_for_status()
                videos_data = videos_response.json()
                
                if 'items' in videos_data:
                    video_ids = [item['snippet']['resourceId']['videoId'] for item in videos_data['items']]
                    
                    if video_ids:
                        video_stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={','.join(video_ids[:50])}&key={YOUTUBE_API_KEY}"
                        video_stats_response = requests.get(video_stats_url, timeout=10)
                        video_stats_response.raise_for_status()
                        video_stats_data = video_stats_response.json()
                        
                        if 'items' in video_stats_data:
                            videos_with_views = []
                            for video in video_stats_data['items']:
                                view_count = int(video['statistics'].get('viewCount', 0))
                                videos_with_views.append({
                                    'title': video['snippet']['title'],
                                    'views': view_count,
                                    'video_id': video['id'],
                                    'published_at': video['snippet']['publishedAt']
                                })
                            
                            videos_with_views.sort(key=lambda x: x['views'], reverse=True)
                            channel_data['top_videos'] = videos_with_views[:5]
            
            return channel_data
        else:
            logging.warning(f"No YouTube data found for channel {channel_id}")
            return {'subscribers': 0, 'total_views': 0, 'video_count': 0, 'top_videos': []}
            
    except Exception as e:
        logging.error(f"Error getting YouTube data for {channel_id}: {e}")
        return {'subscribers': 0, 'total_views': 0, 'video_count': 0, 'top_videos': []}

# ------------------ MAIN COLLECTION FUNCTION ------------------

def collect_all_data():
    """Collects all artist data from multiple platforms including Discord."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        spotify_token = get_spotify_token()
    except Exception as e:
        logging.error(f"Failed to get Spotify token: {e}")
        spotify_token = None
    
    # Get Discord data once (not per artist)
    discord_data = get_discord_member_count()
    
    all_artists_data = {
        'date': today,
        'discord': discord_data,
        'artists': []
    }
    
    # Statistics
    stats = {
        'total': len(artists),
        'spotify_success': 0,
        'youtube_success': 0,
        'instagram_success': 0,
        'monthly_listeners_found': 0,
        'discord_collected': 1 if discord_data['member_count'] > 0 else 0
    }
    
    for artist in artists:
        logging.info(f"\n{'='*50}")
        logging.info(f"Collecting data for {artist['name']}...")
        logging.info(f"{'='*50}")
        
        # Get Spotify data
        if spotify_token and artist.get('spotify_id'):
            spotify_data = get_spotify_artist_data(
                artist.get('spotify_id'), 
                spotify_token,
                artist['name']
            )
            if spotify_data['popularity_score'] > 0:
                stats['spotify_success'] += 1
            if spotify_data['monthly_listeners'] != "N/A":
                stats['monthly_listeners_found'] += 1
        else:
            logging.info(f"{artist['name']} has no Spotify ID, skipping Spotify data collection")
            spotify_data = {
                'popularity_score': 0,
                'followers': 0,
                'monthly_listeners': "N/A",
                'genres': [],
                'top_tracks': []
            }
        
        # Get YouTube data
        youtube_data = get_youtube_channel_data(artist.get('youtube_id'))
        if youtube_data['subscribers'] > 0:
            stats['youtube_success'] += 1
        
        # Get Instagram data
        instagram_data = get_instagram_data(
            artist.get('instagram_username'),
            artist['name']
        )
        if instagram_data['followers'] > 0:
            stats['instagram_success'] += 1
        
        artist_data = {
            'name': artist['name'],
            'spotify': spotify_data,
            'youtube': youtube_data,
            'instagram': instagram_data
        }
        
        all_artists_data['artists'].append(artist_data)
        
        logging.info(f"Progress: {len(all_artists_data['artists'])}/{stats['total']} artists processed")
        
        # Add a small delay between artists
        time.sleep(0.5)
    
    # Log summary statistics
    logging.info("\n" + "="*50)
    logging.info("COLLECTION SUMMARY")
    logging.info("="*50)
    logging.info(f"Total artists: {stats['total']}")
    logging.info(f"Spotify API success: {stats['spotify_success']}/{stats['total']}")
    logging.info(f"Monthly listeners found: {stats['monthly_listeners_found']}/{stats['total']}")
    logging.info(f"YouTube API success: {stats['youtube_success']}/{stats['total']}")
    logging.info(f"Instagram API success: {stats['instagram_success']}/{stats['total']}")
    logging.info(f"Discord data collected: {'Yes' if stats['discord_collected'] else 'No'}")
    logging.info("="*50)
    
    # Print summary including Discord
    print("\nData Collection Summary:")
    print("-" * 70)
    
    # Discord server info
    if discord_data['member_count'] > 0:
        print(f"Discord Server: {discord_data['server_name']}")
        print(f"  Members: {discord_data['member_count']:,} ({discord_data['online_count']:,} online)")
        print("-" * 70)
    
    # Artist data
    for artist in all_artists_data['artists']:
        name = artist['name']
        listeners = artist['spotify']['monthly_listeners']
        yt_subs = artist['youtube']['subscribers']
        ig_followers = artist['instagram']['followers']
        print(f"{name:<20} Spotify: {listeners:>10}  YT: {yt_subs:>8}  IG: {ig_followers:>8}")
    print("-" * 70)
    
    return all_artists_data

def save_data_as_json(data, filename):
    """Saves the collected data as JSON."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    logging.info(f"Data saved to {filename}")

def update_historical_data(data):
    """Updates the historical data files."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Create directories if they don't exist
    os.makedirs('data/historical', exist_ok=True)
    
    # Save today's data in historical folder
    historical_file = f"data/historical/{today}.json"
    save_data_as_json(data, historical_file)
    
    # Update latest data file
    save_data_as_json(data, 'data/latest.json')
    
    # Also save as CSV for backward compatibility
    csv_file = 'data/popularity_scores.csv'
    artists_data = []
    
    for artist in data['artists']:
        artist_info = {
            'artist_name': artist['name'],
            'date': today,
            'popularity_score': artist['spotify']['popularity_score'],
            'followers': artist['spotify']['followers'],
            'monthly_listeners': artist['spotify']['monthly_listeners'],
            'youtube_subscribers': artist['youtube']['subscribers'],
            'youtube_total_views': artist['youtube']['total_views'],
            'youtube_video_count': artist['youtube']['video_count'],
            'instagram_followers': artist['instagram']['followers'],
            'instagram_media_count': artist['instagram'].get('media_count', 0)
        }
        artists_data.append(artist_info)
    
    # Add Discord data as a separate row if it exists
    if data.get('discord') and data['discord']['member_count'] > 0:
        discord_info = {
            'artist_name': 'Discord Server',
            'date': today,
            'popularity_score': 0,
            'followers': data['discord']['member_count'],
            'monthly_listeners': data['discord']['online_count'],
            'youtube_subscribers': 0,
            'youtube_total_views': 0,
            'youtube_video_count': 0,
            'instagram_followers': 0,
            'instagram_media_count': 0
        }
        artists_data.append(discord_info)
    
    df = pandas.DataFrame(artists_data)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_file)
    df.to_csv(csv_file, mode='a', header=not file_exists, index=False)
    
    logging.info(f"CSV data saved to {csv_file}")

# ------------------ MAIN PROCESS ------------------

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MULTI-PLATFORM DATA COLLECTION SCRIPT v4.0")
    print("Collecting: Spotify, YouTube, Instagram, Discord")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    try:
        # Collect all data
        collected_data = collect_all_data()
        
        # Update historical records
        update_historical_data(collected_data)
        
        print("\n" + "="*60)
        print("DATA COLLECTION COMPLETE!")
        print("="*60)
        print(f"Successfully collected data for {len(collected_data['artists'])} artists")
        if collected_data.get('discord') and collected_data['discord']['member_count'] > 0:
            print(f"Discord server members: {collected_data['discord']['member_count']:,}")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print(f"\nERROR during data collection: {e}")
        logging.exception("Fatal error in main execution")
        raise
