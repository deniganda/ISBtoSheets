# Cara Mendapatkan Spreadsheet ID
Saat bekerja dengan Google Sheets, Anda sering memerlukan Spreadsheet ID untuk berinteraksi dengan API. Spreadsheet ID adalah pengenal unik yang terdapat dalam URL Google Sheet.

## Panduan Langkah demi Langkah

1. **Buka Google Sheet Anda**:
   - Buka [Google Sheets](https://docs.google.com/spreadsheets/) dan buka spreadsheet yang ingin Anda gunakan.

2. **Temukan Spreadsheet ID**:
   - Lihat URL di bilah alamat browser Anda.
   - URL-nya akan terlihat seperti ini:
     ```
     https://docs.google.com/spreadsheets/d/1SeTFM_Asd167ejmTpWM_Np19zbK0mI2rPBJfwN3L1wa4/edit?usp=sharing
     ```

3. **Identifikasi Spreadsheet ID**:
   - Bagian **yang dicetak tebal** dari URL antara `/d/` dan `/edit` adalah Spreadsheet ID Anda.
   - Dalam contoh ini, Spreadsheet ID-nya adalah:
     ```
     1SeTFM_Asd167ejmTpWM_Np19zbK0mI2rPBJfwN3L1wa4
     ```

---

# Cara Menambahkan Google Service Account sebagai Editor di Google Sheets

Untuk memungkinkan Google Service Account Anda berinteraksi dengan Google Sheets, Anda perlu menambahkannya sebagai Editor. Berikut cara melakukannya:

## Panduan Langkah demi Langkah

1. **Buat atau Dapatkan Email Service Account**:
   - Jika Anda belum membuat service account, ikuti langkah-langkah [di sini](https://github.com/deniganda/ISBtoSheets/blob/main/Guide/Google%20Service%20Account.md).
   - Email service account biasanya terlihat seperti `your-service-account@your-project-id.iam.gserviceaccount.com`.

2. **Buka Google Sheets**:
   - Buka [Google Sheets](https://docs.google.com/spreadsheets/) dan buka spreadsheet yang ingin Anda bagikan.

3. **Buka Pengaturan Berbagi**:
   - Di sudut kanan atas spreadsheet, klik tombol **Share**.

4. **Tambahkan Service Account sebagai Editor**:
   - Di bidang "Share with people and groups", masukkan email service account yang Anda dapatkan sebelumnya.
   - Klik dropdown di sebelah alamat email dan pilih **Editor**.

5. **Simpan Perubahan**:
   - Klik **Send** atau **Share** untuk memberikan akses editor kepada service account di spreadsheet tersebut.
