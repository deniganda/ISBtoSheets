import os
import json
import random
import time
from pathlib import Path

import requests
import gspread
from google.oauth2.service_account import Credentials

# =========================
# LOAD ENV (supports .env locally + GitHub Actions env)
# =========================
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    try:
        from dotenv import load_dotenv
    except ImportError:
        raise RuntimeError("python-dotenv is required to load .env locally")
    load_dotenv(env_path)

TOKEN = os.getenv("TOKEN_API_ISB")
SA_JSON = os.getenv("GOOGLE_SHEET_KEY_JSON")   # PATH ke file json ATAU JSON string
SHEETS_ID = os.getenv("SPREADSHEET_ID")

if not TOKEN:
    raise RuntimeError("TOKEN_API_ISB tidak ditemukan di environment atau .env")
if not SA_JSON:
    raise RuntimeError("GOOGLE_SHEET_KEY_JSON tidak ditemukan di environment atau .env")
if not SHEETS_ID:
    raise RuntimeError("SPREADSHEET_ID tidak ditemukan di environment atau .env")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
    "User-Agent": "inaproc-fetch/1.0",
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

# =========================
# ENDPOINT CONFIG (placeholder params/sheet names)
# =========================
LIMIT_MIN = 50
LIMIT_MAX = 100
CURSOR_RETRY_ATTEMPTS = 5
CURSOR_RETRY_DELAY_SEC = 4

DEFAULTS = {
    "kode_klpd": "D270",
    "tahun": 2026,
    "limit": 70,
    "kodePenyedia": "KODE_PENYEDIA",
    "kodeTender": "KODE_TENDER",
}

ENDPOINTS = [
    {
        "name": "Endpoint 01 - ekatalog paket e-purchasing",
        "sheet": "E-Purchasing6",
        "url": "https://data.inaproc.id/api/v1/ekatalog/paket-e-purchasing",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    # {
    #     "name": "Endpoint 02 - ekatalog penyedia detail",
    #     "sheet": "SHEET_ENDPOINT_02",
    #     "url": "https://data.inaproc.id/api/v1/ekatalog/penyedia-detail",
    #     "params": {"kodePenyedia": DEFAULTS["kodePenyedia"]},
    #     "use_cursor": False,
    # },
    # {
    #     "name": "Endpoint 03 - rup master satker",
    #     "sheet": "SHEET_ENDPOINT_03",
    #     "url": "https://data.inaproc.id/api/v1/rup/master-satker",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 04 - rup paket anggaran penyedia",
    #     "sheet": "SHEET_ENDPOINT_04",
    #     "url": "https://data.inaproc.id/api/v1/rup/paket-anggaran-penyedia",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 05 - rup paket anggaran swakelola",
    #     "sheet": "SHEET_ENDPOINT_05",
    #     "url": "https://data.inaproc.id/api/v1/rup/paket-anggaran-swakelola",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    {
        "name": "Endpoint 06 - rup paket penyedia terumumkan",
        "sheet": "Penyedia",
        "url": "https://data.inaproc.id/api/v1/rup/paket-penyedia-terumumkan",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    {
        "name": "Endpoint 07 - rup paket swakelola terumumkan",
        "sheet": "Swakelola",
        "url": "https://data.inaproc.id/api/v1/rup/paket-swakelola-terumumkan",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    # {
    #     "name": "Endpoint 08 - rup program master",
    #     "sheet": "SHEET_ENDPOINT_08",
    #     "url": "https://data.inaproc.id/api/v1/rup/program-master",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 09 - tender jadwal tahapan non tender",
    #     "sheet": "SHEET_ENDPOINT_09",
    #     "url": "https://data.inaproc.id/api/v1/tender/jadwal-tahapan-non-tender",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 10 - tender jadwal tahapan tender",
    #     "sheet": "SHEET_ENDPOINT_10",
    #     "url": "https://data.inaproc.id/api/v1/tender/jadwal-tahapan-tender",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 11 - tender non tender ekontrak kontrak",
    #     "sheet": "SHEET_ENDPOINT_11",
    #     "url": "https://data.inaproc.id/api/v1/tender/non-tender-ekontrak-kontrak",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 12 - tender non tender pengumuman",
    #     "sheet": "SHEET_ENDPOINT_12",
    #     "url": "https://data.inaproc.id/api/v1/tender/non-tender-pengumuman",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    {
        "name": "Endpoint 13 - tender non tender selesai",
        "sheet": "NonTender",
        "url": "https://data.inaproc.id/api/v1/tender/non-tender-selesai",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    {
        "name": "Endpoint 14 - tender pencatatan non tender",
        "sheet": "Pen NonTender",
        "url": "https://data.inaproc.id/api/v1/tender/pencatatan-non-tender",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    # {
    #     "name": "Endpoint 15 - tender pencatatan non tender realisasi",
    #     "sheet": "SHEET_ENDPOINT_15",
    #     "url": "https://data.inaproc.id/api/v1/tender/pencatatan-non-tender-realisasi",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    {
        "name": "Endpoint 16 - tender pencatatan swakelola",
        "sheet": "Pen Swakelola",
        "url": "https://data.inaproc.id/api/v1/tender/pencatatan-swakelola",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    # {
    #     "name": "Endpoint 17 - tender pencatatan swakelola realisasi",
    #     "sheet": "SHEET_ENDPOINT_17",
    #     "url": "https://data.inaproc.id/api/v1/tender/pencatatan-swakelola-realisasi",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 18 - tender pengumuman",
    #     "sheet": "TenderPengumuman",
    #     "url": "https://data.inaproc.id/api/v1/tender/pengumuman",
    #     "params": {
    #         "kodeTender": DEFAULTS["kodeTender"],
    #         "kode_klpd": DEFAULTS["kode_klpd"],
    #         "tahun": DEFAULTS["tahun"],
    #         "limit": DEFAULTS["limit"],
    #     },
    #     "use_cursor": True,
    # },
    # {
    #     "name": "Endpoint 19 - tender peserta tender",
    #     "sheet": "SHEET_ENDPOINT_19",
    #     "url": "https://data.inaproc.id/api/v1/tender/peserta-tender",
    #     "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
    #     "use_cursor": True,
    # },
    {
        "name": "Endpoint 20 - tender ekontrak kontrak",
        "sheet": "Tender",
        "url": "https://data.inaproc.id/api/v1/tender/tender-ekontrak-kontrak",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
    {
        "name": "Endpoint 21 - tender selesai nilai",
        "sheet": "TenderNilai",
        "url": "https://data.inaproc.id/api/v1/tender/tender-selesai-nilai",
        "params": {"kode_klpd": DEFAULTS["kode_klpd"], "tahun": DEFAULTS["tahun"], "limit": DEFAULTS["limit"]},
        "use_cursor": True,
    },
]

# =========================
# HELPERS
# =========================
def fetch_page(url, params, cursor, max_retries=3, base_delay=1.0):
    p = dict(params)
    if cursor:
        p["cursor"] = cursor
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, params=p, timeout=60)
            print("HTTP:", r.status_code, "| cursor:", cursor, "| attempt:", attempt)
            print("URL:", r.url)
            if r.status_code >= 400:
                print("Response snippet:", r.text[:1000])
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            last_err = exc
            if attempt == max_retries:
                break
            time.sleep(base_delay * attempt)
    raise last_err

def append_items(ws, header_keys, items):
    if not items:
        return header_keys, 0
    if header_keys is None:
        header_keys = list(items[0].keys())
        ws.append_row(header_keys, value_input_option="RAW")
    rows = [[it.get(k, "") for k in header_keys] for it in items]
    if rows:
        ws.append_rows(rows, value_input_option="RAW")
    return header_keys, len(rows)

def get_sheet(title):
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=1000, cols=30)
    ws.clear()
    return ws

# =========================
# MAIN LOOP
# =========================
for ep in ENDPOINTS:
    print(f"\n== {ep['name']} -> {ep['sheet']} ==")
    ws = get_sheet(ep["sheet"])

    total = 0
    header_keys = None

    if not ep["use_cursor"]:
        j = fetch_page(ep["url"], ep["params"], None)
        items = j.get("data") or []
        if not isinstance(items, list):
            items = []
        header_keys, added = append_items(ws, header_keys, items)
        total += added
        print(f"✅ appended {added} rows (total {total})")
        print(f"✅ Done {ep['name']}. Total rows: {total}")
        continue

    cursor = None
    last_json = None
    limit_used = None
    params_for_cursor = None

    for attempt in range(1, CURSOR_RETRY_ATTEMPTS + 1):
        limit_used = random.randint(LIMIT_MIN, LIMIT_MAX)
        params_for_cursor = dict(ep["params"])
        params_for_cursor["limit"] = limit_used
        last_json = fetch_page(ep["url"], params_for_cursor, None)
        meta = last_json.get("meta") or {}
        cursor = meta.get("cursor")
        if cursor:
            print(f"✅ cursor found (attempt {attempt}, limit {limit_used})")
            break
        if attempt < CURSOR_RETRY_ATTEMPTS:
            print(f"⚠️ no cursor, retrying (attempt {attempt}/{CURSOR_RETRY_ATTEMPTS})")
            time.sleep(CURSOR_RETRY_DELAY_SEC)

    items = (last_json.get("data") if last_json else []) or []
    if not isinstance(items, list):
        items = []
    header_keys, added = append_items(ws, header_keys, items)
    total += added
    print(f"✅ appended {added} rows (total {total})")

    if not cursor:
        print(f"⚠️ no cursor after {CURSOR_RETRY_ATTEMPTS} attempts, stopping pagination")
        print(f"✅ Done {ep['name']}. Total rows: {total}")
        continue

    while True:
        j = fetch_page(ep["url"], params_for_cursor, cursor)
        items = j.get("data") or []
        if not isinstance(items, list):
            items = []
        if not items:
            break

        header_keys, added = append_items(ws, header_keys, items)
        total += added
        print(f"✅ appended {added} rows (total {total})")

        meta = j.get("meta") or {}
        has_more = meta.get("has_more")
        next_cursor = meta.get("cursor")
        if has_more is True and next_cursor:
            cursor = next_cursor
        else:
            break

    print(f"✅ Done {ep['name']}. Total rows: {total}")
