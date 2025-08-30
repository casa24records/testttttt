import requests
import json
import sys
from datetime import datetime

# ===== CONFIGURATION =====
BOT_TOKEN = "MTQxMDc2MDEzODQ0ODcwMzYwMw.GepEah.m-bnhMtnMrbSPAn9b8CJ6A198FwaaEavXH_el0"  # Replace with your full bot token
GUILD_ID = "1000913895415877712"   # Your Discord server ID

# ===== COLOR CODES FOR OUTPUT =====
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print(f"{BLUE}{'='*60}")
print("DISCORD BOT DEBUGGING SCRIPT")
print(f"{'='*60}{RESET}\n")

# ===== 1. CHECK TOKEN FORMAT =====
print(f"{YELLOW}[1] Checking Token Format...{RESET}")
print(f"    Token length: {len(BOT_TOKEN)} characters")

if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print(f"{RED}    ✗ ERROR: Token not replaced! Please paste your actual token.{RESET}")
    sys.exit(1)

if len(BOT_TOKEN) < 50:
    print(f"{RED}    ✗ ERROR: Token too short! Discord tokens are usually 70+ characters.{RESET}")
    print(f"    Your token might be incomplete.")
    
token_parts = BOT_TOKEN.split('.')
print(f"    Token parts: {len(token_parts)} (should be 3)")

if len(token_parts) != 3:
    print(f"{RED}    ✗ ERROR: Invalid token format! Token should have 3 parts separated by dots.{RESET}")
    print(f"    Example format: XXXXXXX.XXXXXX.XXXXXXXXX")
else:
    print(f"{GREEN}    ✓ Token format looks correct (3 parts found){RESET}")
    print(f"    Part 1 length: {len(token_parts[0])}")
    print(f"    Part 2 length: {len(token_parts[1])}")
    print(f"    Part 3 length: {len(token_parts[2])}")

# ===== 2. TEST BOT AUTHENTICATION =====
print(f"\n{YELLOW}[2] Testing Bot Authentication...{RESET}")
headers = {
    'Authorization': f'Bot {BOT_TOKEN}',
    'Content-Type': 'application/json',
    'User-Agent': 'DiscordBot (Debug Script, 1.0)'
}

try:
    response = requests.get(
        'https://discord.com/api/v10/users/@me',
        headers=headers,
        timeout=10
    )
    
    print(f"    Response Status Code: {response.status_code}")
    print(f"    Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        bot_info = response.json()
        print(f"{GREEN}    ✓ Bot authenticated successfully!{RESET}")
        print(f"    Bot Username: {bot_info.get('username', 'Unknown')}")
        print(f"    Bot ID: {bot_info.get('id', 'Unknown')}")
        print(f"    Bot Discriminator: {bot_info.get('discriminator', '0')}")
        bot_is_verified = True
        
    elif response.status_code == 401:
        print(f"{RED}    ✗ AUTHENTICATION FAILED: Invalid token{RESET}")
        print(f"    Response body: {response.text}")
        print(f"\n    Possible reasons:")
        print(f"    1. Token is incorrect or incomplete")
        print(f"    2. Token has been regenerated (old token won't work)")
        print(f"    3. Token was not copied completely from Discord Developer Portal")
        print(f"\n    Solution: Go to Discord Developer Portal > Your App > Bot > Reset Token")
        bot_is_verified = False
        
    elif response.status_code == 429:
        print(f"{RED}    ✗ RATE LIMITED: Too many requests{RESET}")
        retry_after = response.headers.get('Retry-After', 'Unknown')
        print(f"    Retry after: {retry_after} seconds")
        bot_is_verified = False
        
    else:
        print(f"{RED}    ✗ Unexpected response: {response.status_code}{RESET}")
        print(f"    Response body: {response.text}")
        bot_is_verified = False
        
except requests.exceptions.ConnectionError:
    print(f"{RED}    ✗ CONNECTION ERROR: Cannot reach Discord API{RESET}")
    print(f"    Check your internet connection")
    bot_is_verified = False
    
except requests.exceptions.Timeout:
    print(f"{RED}    ✗ TIMEOUT: Request took too long{RESET}")
    bot_is_verified = False
    
except Exception as e:
    print(f"{RED}    ✗ UNEXPECTED ERROR: {e}{RESET}")
    bot_is_verified = False

# ===== 3. CHECK GUILD ID FORMAT =====
print(f"\n{YELLOW}[3] Checking Guild ID Format...{RESET}")
print(f"    Guild ID: {GUILD_ID}")
print(f"    Guild ID length: {len(GUILD_ID)} characters")

if not GUILD_ID.isdigit():
    print(f"{RED}    ✗ ERROR: Guild ID should only contain numbers!{RESET}")
elif len(GUILD_ID) < 17 or len(GUILD_ID) > 20:
    print(f"{RED}    ✗ WARNING: Guild ID length unusual (typically 18-19 digits){RESET}")
else:
    print(f"{GREEN}    ✓ Guild ID format looks correct{RESET}")

# ===== 4. TEST GUILD ACCESS =====
if bot_is_verified:
    print(f"\n{YELLOW}[4] Testing Guild Access...{RESET}")
    
    try:
        response = requests.get(
            f'https://discord.com/api/v10/guilds/{GUILD_ID}?with_counts=true',
            headers=headers,
            timeout=10
        )
        
        print(f"    Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            guild_data = response.json()
            print(f"{GREEN}    ✓ Successfully accessed guild!{RESET}")
            print(f"\n    {BLUE}=== GUILD INFORMATION ==={RESET}")
            print(f"    Server Name: {guild_data.get('name', 'Unknown')}")
            print(f"    Server ID: {guild_data.get('id', 'Unknown')}")
            print(f"    Member Count: {guild_data.get('approximate_member_count', 'Unknown'):,}")
            print(f"    Online Count: {guild_data.get('approximate_presence_count', 'Unknown'):,}")
            print(f"    Server Created: {guild_data.get('created_at', 'Unknown')}")
            print(f"    {BLUE}========================={RESET}")
            
        elif response.status_code == 403:
            print(f"{RED}    ✗ ACCESS DENIED: Bot cannot access this guild{RESET}")
            print(f"    Response body: {response.text}")
            print(f"\n    Possible reasons:")
            print(f"    1. Bot is not in the server")
            print(f"    2. Bot was kicked or banned from the server")
            print(f"    3. Bot lacks necessary permissions")
            print(f"\n    Solution: Re-invite the bot to your server using OAuth2 URL Generator")
            
        elif response.status_code == 404:
            print(f"{RED}    ✗ NOT FOUND: Guild does not exist{RESET}")
            print(f"    The Guild ID might be incorrect")
            print(f"\n    How to get correct Guild ID:")
            print(f"    1. Open Discord")
            print(f"    2. Go to User Settings > Advanced")
            print(f"    3. Enable 'Developer Mode'")
            print(f"    4. Right-click your server name")
            print(f"    5. Click 'Copy Server ID'")
            
        elif response.status_code == 429:
            print(f"{RED}    ✗ RATE LIMITED: Too many requests{RESET}")
            retry_after = response.headers.get('Retry-After', 'Unknown')
            print(f"    Retry after: {retry_after} seconds")
            
        else:
            print(f"{RED}    ✗ Unexpected response: {response.status_code}{RESET}")
            print(f"    Response body: {response.text}")
            
    except Exception as e:
        print(f"{RED}    ✗ ERROR accessing guild: {e}{RESET}")
else:
    print(f"\n{YELLOW}[4] Skipping Guild Access Test (bot not authenticated){RESET}")

# ===== 5. TEST ALTERNATIVE ENDPOINTS =====
if bot_is_verified:
    print(f"\n{YELLOW}[5] Testing Alternative Endpoints...{RESET}")
    
    # Test getting bot's guilds
    print(f"    Testing bot's guild list...")
    try:
        response = requests.get(
            'https://discord.com/api/v10/users/@me/guilds',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            guilds = response.json()
            print(f"    Bot is in {len(guilds)} guild(s)")
            
            # Check if our target guild is in the list
            target_found = False
            for guild in guilds:
                if guild['id'] == GUILD_ID:
                    print(f"{GREEN}    ✓ Target guild found in bot's guild list!{RESET}")
                    print(f"      Name: {guild.get('name', 'Unknown')}")
                    print(f"      Bot's permissions: {guild.get('permissions', 'Unknown')}")
                    target_found = True
                    break
            
            if not target_found:
                print(f"{RED}    ✗ Target guild NOT in bot's guild list{RESET}")
                print(f"    The bot is not in guild {GUILD_ID}")
                print(f"\n    Guilds the bot IS in:")
                for guild in guilds[:5]:  # Show first 5
                    print(f"      - {guild.get('name', 'Unknown')} (ID: {guild.get('id', 'Unknown')})")
                    
    except Exception as e:
        print(f"    Could not fetch guild list: {e}")

# ===== 6. FINAL SUMMARY =====
print(f"\n{BLUE}{'='*60}")
print("DEBUGGING SUMMARY")
print(f"{'='*60}{RESET}")

print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Token Status: {'✓ Valid' if bot_is_verified else '✗ Invalid'}")
print(f"Guild ID: {GUILD_ID}")

if not bot_is_verified:
    print(f"\n{RED}MAIN ISSUE: Bot token is invalid or not working{RESET}")
    print(f"\n{YELLOW}NEXT STEPS:{RESET}")
    print(f"1. Go to https://discord.com/developers/applications")
    print(f"2. Select your application")
    print(f"3. Go to 'Bot' section")
    print(f"4. Click 'Reset Token'")
    print(f"5. Copy the ENTIRE new token")
    print(f"6. Replace it in this script and run again")
    
print(f"\n{BLUE}{'='*60}{RESET}")
