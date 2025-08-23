import os, json, requests, pathlib, datetime as dt, time

# ===== PLACEHOLDERS =====
ACCESS_TOKEN = "EAAKuuZBZAgOugBPUQhNZCvoNSixTsvMUgX8h6X5ZCTZAUqTYAu5xFueSZA2hBJdXN7sw0jdPH4QyDY6wXiKQwbYz6Sw2VsaziZCxZBR9uAcxk0zXaNKhR9MGehuHPRuPX6sYVfZCtvii1h8HW2ZCBUF0fiSzE6iWUZCB4uQKnZCue134Ana93maR61PZCstlgMAszAlSUhgZDZD"
# El IG_USER_ID de TU cuenta Business/Creator (desde tu Page vinculada)
MY_IG_USER_ID = "casa24records"

# Lista de artistas (usernames de Instagram sin @)
TARGETS = [
    "PYRO_0201",
    "chef_lino99",
    "arandajrr",
    "the.bowlieexperience",
    "mangobladesonics",
    "zacko.____",
]

# =========================

def ig_get(url, params=None):
    p = {"access_token": ACCESS_TOKEN}
    if params: p.update(params)
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()

# Carpeta de salida con fecha de hoy
today = dt.date.today().isoformat()
outdir = pathlib.Path("data")/ "instagram" / today
outdir.mkdir(parents=True, exist_ok=True)

for uname in TARGETS:
    try:
        data = ig_get(
            f"https://graph.facebook.com/v21.0/{MY_IG_USER_ID}",
            {
                "fields": f"business_discovery.username({uname})"
                          + "{username,biography,followers_count,"
                          + "follows_count,media_count,profile_picture_url}"
            }
        )
        bd = data.get("business_discovery")
        if not bd:
            print(f"[warn] {uname} no es Business/Creator o no visible")
            continue

        # Guardar JSON
        (outdir/f"{uname}.json").write_text(
            json.dumps(bd, ensure_ascii=False, indent=2)
        )
        print(f"[ok] {uname}: {bd['followers_count']} followers")

        time.sleep(0.5)  # respetar límites
    except Exception as e:
        print(f"[error] {uname}: {e}")
