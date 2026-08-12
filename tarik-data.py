import json
import os
import random
import time
from pathlib import Path

import requests
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CRED_PATH = BASE_DIR / "credentials.json"
if not CRED_PATH.exists():
    raise RuntimeError(f"credentials.json tidak ditemukan di {CRED_PATH}")

ENDPOINTS_CONFIG_PATH = BASE_DIR / "endpoints.json"
if not ENDPOINTS_CONFIG_PATH.exists():
    raise RuntimeError(f"endpoints.json tidak ditemukan di {ENDPOINTS_CONFIG_PATH}")


def env(name, err):
    val = os.getenv(name)
    if not val:
        raise RuntimeError(err)
    return val


TOKEN = env("TOKEN_API_ISB", "TOKEN_API_ISB tidak ditemukan di .env")
SHEETS_ID = env("SPREADSHEET_ID", "SPREADSHEET_ID tidak ditemukan di .env")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


# =========================
# LOAD ENDPOINT CONFIG (dari endpoints.yaml)
# =========================
def load_endpoints_config(path):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f) or {}

    defaults = cfg.get("defaults") or {}
    endpoints = cfg.get("endpoints") or []

    if not endpoints:
        raise RuntimeError(f"Tidak ada endpoint yang terdaftar di {path}")

    required_fields = ("name", "sheet", "url")
    for i, ep in enumerate(endpoints, start=1):
        missing = [f for f in required_fields if not ep.get(f)]
        if missing:
            raise RuntimeError(
                f"Endpoint #{i} di {path} kurang field: {', '.join(missing)}"
            )
        ep["params"] = dict(defaults)

    return endpoints


DEFAULTS_INFO = None  # hanya buat referensi, defaults sudah dipakai di load_endpoints_config
ENDPOINTS = load_endpoints_config(ENDPOINTS_CONFIG_PATH)

# =========================
# HTTP & GOOGLE SHEETS
# =========================
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "inaproc-fetch/1.0",
}


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def ensure_sheets(sh, titles):
    """Cek 1x semua worksheet yg ada, auto-create yg belum ada.
    Dipanggil sekali di awal biar get_sheet() gak perlu try/except lagi."""
    existing = {ws.title for ws in sh.worksheets()}
    missing = [t for t in titles if t not in existing]
    for title in missing:
        sh.add_worksheet(title=title, rows=1000, cols=30)
        print(f"➕ Sheet '{title}' belum ada, dibuat baru")
    if not missing:
        print("✅ Semua sheet sudah ada")


def get_sheet(sh, title):
    ws = sh.worksheet(title)
    ws.clear()
    return ws


# =========================
# FETCH
# =========================
def fetch_page(session, url, params, cursor, max_retries=3, base_delay=1.0):
    p = dict(params)
    if cursor:
        p["cursor"] = cursor

    for attempt in range(1, max_retries + 1):
        try:
            # timeout = (connect, read). Connect pendek supaya cepat gagal & retry.
            r = session.get(url, params=p, timeout=(10, 90))
            print(f"HTTP: {r.status_code} | cursor: {cursor} | attempt: {attempt}")
            if r.status_code >= 400:
                print(f"Response snippet: {r.text[:500]}")
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            print(f"⚠️ request error (attempt {attempt}/{max_retries}): {exc}")
            if attempt == max_retries:
                raise
            time.sleep(base_delay * attempt)


def fetch_all_items(session, ep):
    """Ambil semua halaman via cursor pagination, kumpulkan di memory
    (Sheets API cuma dipanggil sekali di akhir, bukan per-halaman).

    Limit per-request diacak 900-999 dan cursor di-retry sampai 3x (delay 4s)
    karena API kadang balikin response sukses tapi meta.cursor-nya belum ada."""
    all_items = []
    cursor = None
    last_json = None
    params = None

    for attempt in range(1, 3 + 1):
        params = {**ep["params"], "limit": random.randint(900, 999)}
        last_json = fetch_page(session, ep["url"], params, None)
        cursor = (last_json.get("meta") or {}).get("cursor")
        if cursor:
            print(f"✅ [{ep['name']}] cursor found (attempt {attempt}, limit {params['limit']})")
            break
        if attempt < 3:
            print(f"⚠️ [{ep['name']}] no cursor, retrying ({attempt}/3)")
            time.sleep(4)

    items = last_json.get("data") or []
    all_items.extend(items)
    print(f"✅ [{ep['name']}] page 1: {len(items)} rows (total {len(all_items)})")

    if not cursor:
        print(f"⚠️ [{ep['name']}] no cursor after 3 attempts, stopping pagination")
        return all_items

    while True:
        j = fetch_page(session, ep["url"], params, cursor)
        items = j.get("data") or []
        if not items:
            break
        all_items.extend(items)
        print(f"✅ [{ep['name']}] +{len(items)} rows (total {len(all_items)})")
        meta = j.get("meta") or {}
        if meta.get("has_more") and meta.get("cursor"):
            cursor = meta["cursor"]
        else:
            break

    return all_items


def write_all_to_sheet(sh, sheet_title, all_items):
    """Tulis semua data sekaligus (1 API call), lebih cepat daripada append per-halaman."""
    ws = get_sheet(sh, sheet_title)
    if not all_items:
        return 0
    keys = list(all_items[0].keys())
    rows = [keys]
    for it in all_items:
        rows.append([it.get(k, "") for k in keys])
    ws.update(rows, value_input_option="RAW")
    return len(all_items)


# =========================
# MAIN
# =========================
def main():
    start = time.time()
    print(f"🔄 Mulai tarik data | {len(ENDPOINTS)} endpoint | sekuensial")

    creds = Credentials.from_service_account_file(str(CRED_PATH), scopes=SCOPES)
    sh = gspread.authorize(creds).open_by_key(SHEETS_ID)
    ensure_sheets(sh, [ep["sheet"] for ep in ENDPOINTS])
    session = make_session()

    total_rows = 0
    errors = []

    for ep in ENDPOINTS:
        print(f"\n== {ep['name']} -> {ep['sheet']} ==")
        try:
            items = fetch_all_items(session, ep)
            total = write_all_to_sheet(sh, ep["sheet"], items)
            print(f"✅ Done {ep['name']}. Total rows: {total}")
            total_rows += total
        except Exception as e:
            print(f"❌ Error di {ep['name']}: {e}")
            errors.append(ep["name"])

    session.close()
    print(f"\n✅ Selesai dalam {time.time() - start:.1f}s | Total baris: {total_rows}")
    if errors:
        print(f"⚠️ Error di: {', '.join(errors)}")


if __name__ == "__main__":
    main()