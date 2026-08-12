# Cara Membuat `credentials.json` untuk Google Service Account

Ikuti langkah-langkah berikut untuk membuat file `credentials.json`, yang dapat Anda gunakan untuk mengautentikasi aplikasi Anda dengan Google API.

## 1. Buka Google Cloud Console
- Kunjungi [Google Cloud Console](https://console.cloud.google.com/).

## 2. Buat Proyek Baru atau Pilih Proyek yang Sudah Ada
- **Proyek Baru**: Klik dropdown proyek di bagian atas dan pilih **Proyek Baru**. Beri nama, lalu klik **Buat**.
- **Proyek yang Sudah Ada**: Pilih proyek Anda dari dropdown.

## 3. Aktifkan API yang Dibutuhkan
- Navigasikan ke bagian **APIs & Services** dari menu di sebelah kiri.
- Klik **Library** dan cari API yang Anda butuhkan (misalnya, Google Sheets API, Google Drive API).
- Klik pada API tersebut, lalu klik **Enable**.

## 4. Buat Service Account
- Di bagian **APIs & Services**, klik **Credentials**.
- Klik tombol **Create Credentials** dan pilih **Service account**.
- Berikan nama untuk service account dan deskripsi opsional.
- Klik **Create and Continue**.
- Jika diperlukan, tetapkan peran atau izin; jika tidak, klik **Done**.

## 5. Buat Kunci untuk Service Account
- Di bagian **APIs & Services**, temukan service account yang baru saja Anda buat di bawah **Service Accounts**.
- Klik pada nama service account tersebut.
- Buka tab **Keys**.
- Klik **Add Key** dan pilih **Create new key**.
- Pilih tipe kunci sebagai **JSON** dan klik **Create**.
- Sebuah file `credentials.json` akan diunduh ke komputer Anda.
