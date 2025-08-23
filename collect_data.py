#!/usr/bin/env python3
"""
Complete integration changes for collect_data.py to add Instagram support.
These modifications add Instagram data collection while preserving all existing functionality.
"""

# ============================================================
# STEP 1: Add to imports section (at the top of collect_data.py)
# ============================================================
# Add this import after the existing imports:
from instagram_client import fetch_instagram_data

# ============================================================
# STEP 2: Add to CONFIGURATION section (keep all secrets together)
# ============================================================
# Add these lines in the CONFIGURATION section, right after YOUTUBE_API_KEY:

# ------------------ CONFIGURATION ------------------

# Spotify API Credentials
CLIENT_ID = '737e719bb4c4413dab75709796eea4f5'
CLIENT_SECRET = '2257b35c9acb46ea817f4a99cf833a8c'

# YouTube API Key
YOUTUBE_API_KEY = 'AIzaSyCgffLM7bMJ2vqw-VBGaNNJWkMQPEfNfgk'

# Instagram API Credentials
INSTAGRAM_ACCESS_TOKEN = 'EAAKuuZBZAgOugBPRZBLNB5fqOaOhKgFXEcux7msZCrsBjfkYeXnj6EhIShff6faTrNu9xEYS4hk3EoikuSI74YJvIyaGRsyEBYEDupLwnHsAJ6LGnTbtdurlbI9sSthCqHthpAV3LKaoSljRhKMTZAuf4xbTlCWrfm5vGTZB3tpl4DEbm1Ttc6TafK8fNmXJtIqgZDZD'  # Replace with actual token
INSTAGRAM_BUSINESS_ACCOUNT_ID = '17841404800001416'  # Your Instagram Business Account numeric ID
INSTAGRAM_API_VERSION = 'v18.0'

# List of artists with their platform IDs
# NOTE: Pax has been completely removed from tracking
# NOTE: 'instagram_id' should contain the Instagram USERNAME (without @)
artists = [
    {
        'name': 'Casa 24',
        'spotify_id': '2QpRYjtwNg9z6KwD4fhC5h',
        'youtube_id': 'UCshvYG0n1I_gXbM8htuANAg',
        'instagram_id': 'casa24records',  # Instagram username (without @)
    },
    {
        'name': 'Chef Lino',
        'spotify_id': '56tisU5xMB4CYyzG99hyBN',
        'youtube_id': 'UCTH5Cs-r1YShzfARJLQ5Hzw',
        'instagram_id': 'chef_lino99',  # Instagram username (without @)
    },
    {
        'name': 'PYRO',
        'spotify_id': '5BsYYsSnFsE9SoovY7aQV0',
        'youtube_id': None,
        'instagram_id': 'PYRO_0201',  # Instagram username (without @)
    },
    {
        'name': 'bo.wlie',
        'spotify_id': '2DqDBHhQzNE3KHZq6yKG96',
        'youtube_id': 'UCWnUHb8KCdprdkBBts9GxSA',
        'instagram_id': 'the.bowlieexperience',  # Instagram username (without @)
    },
    {
        'name': 'Mango Blade',
        'spotify_id': '4vYClJG7K1FGWMMalEW5Hg',
        'youtube_id': 'UCkKr9JaItuEsGRn8QEy5HjA',
        'instagram_id': 'mangobladesonics',  # Instagram username (without @)
    },
    {
        'name': 'ZACKO',
        'spotify_id': '3gXXs7vEDPmeJ2HAOCGi8e',
        'youtube_id': None,
        'instagram_id': 'zacko.____',  # Instagram username (without @)
    },
    {
        'name': 'ARANDA',
        'spotify_id': '7DFovnGo8GZX5PuEyXh6LV',
        'youtube_id': None,
        'instagram_id': 'arandajrr',  # Instagram username (without @)
    },
    {
        'name': 'Casa 24Beats',
        'spotify_id': None,  # No Spotify presence
        'youtube_id': 'UCg3IuQwjIBbkvEbDVJZd8VQ',
        'instagram_id': None,  # Instagram username (without @)
    }
]

# ============================================================
# STEP 3: Modify collect_all_data() function
# ============================================================
# This is the complete updated collect_all_data function with Instagram integration:

def collect_all_data():
    """Collects all artist data from multiple platforms."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        spotify_token = get_spotify_token()
    except Exception as e:
        logging.error(f"Failed to get Spotify token: {e}")
        spotify_token = None
    
    all_artists_data = {
        'date': today,
        'artists': []
    }
    
    # Statistics - now includes Instagram
    stats = {
        'total': len(artists),
        'spotify_success': 0,
        'youtube_success': 0,
        'instagram_success': 0,  # NEW
        'monthly_listeners_found': 0
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
        
        # NEW: Get Instagram data
        instagram_data = fetch_instagram_data(
            artist.get('instagram_id'),  # This should be the Instagram username
            artist['name'],
            INSTAGRAM_ACCESS_TOKEN,
            INSTAGRAM_BUSINESS_ACCOUNT_ID
        )
        if instagram_data['followers'] > 0:
            stats['instagram_success'] += 1
        
        artist_data = {
            'name': artist['name'],
            'spotify': spotify_data,
            'youtube': youtube_data,
            'instagram': instagram_data  # NEW
        }
        
        all_artists_data['artists'].append(artist_data)
        
        # Log progress
        logging.info(f"Progress: {len(all_artists_data['artists'])}/{stats['total']} artists processed")
        
        # Add a small delay between artists
        time.sleep(0.5)
    
    # Log summary statistics - updated to include Instagram
    logging.info("\n" + "="*50)
    logging.info("COLLECTION SUMMARY")
    logging.info("="*50)
    logging.info(f"Total artists: {stats['total']}")
    logging.info(f"Spotify API success: {stats['spotify_success']}/{stats['total']}")
    logging.info(f"Monthly listeners found: {stats['monthly_listeners_found']}/{stats['total']}")
    logging.info(f"YouTube API success: {stats['youtube_success']}/{stats['total']}")
    logging.info(f"Instagram API success: {stats['instagram_success']}/{stats['total']}")  # NEW
    logging.info("="*50)
    
    # Print summary including Instagram
    print("\nData Collection Summary:")
    print("-" * 60)
    for artist in all_artists_data['artists']:
        name = artist['name']
        listeners = artist['spotify']['monthly_listeners']
        yt_subs = artist['youtube']['subscribers']
        ig_followers = artist['instagram']['followers']  # NEW
        print(f"{name:<20} Spotify: {listeners:>10}  YT: {yt_subs:>8}  IG: {ig_followers:>8}")
    print("-" * 60)
    
    return all_artists_data

# ============================================================
# STEP 4: Update the update_historical_data() function
# ============================================================
# Add Instagram data to CSV export:

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
            'instagram_followers': artist['instagram']['followers'],  # NEW
            'instagram_media_count': artist['instagram'].get('media_count', 0)  # NEW
        }
        artists_data.append(artist_info)
    
    df = pandas.DataFrame(artists_data)
    
    # Check if file exists to determine if we need headers
    file_exists = os.path.exists(csv_file)
    df.to_csv(csv_file, mode='a', header=not file_exists, index=False)
    
    logging.info(f"CSV data saved to {csv_file}")

# ============================================================
# STEP 5: Update the main execution block
# ============================================================
# Update the title to reflect Instagram integration:

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MULTI-PLATFORM DATA COLLECTION SCRIPT v3.0")  # Updated version
    print("Collecting: Spotify, YouTube, Instagram")  # Updated description
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
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
    except Exception as e:
        print(f"\nERROR during data collection: {e}")
        logging.exception("Fatal error in main execution")
        raise
