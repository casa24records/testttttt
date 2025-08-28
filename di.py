import requests

BOT_TOKEN = "MTQxMDc2MDEzODQ0ODcwMzYwMw.G41dDh.GLcUfa3d75kry8CXsrKdw3Wqdtr08R80ob_e2g"
GUILD_ID = "1000913895415877712"

response = requests.get(
    f'https://discord.com/api/v10/guilds/{GUILD_ID}?with_counts=true',
    headers={'Authorization': f'Bot {BOT_TOKEN}'}
)

if response.status_code == 200:
    member_count = response.json()['approximate_member_count']
    print(member_count)
else:
    print(f"Error: {response.status_code}")
