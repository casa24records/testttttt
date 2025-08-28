import requests

# Paste your FULL new token here (it should be ~70+ characters)
BOT_TOKEN = "MTQxMDc2MDEzODQ0ODcwMzYwMw.GouVyB.-97IIZ3dNtVlCg-TBpE7y23SI56j9ZPio98VXw"
GUILD_ID = "1000913895415877712"

# Test the connection
headers = {'Authorization': f'Bot {BOT_TOKEN}'}
response = requests.get(
    f'https://discord.com/api/v10/guilds/{GUILD_ID}?with_counts=true',
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Server: {data['name']}")
    print(f"Members: {data['approximate_member_count']}")
else:
    print(f"Error: {response.status_code}")
