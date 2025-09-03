# Spotify Playlist to MP3 Converter

Script Python untuk **mengunduh lagu dari playlist Spotify** dengan cara:

1. Mengambil metadata lengkap dari Spotify (judul, artis, album, tahun, genre, cover art).
2. Mencari lagu di YouTube secara otomatis.
3. Mengunduh audio dari YouTube dan mengonversinya menjadi **MP3 192 kbps 44.1 kHz**.
4. Menulis metadata + cover art ke file MP3.

---

## Fitur

- Ambil semua lagu dari playlist Spotify.
- Cari lagu di YouTube otomatis berdasarkan **judul + artis**.
- Pilih hasil YouTube dengan durasi paling mirip dengan versi Spotify (lebih akurat).
- Download audio dan konversi ke **MP3 192 kbps 44.1 kHz** menggunakan `ffmpeg`.
- Tulis metadata ID3 (Title, Artist, Album, Year, Track Number, Genre, Cover Art).
- Simpan file MP3 ke folder `downloads/`.

---

## Persiapan

### 1. Install Python

Pastikan sudah ada **Python 3.8+** di komputer.  
Cek dengan:

```bash
python --version
```

### 2. Install dependensi

Jalankan:

```bash
pip install spotipy yt-dlp mutagen requests
```

### 3. Install FFmpeg

Unduh FFmpeg dari:  
https://ffmpeg.org/download.html

Lalu:

- Extract ke folder, misalnya `C:\ffmpeg\bin\`.
- Tambahkan path `C:\ffmpeg\bin\` ke **Environment Variables** → `PATH`.
- Cek instalasi:
  ```bash
  ffmpeg -version
  ```

---

## Spotify API Credentials

Script ini butuh **Spotify Client ID & Secret**.

1. Buka [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Login dengan akun Spotify.
3. Klik **Create App** → isi bebas.
4. Copy **Client ID** dan **Client Secret**.
5. Masukkan ke dalam script di bagian:
   ```python
   SPOTIPY_CLIENT_ID = "CLIENT_ID_ANDA"
   SPOTIPY_CLIENT_SECRET = "CLIENT_SECRET_ANDA"
   ```

---

## Cara Menjalankan

1. Simpan script `spotify_converter.py`.
2. Jalankan di terminal:
   ```bash
   python spotify_converter.py
   ```
3. Masukkan URL playlist Spotify, contoh:
   ```
   https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
   ```
4. Script akan:
   - Mengambil semua lagu dari playlist
   - Mencari di YouTube
   - Mengunduh dan konversi ke MP3
   - Menulis metadata + cover art
   - Menyimpan ke folder `downloads/`

---

## Contoh Output

Setelah script dijalankan, hasil ada di folder `downloads/`:

```
downloads/
├── Coldplay - Yellow.mp3
├── Taylor Swift - Love Story.mp3
└── The Weeknd - Blinding Lights.mp3
```

---

## Catatan Penting

- Script ini **untuk penggunaan pribadi/educational**. Jangan gunakan untuk distribusi ilegal.
- Kualitas audio mengikuti sumber di YouTube, meski di-convert ke 192 kbps.
- Tidak semua lagu Spotify tersedia di YouTube dengan versi identik (mungkin beda versi/cover).

---

## Troubleshooting

- **Error `ffmpeg not found`** → pastikan FFmpeg sudah diinstall dan ada di PATH.
- **Lagu tidak ditemukan di YouTube** → bisa coba ubah query di script agar lebih spesifik.
- **Metadata kosong** → beberapa lagu/album di Spotify tidak punya info lengkap (contoh: tahun rilis kosong).
- **Download berhenti** → pastikan koneksi internet stabil.

---

## Lisensi

Proyek ini hanya untuk **belajar dan penggunaan pribadi**.  
Gunakan secara bijak, patuhi hukum & ketentuan layanan Spotify dan YouTube.
