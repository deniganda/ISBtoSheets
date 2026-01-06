import os, json, requests
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

# =========================
# INAPROC CONFIG
# =========================
URL = "https://data.inaproc.id/api/v1/rup/paket-swakelola-terumumkan"
PARAMS = {
    "kode_klpd": "D270",
    "tahun": 2025,
    "limit": 70,   # lebih efisien daripada 3
}

TOKEN = os.getenv("TOKEN_API_ISB")
SA_JSON = os.getenv("GOOGLE_SHEET_KEY_JSON")   # PATH ke file json ATAU JSON string
SHEETS_ID = os.getenv("SPREADSHEET_ID")
SHEETS_NAME = "Swakelola"

if not TOKEN:
    raise RuntimeError("TOKEN_API_ISB tidak ditemukan di environment (GitHub Secrets)")
if not SA_JSON:
    raise RuntimeError("GOOGLE_SHEET_KEY_JSON tidak ditemukan di environment (GitHub Secrets)")
if not SHEETS_ID:
    raise RuntimeError("SPREADSHEET_ID tidak ditemukan di environment (GitHub Secrets)")
if not SHEETS_NAME:
    raise RuntimeError("SHEETS_NAME tidak ditemukan di environment (GitHub Secrets)")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
}

# =========================
# GOOGLE SHEETS SETUP
# =========================
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

sa_path = Path(SA_JSON)
if sa_path.exists():
    creds = Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
else:
    # kalau SA_JSON adalah JSON string
    creds = Credentials.from_service_account_info(json.loads(SA_JSON), scopes=SCOPES)

gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEETS_ID)

try:
    ws = sh.worksheet(SHEETS_NAME)
except gspread.WorksheetNotFound:
    ws = sh.add_worksheet(title=SHEETS_NAME, rows=1000, cols=30)

# ✅ HAPUS ISI SHEET DI AWAL
print("🧹 Clearing worksheet...")
ws.clear()

# =========================
# HELPERS
# =========================
def fetch_page(cursor=None):
    p = dict(PARAMS)
    if cursor:
        p["cursor"] = cursor

    r = requests.get(URL, headers=HEADERS, params=p, timeout=60)
    print("HTTP:", r.status_code, "| cursor:", cursor)
    r.raise_for_status()
    return r.json()

def write_header_if_needed(keys):
    # karena kita sudah ws.clear(), header pasti kosong
    ws.append_row(keys, value_input_option="RAW")
    return keys

# =========================
# MAIN LOOP
# =========================
cursor = None
total = 0
header_keys = None

while True:
    j = fetch_page(cursor)

    items = j.get("data") or []
    meta = j.get("meta") or {}

    has_more = meta.get("has_more")
    next_cursor = meta.get("cursor")

    print("Items:", len(items), "| has_more:", has_more, "| next_cursor:", next_cursor)

    if not items:
        break

    # set header dari keys item pertama (sekali saja)
    if header_keys is None:
        header_keys = list(items[0].keys())
        header_keys = write_header_if_needed(header_keys)

    # append batch rows per page (lebih cepat)
    rows = [[it.get(k, "") for k in header_keys] for it in items]
    ws.append_rows(rows, value_input_option="RAW")

    total += len(rows)
    print(f"✅ appended {len(rows)} rows (total {total})")

    # cursor boleh sama (sesuai API kamu)
    if has_more is True and next_cursor:
        cursor = next_cursor
    else:
        break

print(f"\n✅ Done! Total rows appended: {total}")
