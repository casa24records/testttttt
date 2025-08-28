import requests

# Full token from Bot tab (NOT client secret!)
BOT_TOKEN = "PASTE_YOUR_TOKEN_HERE".strip()
GUILD_ID = "MTQxMDc2MDEzODQ0ODcwMzYwMw.GouVyB.-97IIZ3dNtVlCg-TBpE7y23SI56j9ZPio98VXw"  # your guild ID

headers = {"Authorization": f"Bot {BOT_TOKEN}"}

# 1) Test token works
test = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
print("users/@me:", test.status_code, test.text)

# 2) Now get member counts
response = requests.get(
    f"https://discord.com/api/v10/guilds/{GUILD_ID}?with_counts=true",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    print(f"Server: {data['name']}")
    print(f"Members: {data['approximate_member_count']}")
else:
    print(f"Error: {response.status_code}, {response.text}")
