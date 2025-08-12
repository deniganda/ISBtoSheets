![ISBtoSheets](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/ISBtoSheets.png)

# ISBtoSheets
ISBtoSheets adalah alat otomatisasi berbasis GitHub Actions yang mengambil data JSON dari Indonesian Spending Benchmark (ISB) LKPP dan langsung mengimpornya ke Google Sheets.
Proyek ini dirancang untuk:
```
   - Menghemat waktu dalam pengambilan data harian.

   - Menyimpan dan mengelola riwayat data secara rapi di Google Sheets.

   - Memudahkan analisis dan pelaporan tanpa perlu memperbarui data mentah secara manual, sehingga rumus, olahan, dan rekap di Google Sheets selalu terbarui setiap hari.
```
Fitur utama:
```
   - Terintegrasi dengan berbagai endpoint ISB LKPP (Tender, Non Tender, E-Purchasing, Toko Daring, dsb).

   - Penjadwalan otomatis setiap hari pukul 06.00 WIB melalui GitHub Actions.

   - Konfigurasi fleksibel lewat Google Sheets API dan GitHub Secrets.
```
Dengan ISBtoSheets, proses sinkronisasi data LKPP menjadi cepat, konsisten, dan siap diolah kapan saja.

## Persyaratan
- [Akun Layanan Google](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/Google%20Service%20Account.md) dengan Google Sheets API diaktifkan (file `credentials.json`).
- [Google Sheets](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/Google%20Sheets.md) (Anda memerlukan Spreadsheet ID untuk memasukkan data).
- Link JSON dari akun [ISB LKPP](https://isb.lkpp.go.id/isb-2) instansi anda.

## Persiapan

### 1. Fork Repositori GitHub

- Fork repositori ini ke akun GitHub Anda.

### 2. Persiapkan Google Sheets

a. **Buat Sheet dengan Nama Berikut:**
``` 
        - Penyedia
        - Swakelola
        - Tender
        - TenderNilai
        - TenderPengumuman
        - NonTender
        - Pen NonTender
        - Pen Swakelola
        - E-Purchasing5
        - E-Purchasing6
        - TokoDaring
```
b. **Tambahkan Google Service Account sebagai Editor:**
- Ikuti [panduan ini](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/Google%20Sheets.md#how-to-add-the-google-service-account-as-an-editor-in-google-sheets) untuk memberikan akses editor kepada Google Service Account Anda di Google Sheets.

### 3. Buat GitHub Secrets

Untuk menyimpan dan menggunakan informasi sensitif dengan aman, atur GitHub Secrets:

- **Navigasi ke:** `Settings > Secrets and variables > Actions > New repository secret`

#### **Secrets yang Diperlukan:**
- `GOOGLE_SHEET_KEY_JSON`: Salin dan tempelkan isi file `credentials.json` Anda di sini.
- `SPREADSHEET_ID`: ID Spreadsheet dari tautan Google Sheets.
- `API_URL_TS`: Tautan JSON dari SPSE-TenderSelesai.
- `API_URL_TSN`: Tautan JSON dari SPSE-TenderSelesaiNilai.
- `API_URL_TSP`: Tautan JSON dari SPSE-TenderPengumuman.
- `API_URL_TD`: Tautan JSON dari Bela-TokoDaringRealisasi.
- `API_URL_SWA`: Tautan JSON dari RUP-PaketSwakelola-Terumumkan.
- `API_URL_PEN`: Tautan JSON dari RUP-PaketPenyedia-Terumumkan.
- `API_URL_PS`: Tautan JSON dari SPSE-PencatatanSwakelola.
- `API_URL_PNT`: Tautan JSON dari SPSE-PencatatanNonTender.
- `API_URL_NTS`: Tautan JSON dari SPSE-NonTenderSelesai.
- `API_URL_EP5`: Tautan JSON dari Ecat-PaketEPurchasing.
- `API_URL_EP6`: Tautan JSON dari Ecat-PaketEPurchasingV6.

### 4. Aktifkan GitHub Actions

a. **Atur Workflow:**
- Buka tab **Actions**.
- Klik `'I understand my workflows, go ahead and enable them'`.
- Pilih `'Daily Node.js Script'` workflow.
- Klik `'Enable workflow'`.

b. **Jalankan Workflow:**
- Anda dapat memicu workflow secara manual dengan mengklik `'Run Workflow'`.
- Workflow juga akan berjalan otomatis setiap pagi pada pukul 6 AM.

---

Sekarang Anda sudah siap! Pengaturan Anda akan secara otomatis mengimpor data JSON ISB LKPP ke Google Sheets yang ditentukan setiap hari. Anda juga dapat menjalankan skrip secara manual kapan saja diperlukan.
