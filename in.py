# fetch_instagram_followers.py
# Solo extrae followers_count de los artistas y genera un resumen claro.

import os, json, requests, pathlib, datetime as dt, time

# ==================== CONFIGURACIÓN ====================
ACCESS_TOKEN   = "EAAKuuZBZAgOugBPRZBLNB5fqOaOhKgFXEcux7msZCrsBjfkYeXnj6EhIShff6faTrNu9xEYS4hk3EoikuSI74YJvIyaGRsyEBYEDupLwnHsAJ6LGnTbtdurlbI9sSthCqHthpAV3LKaoSljRhKMTZAuf4xbTlCWrfm5vGTZB3tpl4DEbm1Ttc6TafK8fNmXJtIqgZDZD"

MY_IG_USER_ID  = "17841404800001416"   # tu IG user id numérico
TARGETS = [
    "PYRO_0201",
    "chef_lino99",
    "arandajrr",
    "the.bowlieexperience",
    "mangobladesonics",
    "zacko.____",
]
# ========================================================

API = "https://graph.facebook.com/v21.0"

def fb_get(path, params=None):
    url = f"{API}/{path}"
    p = {"access_token": ACCESS_TOKEN}
    if params: p.update(params)
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()

def business_discovery_query(ig_user_id, username):
    fields = f"business_discovery.username({username}){{username,followers_count}}"
    data = fb_get(f"{ig_user_id}", {"fields": fields})
    return data.get("business_discovery")

def fmt_num(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except Exception:
        return str(n)

def main():
    ig_user_id = MY_IG_USER_ID
    today = dt.date.today().isoformat()
    outdir = pathlib.Path("data") / "instagram" / today
    outdir.mkdir(parents=True, exist_ok=True)

    with_followers, no_followers = [], []

    for uname in TARGETS:
        try:
            bd = business_discovery_query(ig_user_id, uname)
            if not bd or bd.get("followers_count") is None:
                print(f"[warn] {uname}: sin datos (¿personal/privada?).")
                no_followers.append(uname)
                continue
            followers = int(bd["followers_count"])
            with_followers.append((uname, followers))
            print(f"[ok] {uname}: {followers} followers")
            time.sleep(0.6)
        except Exception as e:
            print(f"[error] {uname}: {e}")
            no_followers.append(uname)

    # Ordenar por followers desc
    with_followers.sort(key=lambda x: x[1], reverse=True)

    # Mensaje Divo
    lines = []
    lines.append("No seamos artistas. Resumen IG:")
    if with_followers:
        lines.append("• Estos son los followers:")
        for uname, f in with_followers:
            lines.append(f"  - {uname}: {fmt_num(f)}")
    if no_followers:
        lines.append("• A estos no les encuentro followers:")
        lines.append("  " + ", ".join(no_followers))

    summary_text = "\n".join(lines)
    (outdir / "summary.txt").write_text(summary_text, encoding="utf-8")
    print("\n" + summary_text)
    print(f"\n[done] Resumen guardado en: {outdir/'summary.txt'}")

if __name__ == "__main__":
    main()
