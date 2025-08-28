import requests

# Replace these with your actual values
BOT_TOKEN = "MTQxMDc2MDEzODQ0ODcwMzYwMw.GkXwBQ.OuKZc7kIRqc1E8kI9q0yCUSF7aB5O0QNnowi54"
GUILD_ID = "1000913895415877712"

print("Testing Discord bot connection...")
print(f"Using Guild ID: {GUILD_ID}")
print(f"Token starts with: {BOT_TOKEN[:20]}..." if len(BOT_TOKEN) > 20 else "Token too short")

# First, test if the bot token is valid
print("\n1. Testing bot authentication...")
headers = {'Authorization': f'Bot {BOT_TOKEN}'}
response = requests.get('https://discord.com/api/v10/users/@me', headers=headers)

if response.status_code == 200:
    bot_info = response.json()
    print(f"✓ Bot authenticated successfully")
    print(f"   Bot name: {bot_info['username']}")
    print(f"   Bot ID: {bot_info['id']}")
elif response.status_code == 401:
    print("✗ Invalid bot token - check your token")
    print("   Make sure you copied the entire token from Discord Developer Portal")
    exit()
else:
    print(f"✗ Unexpected error: {response.status_code}")
    print(f"   Response: {response.text}")
    exit()

# Now test guild access
print("\n2. Testing guild access...")
response = requests.get(
    f'https://discord.com/api/v10/guilds/{GUILD_ID}?with_counts=true',
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"✓ Successfully accessed guild")
    print(f"   Server name: {data['name']}")
    print(f"   Member count: {data['approximate_member_count']}")
elif response.status_code == 403:
    print("✗ Bot doesn't have access to this guild")
    print("   Make sure the bot is added to your server")
elif response.status_code == 404:
    print("✗ Guild not found")
    print("   Check that your GUILD_ID is correct")
else:
    print(f"✗ Error: {response.status_code}")
    print(f"   Response: {response.text}")
