# 🎵 Spotify Playlist Downloader

Script Python untuk mendownload semua lagu dari playlist Spotify dengan metadata lengkap (judul, artist, album, cover art, lyrics).

## ✨ Fitur

- ✅ Download semua lagu dari playlist Spotify
- ✅ Metadata lengkap otomatis terisi (judul, artist, album, cover art)
- ✅ Download lyrics (jika tersedia)
- ✅ Skip lagu yang sudah didownload (resume capability)
- ✅ Konfigurasi fleksibel (format, quality, output folder)
- ✅ Interface yang cantik dengan Rich library
- ✅ Support playlist, album, single track, dan artist

## 📋 Prerequisites

- Python 3.8 atau lebih baru (tested pada Python 3.14)
- pip (Python package manager)
- Koneksi internet

## 🚀 Instalasi

1. **Install dependencies:**
   ```bash
   pip install spotdl rich
   ```

   Atau menggunakan requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Konfigurasi

Edit file `config.json` untuk mengatur preferensi download:

```json
{
  "output_folder": "downloads",
  "audio_format": "mp3",
  "bitrate": "256k",
  "filename_template": "{artist} - {title}",
  "download_lyrics": true,
  "skip_existing": true
}
```

### Penjelasan Setting:

- **output_folder**: Folder tempat lagu akan disimpan
- **audio_format**: Format audio output
  - `mp3` - Paling kompatibel (recommended)
  - `m4a` - Kualitas bagus, file lebih kecil
  - `flac` - Lossless (file besar)
- **bitrate**: Kualitas audio
  - `128k` - Standard
  - `192k` - Good
  - `256k` - High (recommended)
  - `320k` - Very High
- **filename_template**: Template penamaan file
  - Contoh: `{artist} - {title}`, `{title}`, `{track-number} - {title}`
- **download_lyrics**: Download dan embed lyrics ke file
- **skip_existing**: Skip file yang sudah pernah didownload

## 📖 Cara Penggunaan

### 1. Jalankan Script

```bash
python spotify_downloader.py
```

### 2. Masukkan URL Spotify

Script akan menampilkan interface seperti ini:

```
╔═══════════════════════════════════════════════╗
║     🎵  SPOTIFY PLAYLIST DOWNLOADER  🎵       ║
╚═══════════════════════════════════════════════╝

⚙️  Konfigurasi Aktif
┌────────────────┬──────────┐
│ Setting        │ Value    │
├────────────────┼──────────┤
│ Output Folder  │ downloads│
│ Audio Format   │ MP3      │
│ Bitrate        │ 256k     │
└────────────────┴──────────┘

📋 Masukkan URL Spotify Playlist:
🔗 URL: [paste URL di sini]
```

### 3. Mendapatkan URL Spotify

1. Buka Spotify (web atau aplikasi)
2. Buka playlist/album/track yang ingin didownload
3. Klik tombol "Share" → "Copy Link"
4. Paste ke script

**Contoh URL yang didukung:**
- Playlist: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- Album: `https://open.spotify.com/album/6DEjYFkNZh67HP7R9PSZvv`
- Single: `https://open.spotify.com/track/3n3Ppam7vgaVa1iaRUc9Lp`
- Artist: `https://open.spotify.com/artist/6eUKZXaKkcviH0Ku9w2n3V`

## 📁 Output

Lagu akan tersimpan di folder `downloads/` (atau sesuai config) dengan:
- ✅ Metadata lengkap (Title, Artist, Album, Year)
- ✅ Cover art ter-embed
- ✅ Lyrics (jika tersedia)

Contoh:
```
downloads/
├── Ed Sheeran - Shape of You.mp3
├── The Weeknd - Blinding Lights.mp3
└── ...
```

## ❓ FAQ

### Q: Apakah butuh Spotify Premium?
A: Tidak, script ini tidak memerlukan akun Spotify.

### Q: Dari mana audio didownload?
A: spotdl mengambil metadata dari Spotify API dan audio dari YouTube Music.

### Q: Kualitas audionya bagaimana?
A: Dengan setting `256k MP3`, kualitasnya setara Spotify "High Quality".

### Q: Kenapa ada lagu yang gagal?
A: Kemungkinan:
- Lagu tidak tersedia di YouTube Music
- Koneksi internet bermasalah
- Lagu regional (hanya tersedia di negara tertentu)

### Q: Bisa resume jika terputus?
A: Ya! Pastikan `skip_existing: true` di config, lalu jalankan ulang dengan URL yang sama.

## 🐛 Troubleshooting

### Error: "spotdl tidak ditemukan"
```bash
pip install spotdl rich
```

### Error saat install spotdl
Jika ada error dengan version tertentu, install tanpa version:
```bash
pip install spotdl rich
```

### Download lambat
- Pastikan koneksi internet stabil
- Coba di waktu yang berbeda

### Script tidak jalan
Pastikan Python 3.8+:
```bash
python --version
```

## 📝 Notes

- Script ini menggunakan `spotdl` library yang mengambil audio dari YouTube Music
- Gunakan untuk personal use only
- Respect copyright dan music licensing

## 🙏 Credits

- [spotdl](https://github.com/spotDL/spotify-downloader) - Spotify downloader library
- [rich](https://github.com/Textualize/rich) - Beautiful terminal formatting

---

**Happy Downloading! 🎵✨**
