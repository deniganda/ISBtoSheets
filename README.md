![ISBtoSheets](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/ISBtoSheets.png)

# ISBtoSheets
Script ini digunakan untuk menarik data dari beberapa endpoint API `data.inaproc.id`, yang kemudian secara otomatis dituliskan ke masing-masing tab pada Google Sheets.

## Persyaratan Penggunaan Script Ini

Sebelum menjalankan script ini, pastikan telah memiliki:

- [Akun Layanan Google (Service Account)](https://github.com/deniganda/ISBtoSheets/blob/main/guide/Google%20Service%20Account.md) dengan Google Sheets API diaktifkan (file `credentials.json`).
- [Google Sheets](https://github.com/deniganda/ISBtoSheets/blob/main/guide/Google%20Sheets.md) tujuan (diperlukan Spreadsheet ID untuk memasukkan data).
- [INAPROC API](https://data.inaproc.id/portal/tokens) dari akun ISB LKPP instansi Anda.

## Kenapa Menggunakan Script Ini?

Penggunaan script ini sangat disarankan karena dapat **dijalankan setiap hari secara rutin**, dengan hasil yang tersimpan pada Google Sheets. Setiap kali dijalankan, data akan diperbarui pada sheet tersebut. Apabila sewaktu-waktu diperlukan data pada tanggal-tanggal sebelumnya, dapat memanfaatkan fitur bawaan Google Sheets **Version History** (File → Version history → See version history) untuk melihat kondisi data secara historis, tidak hanya data terbaru saja.

> 💡 Perlu diperhatikan bahwa script ini akan **menimpa (replace)** data lama setiap kali dijalankan (lihat FAQ "Mengapa data tertimpa/hilang setiap kali dijalankan ulang?"). Oleh karena itu, riwayat data harian tetap dapat ditelusuri kembali melalui fitur Version History tersebut.

## Struktur File

```
├── tarik-data.py         ← script utama
├── endpoints.json         ← daftar endpoint & nama sheet (dapat diedit)
├── requirements.txt       ← daftar library
├── .env.example            ← template .env (aman untuk dibagikan)
├── credentials.json       ← dibuat sendiri (Step 2)
└── .env                   ← dibuat sendiri (Step 4)
```

---

## Panduan Instalasi

### Step 1 — Instalasi Dependency

```
pip install -r requirements.txt
```

### Step 2 — Membuat `credentials.json` (Service Account Google)

File ini merupakan kredensial agar script dapat melakukan autentikasi ke Google Sheets API tanpa perlu login manual.

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project baru (atau gunakan project yang sudah ada)
3. Pada kolom pencarian, cari **Google Sheets API** → klik **Enable**
4. Buka menu **IAM & Admin → Service Accounts** → **Create Service Account**
5. Isi nama sesuai kebutuhan → lanjutkan hingga selesai (tidak perlu menambahkan role khusus)
6. Buka service account yang baru dibuat → tab **Keys** → **Add Key → Create new key** → pilih **JSON**
7. File JSON akan otomatis terunduh → ganti nama menjadi `credentials.json` → simpan pada folder yang sama dengan `tarik-data.py`

### Step 3 — Membagikan Akses Google Sheets ke Service Account

1. Buka `credentials.json`, cari field `client_email` (formatnya `xxx@xxx.iam.gserviceaccount.com`)
2. Buka Google Sheets tujuan → klik **Share** → masukkan email tersebut → berikan akses **Editor** → Send

Tanpa langkah ini, script akan menghasilkan error `PermissionError` meskipun `credentials.json` sudah valid.

### Step 4 — Membuat File `.env`

Salin `.env.example` menjadi `.env` (atau buat file baru bernama `.env`) pada folder yang sama dengan `tarik-data.py`, kemudian isi:

```
TOKEN_API_ISB=isi_token_di_sini
SPREADSHEET_ID=isi_id_spreadsheet_di_sini
```

**Cara memperoleh `SPREADSHEET_ID`** — dapat diambil dari URL Google Sheets:

```
https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/edit
                                        └────── ini ID-nya ──────┘
```

**Cara memperoleh `TOKEN_API_ISB`** — login menggunakan akun yang memiliki role **"Data Integrator"**, kemudian buka [https://data.inaproc.id/portal/tokens](https://data.inaproc.id/portal/tokens). Pastikan juga akses API telah diajukan untuk endpoint-endpoint yang akan digunakan pada `endpoints.json`.

⚠️ File `.env` dan `credentials.json` bersifat rahasia — **jangan pernah dibagikan atau diunggah ke pihak lain**.

### Step 5 — Menyesuaikan `endpoints.json`

Buka `endpoints.json`, bagian `defaults` **wajib disesuaikan** — ini merupakan parameter yang otomatis dikirim ke **seluruh** endpoint:

```json
"defaults": {
  "kode_klpd": "D270",
  "tahun": 2026
}
```

`kode_klpd` **wajib diisi sesuai KLPD masing-masing** (setiap endpoint API INAPROC terikat pada KLPD tertentu, sehingga tidak dapat dikosongkan atau dibiarkan menggunakan nilai contoh di atas). Sesuaikan juga `tahun` apabila tahun anggarannya berbeda. Cukup diubah pada satu tempat ini, tidak perlu diubah satu per satu pada tiap endpoint.

Selain `defaults`, periksa juga daftar pada `"endpoints"` — format tiap entry:

```json
{
  "name": "Nama bebas untuk keperluan log",
  "sheet": "Nama Tab Sheet",
  "url": "https://data.inaproc.id/api/v1/..."
}
```

Tambah/hapus/ubah entry sesuai endpoint yang datanya ingin ditarik. Apabila nama sheet belum tersedia pada spreadsheet, script akan secara otomatis membuat tab baru — sehingga cukup tuliskan nama tab yang diinginkan pada field `sheet`.

### Step 6 — Menjalankan Script

```
python tarik-data.py
```

---

## FAQ

<details>
<summary>Mengapa data tertimpa/hilang setiap kali dijalankan ulang?</summary>

Hal ini disengaja — fungsi `get_sheet()` memanggil `ws.clear()` sebelum menuliskan data baru, agar sheet selalu berisi data terkini tanpa duplikasi dari proses sebelumnya. Apabila diperlukan penyimpanan riwayat data, lakukan pencadangan (backup) secara manual sebelum menjalankan ulang script.

</details>

<details>
<summary>Mengapa terdapat mekanisme retry & delay 4 detik pada <code>fetch_all_items</code>?</summary>

Terkadang API `data.inaproc.id` mengembalikan response sukses (200) namun field `meta.cursor` belum terisi. Script akan mencoba ulang hingga 3 kali dengan jeda 4 detik agar proses tidak langsung gagal pada percobaan pertama.

</details>

<details>
<summary>Error: <code>PermissionError</code> pada <code>open_by_key</code></summary>

```
File ".../tarik-data.py", line 193, in main
    sh = gspread.authorize(creds).open_by_key(SHEETS_ID)
File ".../gspread/client.py", line 173, in open_by_key
    raise PermissionError from ex
PermissionError
```

Service account **berhasil melakukan autentikasi**, namun **tidak memiliki akses** ke spreadsheet yang dituju. Periksa satu per satu:

1. **Spreadsheet belum dibagikan ke service account.** Penyebab paling umum. Ambil `client_email` dari `credentials.json`, kemudian bagikan spreadsheet ke email tersebut dengan akses Editor.
2. **`SPREADSHEET_ID` pada `.env` keliru/tertukar.** Periksa kembali pada URL spreadsheet, pastikan tidak ada karakter yang terpotong.
3. **Google Sheets API belum diaktifkan** pada project Google Cloud yang sesuai dengan `credentials.json`.
4. **`credentials.json` berasal dari project/service account yang berbeda** dari yang dibagikan ke spreadsheet.

</details>

<details>
<summary>Dijalankan pada Linux muncul error saat <code>pip install</code>, apakah perlu menggunakan venv?</summary>

Benar, pada sebagian besar distro Linux (Ubuntu/Debian versi terbaru, dan lainnya), `pip install` langsung ke sistem sering kali ditolak dengan error sebagai berikut:

```
error: externally-managed-environment
```

Ini merupakan proteksi bawaan agar package Python bawaan sistem tidak mengalami konflik/kerusakan. Solusinya adalah menggunakan **virtual environment (venv)** — berbeda dengan Windows yang umumnya dapat langsung menjalankan `pip install` tanpa kendala.

Cara penggunaan venv pada Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tarik-data.py
```

- `python3 -m venv .venv` → membuat folder venv baru (`.venv`)
- `source .venv/bin/activate` → mengaktifkan venv (perlu dilakukan setiap membuka terminal baru, sebelum menjalankan script)
- Setelah aktif, prompt terminal umumnya berubah dengan tambahan `(.venv)` di depannya

Untuk keluar dari venv, gunakan perintah: `deactivate`.

Tambahkan pula `.venv/` ke dalam `.gitignore` agar tidak turut ter-commit.

</details>

<details>
<summary>File apa saja yang aman untuk dibagikan/di-commit ke Git?</summary>

| File | Aman Dibagikan? |
|---|---|
| `tarik-data.py` | ✅ Aman |
| `endpoints.json` | ✅ Aman |
| `requirements.txt` | ✅ Aman |
| `README.md` | ✅ Aman |
| `.env.example` | ✅ Aman (kosong, hanya template) |
| `.env` | ❌ **Tidak**, berisi token & ID |
| `credentials.json` | ❌ **Tidak**, berisi kunci akses Google |
| `.venv/` | ❌ **Tidak**, folder virtual environment, bukan bagian dari source code |

Tambahkan `.env`, `credentials.json`, dan `.venv/` ke dalam `.gitignore`.

</details>