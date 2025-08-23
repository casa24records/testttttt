# fetch_instagram.py

import os, json, requests, pathlib, datetime as dt, time, csv

# ==================== CONFIGURACIÓN ====================
ACCESS_TOKEN   = "EAAKuuZBZAgOugBPRZBLNB5fqOaOhKgFXEcux7msZCrsBjfkYeXnj6EhIShff6faTrNu9xEYS4hk3EoikuSI74YJvIyaGRsyEBYEDupLwnHsAJ6LGnTbtdurlbI9sSthCqHthpAV3LKaoSljRhKMTZAuf4xbTlCWrfm5vGTZB3tpl4DEbm1Ttc6TafK8fNmXJtIqgZDZD"

MY_IG_USER_ID  = "103136425167758"          # si ya conoces tu ID numérico (1784...), ponlo aquí
MY_PAGE_NAME   = "casa24records"   # nombre EXACTO de tu Page en Facebook
MY_PAGE_ID     = ""          # opcional, si prefieres poner el ID de la Page

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
    if r.status_code >= 400:
        try:
            print("[fb-error]", r.json())
        except Exception:
            print("[fb-error-text]", r.text)
        r.raise_for_status()
    return r.json()

def resolve_page_id():
    if MY_PAGE_ID:
        return MY_PAGE_ID
    pages = fb_get("me/accounts")
    data = pages.get("data", [])
    if not data:
        raise RuntimeError("No se encontraron Pages para este token.")
    if MY_PAGE_NAME:
        for p in data:
            if p.get("name", "").strip().lower() == MY_PAGE_NAME.strip().lower():
                return p["id"]
        print(f"[warn] No se encontró Page llamada '{MY_PAGE_NAME}', uso la primera.")
    return data[0]["id"]

def resolve_ig_user_id():
    page_id = resolve_page_id()
    res = fb_get(f"{page_id}", {"fields": "instagram_business_account"})
    iba = res.get("instagram_business_account")
    if not iba or "id" not in iba:
        raise RuntimeError("La Page no está vinculada a una IG Business/Creator.")
    return iba["id"]

def ensure_ig_user_id():
    if MY_IG_USER_ID:
        if not MY_IG_USER_ID.isdigit():
            raise ValueError("MY_IG_USER_ID debe ser numérico (ej. empieza por 1784...).")
        return MY_IG_USER_ID
    return resolve_ig_user_id()

def business_discovery_query(ig_user_id, username):
    fields = (
        f"business_discovery.username({username})"
        "{username,biography,followers_count,follows_count,media_count,profile_picture_url,ig_id}"
    )
    data = fb_get(f"{ig_user_id}", {"fields": fields})
    return data.get("business_discovery")

def main():
    ig_user_id = ensure_ig_user_id()
    today = dt.date.today().isoformat()
    outdir = pathlib.Path("data") / "instagram" / today
    outdir.mkdir(parents=True, exist_ok=True)

    consolidated_rows = []
    for uname in TARGETS:
        try:
            bd = business_discovery_query(ig_user_id, uname)
            if not bd:
                print(f"[warn] {uname}: sin datos (¿cuenta personal/privada?).")
                continue

            # JSON por artista
            (outdir / f"{uname}.json").write_text(
                json.dumps(bd, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            row = {
                "snapshot_date": today,
                "username": bd.get("username"),
                "ig_id": bd.get("ig_id"),
                "followers_count": bd.get("followers_count"),
                "follows_count": bd.get("follows_count"),
                "media_count": bd.get("media_count"),
                "profile_picture_url": bd.get("profile_picture_url"),
                "biography": (bd.get("biography") or "").replace("\n", " ").strip(),
            }
            consolidated_rows.append(row)
            print(f"[ok] {uname}: {row['followers_count']} followers")
            time.sleep(0.6)
        except requests.HTTPError:
            print(f"[error] {uname}: request inválido (revisa [fb-error] arriba).")
        except Exception as e:
            print(f"[error] {uname}: {e}")

    # CSV consolidado
    if consolidated_rows:
        csv_path = outdir / "instagram_business_discovery.csv"
        fieldnames = [
            "snapshot_date","username","ig_id","followers_count",
            "follows_count","media_count","profile_picture_url","biography"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(consolidated_rows)
        print(f"[done] Consolidado: {csv_path}")
    else:
        print("[done] No hubo filas consolidadas.")

if __name__ == "__main__":
    main()
