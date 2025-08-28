import requests

TOKEN = "MTQxMDc2MDEzODQ0ODcwMzYwMw.GouVyB.-97IIZ3dNtVlCg-TBpE7y23SI56j9ZPio98VXw"          # from Bot tab (not Client Secret)
GUILD_ID = "1000913895415877712"           # you already have this

# 1) Validate token
me = requests.get("https://discord.com/api/v10/users/@me",
                  headers={"Authorization": f"Bot {TOKEN}"}, timeout=10)
print("users/@me:", me.status_code, me.text)  # should be 200

# 2) Get counts
r = requests.get(f"https://discord.com/api/v10/guilds/{GUILD_ID}",
                 headers={"Authorization": f"Bot {TOKEN}"},
                 params={"with_counts": "true"},
                 timeout=10)
print("guilds:", r.status_code, r.text)       # should be 200 with counts
