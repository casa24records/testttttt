#!/usr/bin/env python3
"""
Robust Spotify, YouTube, Instagram, and Discord data collection script
Handles K/M/B notation and meta tag extraction
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
# NOTE: Pax has been completely removed from tracking
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
        'instagram_username': None,  # No Instagram presence
    }
]

# ------------------ HELPER CLASSES ------------------

class AntiDetectionManager:
    """Manages anti-detection measures for web scraping"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
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
            'Pragma': 'no-cache'
        }
    
    @staticmethod
    def get_delay(base_delay: float = 1.0) -> float:
        """Generate random delay to mimic human behavior"""
        return random.uniform(base_delay, base_delay * 1.5)

# ------------------ DISCORD FUNCTIONS ------------------

def get_discord_member_count() -> Dict:
    """
    Fetch Discord server member count using bot token.
    
    Returns:
        Dict with Discord server metrics
    """
    if not DISCORD_BOT_TOKEN or DISCORD_BOT_TOKEN == 'YOUR_DISCORD_BOT_TOKEN_HERE':
        logging.warning("Discord bot token not configured, skipping Discord data collection")
        return {
            'server_name': None,
            'member_count': 0,
            'online_count': 0,
            'collected_at': datetime.now().isoformat()
        }
    
    if not DISCORD_GUILD_ID:
        logging.warning("Discord guild ID not configured")
        return {
            'server_name': None,
            'member_count': 0,
            'online_count': 0,
            'collected_at': datetime.now().isoformat()
        }
    
    try:
        # Set up headers with bot authentication
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Discord API endpoint for guild info with counts
        url = f'https://discord.com/api/v10/guilds/{DISCORD_GUILD_ID}?with_counts=true'
        
        logging.info(f"Fetching Discord server data...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            server_name = data.get('name', 'Unknown')
            member_count = data.get('approximate_member_count', 0)
            online_count = data.get('approximate_presence_count', 0)
            
            logging.info(f"✓ Successfully fetched Discord data: {server_name} - {member_count:,} members ({online_count:,} online)")
            
            return {
                'server_name': server_name,
                'member_count': member_count,
                'online_count': online_count,
                'collected_at': datetime.now().isoformat()
            }
            
        elif response.status_code == 401:
            logging.error("Discord: Invalid bot token - check your token")
            return {
                'server_name': 'Auth Error',
                'member_count': 0,
                'online_count': 0,
                'collected_at': datetime.now().isoformat()
            }
        elif response.status_code == 403:
            logging.error("Discord: Bot doesn't have access to this guild")
            return {
                'server_name': 'Access Denied',
                'member_count': 0,
                'online_count': 0,
                'collected_at': datetime.now().isoformat()
            }
        elif response.status_code == 429:
            logging.warning("Discord: Rate limited - will retry later")
            return {
                'server_name': 'Rate Limited',
                'member_count': 0,
                'online_count': 0,
                'collected_at': datetime.now().isoformat()
            }
        else:
            logging.error(f"Discord API error: {response.status_code}")
            return {
                'server_name': 'API Error',
                'member_count': 0,
                'online_count': 0,
                'collected_at': datetime.now().isoformat()
            }
            
    except Exception as e:
        logging.error(f"Error fetching Discord data: {e}")
        return {
            'server_name': 'Error',
            'member_count': 0,
            'online_count': 0,
            'collected_at': datetime.now().isoformat()
        }

# [Keep all the existing Instagram, Spotify, and YouTube functions as they are]
# ... (all the existing code for Instagram, Spotify, YouTube remains unchanged) ...

# ------------------ MAIN COLLECTION FUNCTION ------------------

def collect_all_data():
    """Collects all artist data from multiple platforms plus Discord server data."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        spotify_token = get_spotify_token()
    except Exception as e:
        logging.error(f"Failed to get Spotify token: {e}")
        spotify_token = None
    
    # Get Discord server data (separate from artists)
    logging.info(f"\n{'='*50}")
    logging.info("Collecting Discord server data...")
    logging.info(f"{'='*50}")
    discord_data = get_discord_member_count()
    
    all_artists_data = {
        'date': today,
        'discord': discord_data,  # Add Discord data at the top level
        'artists': []
    }
    
    # Statistics - now includes Instagram and Discord
    stats = {
        'total': len(artists),
        'spotify_success': 0,
        'youtube_success': 0,
        'instagram_success': 0,
        'monthly_listeners_found': 0,
        'discord_success': 1 if discord_data['member_count'] > 0 else 0
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
        
        # Log progress
        logging.info(f"Progress: {len(all_artists_data['artists'])}/{stats['total']} artists processed")
        
        # Add a small delay between artists
        time.sleep(0.5)
    
    # Log summary statistics - updated to include Discord
    logging.info("\n" + "="*50)
    logging.info("COLLECTION SUMMARY")
    logging.info("="*50)
    logging.info(f"Total artists: {stats['total']}")
    logging.info(f"Spotify API success: {stats['spotify_success']}/{stats['total']}")
    logging.info(f"Monthly listeners found: {stats['monthly_listeners_found']}/{stats['total']}")
    logging.info(f"YouTube API success: {stats['youtube_success']}/{stats['total']}")
    logging.info(f"Instagram API success: {stats['instagram_success']}/{stats['total']}")
    logging.info(f"Discord server data: {'✓' if stats['discord_success'] else '✗'}")
    logging.info("="*50)
    
    # Print summary including Discord
    print("\nData Collection Summary:")
    print("-" * 60)
    
    # Print Discord server info
    print(f"{'Discord Server':<20} Members: {discord_data['member_count']:>8}  Online: {discord_data['online_count']:>8}")
    print("-" * 60)
    
    # Print artist info
    for artist in all_artists_data['artists']:
        name = artist['name']
        listeners = artist['spotify']['monthly_listeners']
        yt_subs = artist['youtube']['subscribers']
        ig_followers = artist['instagram']['followers']
        print(f"{name:<20} Spotify: {listeners:>10}  YT: {yt_subs:>8}  IG: {ig_followers:>8}")
    print("-" * 60)
    
    return all_artists_data

def update_historical_data(data):
    """Updates the historical data files including Discord data."""
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
    
    # Add Discord server data as a special entry
    discord_info = {
        'artist_name': 'DISCORD_SERVER',
        'date': today,
        'popularity_score': 0,
        'followers': 0,
        'monthly_listeners': 'N/A',
        'youtube_subscribers': 0,
        'youtube_total_views': 0,
        'youtube_video_count': 0,
        'instagram_followers': 0,
        'instagram_media_count': 0,
        'discord_members': data['discord']['member_count'],
        'discord_online': data['discord']['online_count']
    }
    artists_data.append(discord_info)
    
    # Add artist data
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
            'instagram_media_count': artist['instagram'].get('media_count', 0),
            'discord_members': 0,  # Artists don't have Discord data
            'discord_online': 0
        }
        artists_data.append(artist_info)
    
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
        print(f"Discord server: {collected_data['discord']['member_count']} members")
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print(f"\nERROR during data collection: {e}")
        logging.exception("Fatal error in main execution")
        raise
