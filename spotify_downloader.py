import os
import re
import time
import math
import requests
import yt_dlp
import spotipy
from typing import List, Dict, Optional
from spotipy.oauth2 import SpotifyClientCredentials
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, APIC, error as ID3Error
from mutagen.mp3 import MP3

# ====== KONFIGURASI WAJIB ======
SPOTIPY_CLIENT_ID = "947204ec6fb0422aaf80122bfca44520"
SPOTIPY_CLIENT_SECRET = "d6335ed2548640dc984c81fa9963e992"
DOWNLOAD_DIR = "downloads"

# ====== UTIL ======
def sanitize_filename(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name

def sec(ms: int) -> int:
    return int(round(ms / 1000))

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

# ====== SPOTIFY CLIENT ======
def get_spotify_client() -> spotipy.Spotify:
    auth = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
    return spotipy.Spotify(auth_manager=auth, requests_timeout=10, retries=3)

def fetch_playlist_tracks(sp: spotipy.Spotify, playlist_url: str) -> List[Dict]:
    tracks = []
    limit = 100
    offset = 0
    print("Mengambil dari Spotify...")
    while True:
        page = sp.playlist_items(playlist_url, limit=limit, offset=offset)
        items = page.get("items", [])
        for item in items:
            t = item.get("track")
            if not t or t.get("is_local"):
                continue
            title = t.get("name", "")
            artists = [a.get("name", "") for a in t.get("artists", [])]
            album = (t.get("album") or {}).get("name", "")
            release_date = (t.get("album") or {}).get("release_date", "") or ""
            year = release_date[:4] if release_date else ""
            duration_ms = t.get("duration_ms") or 0
            images = (t.get("album") or {}).get("images") or []
            cover_url = images[0]["url"] if images else None
            track_no = t.get("track_number")
            genres = []
            try:
                first_artist = t.get("artists", [None])[0]
                artist_id = first_artist.get("id") if first_artist else None
                if artist_id:
                    a = sp.artist(artist_id)
                    genres = a.get("genres") or []
            except Exception:
                pass

            tracks.append({
                "title": title,
                "artists": artists,
                "album": album,
                "year": year or "",
                "duration_s": sec(duration_ms),
                "cover_url": cover_url,
                "track_no": track_no,
                "genres": genres
            })
        # pagination
        if page.get("next"):
            offset += limit
        else:
            break
    return tracks

# ====== YOUTUBE SEARCH + DOWNLOAD ======
def choose_best_entry(entries: List[Dict], target_duration_s: int) -> Optional[Dict]:
    if not entries:
        return None
    # pilih entry dengan perbedaan durasi paling kecil (jika durasi tersedia)
    best = None
    best_diff = None
    for e in entries:
        dur = e.get("duration")
        if dur is None:
            # beri penalti besar jika durasi tidak tersedia
            diff = 999999
        else:
            diff = abs((dur or 0) - (target_duration_s or 0))
        if best is None or diff < best_diff:
            best = e
            best_diff = diff
    return best

def search_youtube_and_download(track: Dict, out_path: str) -> Optional[str]:
    query = f"{track['title']} {' '.join(track['artists'])}"
    print(f"  🔎 Mencari YouTube: {query}")

    ydl_search_opts = {"quiet": True, "skip_download": True, "extract_flat": False}
    info = None
    try:
        with yt_dlp.YoutubeDL(ydl_search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
    except Exception as e:
        print(f"  ⚠️  Error saat mencari YouTube: {e}")
        return None

    entries = (info or {}).get("entries") or []
    if not entries:
        print("  ⚠️  Tidak ditemukan hasil YouTube.")
        return None

    chosen = choose_best_entry(entries, track.get("duration_s", 0))
    if not chosen:
        chosen = entries[0]

    url = chosen.get("webpage_url") or chosen.get("id")
    print(f"  ▶️  Pilihan: {chosen.get('title')} (durasi {chosen.get('duration')}s)")

    # pastikan folder ada
    ensure_dir(os.path.dirname(out_path) or ".")

    # outtmpl: gunakan placeholder ext agar yt_dlp membuat file sumber lalu postprocessor menghasilkan .mp3
    # Contoh: downloads/Artist - Title.%(ext)s  -> postproc akan menghasilkan downloads/Artist - Title.mp3
    outtmpl = os.path.splitext(out_path)[0] + ".%(ext)s"

    ydl_dl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "noplaylist": True,
        "quiet": True,
        # kita percayakan PATH ffmpeg yang sudah kamu atur
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",  # legacy; we'll force bitrate in postprocessor_args
        }],
        # atur ffmpeg args: sample rate 44100, bitrate 192k
        "postprocessor_args": ["-ar", "44100", "-b:a", "192k"],
        "prefer_ffmpeg": True,
        "nopart": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_dl_opts) as ydl:
            ydl.download([url])
        # hasil akhir path mp3
        final_mp3 = os.path.splitext(out_path)[0] + ".mp3"
        if os.path.exists(final_mp3):
            return final_mp3
        else:
            # kadang file berekstensi berbeda; cari file terdekat di folder
            base = os.path.splitext(out_path)[0]
            for ext in (".mp3", ".m4a", ".webm", ".opus"):
                candidate = base + ext
                if os.path.exists(candidate):
                    # jika bukan mp3, coba konversi (fallback) -- but normally postprocessor made mp3
                    if ext != ".mp3":
                        # convert using ffmpeg (external), but hanya jika ffmpeg tersedia
                        converted = base + ".mp3"
                        cmd = f'ffmpeg -y -i "{candidate}" -ar 44100 -b:a 192k "{converted}"'
                        os.system(cmd)
                        if os.path.exists(converted):
                            return converted
                    else:
                        return candidate
    except Exception as e:
        print(f"  ❌ Error download: {e}")
        return None

    return None

# ====== METADATA ======
def write_id3_tags(mp3_path: str, track: Dict):
    if not os.path.exists(mp3_path):
        print(f"  ⚠️ File tidak ditemukan: {mp3_path}")
        return

    # pastikan ID3 ada
    try:
        audio = MP3(mp3_path, ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
            audio.save()
    except ID3Error:
        pass
    except Exception:
        pass

    try:
        tags = ID3(mp3_path)
    except Exception:
        # kalau gagal load, buat baru
        tags = ID3()

    # set frames
    tags.add(TIT2(encoding=3, text=track.get("title", "")))
    tags.add(TPE1(encoding=3, text=", ".join(track.get("artists", []))))
    tags.add(TALB(encoding=3, text=track.get("album", "")))
    if track.get("year"):
        tags.add(TDRC(encoding=3, text=track.get("year")))
    if track.get("track_no"):
        tags.add(TRCK(encoding=3, text=str(track.get("track_no"))))
    if track.get("genres"):
        tags.add(TCON(encoding=3, text=", ".join(track.get("genres")[:3])))

    cover_url = track.get("cover_url")
    if cover_url:
        try:
            resp = requests.get(cover_url, timeout=20)
            resp.raise_for_status()
            img_data = resp.content
            # detect mime (simple)
            mime = "image/jpeg"
            if img_data.startswith(b"\x89PNG"):
                mime = "image/png"
            tags.add(APIC(encoding=3, mime=mime, type=3, desc="Cover", data=img_data))
        except Exception as e:
            print(f"  ⚠️  Gagal mengambil cover art: {e}")

    # simpan
    try:
        tags.save(mp3_path, v2_version=3)
        print("  🏷️  Metadata & cover art ditulis.")
    except Exception as e:
        print(f"  ⚠️  Gagal menyimpan tag ID3: {e}")

# ====== MAIN PROCESS ======
def process_playlist(playlist_url: str):
    ensure_dir(DOWNLOAD_DIR)
    sp = get_spotify_client()
    print("Mengambil daftar lagu dari Spotify...")
    tracks = fetch_playlist_tracks(sp, playlist_url)
    print(f"Total lagu: {len(tracks)}\n")

    for i, t in enumerate(tracks, 1):
        base_name = f"{', '.join(t['artists'])} - {t['title']}"
        file_name = sanitize_filename(base_name) + ".mp3"
        out_path = os.path.join(DOWNLOAD_DIR, file_name)

        print(f"[{i}/{len(tracks)}] {base_name}")

        if os.path.exists(out_path):
            print("  ✅ Sudah ada, lewati.")
            continue

        mp3_file = search_youtube_and_download(t, out_path)
        if not mp3_file or not os.path.exists(mp3_file):
            print("  ⏭️  Lewati lagu ini.\n")
            continue

        try:
            write_id3_tags(mp3_file, t)
        except Exception as e:
            print(f"  ⚠️  Gagal menulis metadata: {e}")

        print("  ✅ Selesai.\n")
        time.sleep(1)

if __name__ == "__main__":
    try:
        playlist_url = input("Masukkan URL playlist Spotify: ").strip()
        if not playlist_url:
            raise SystemExit("URL playlist diperlukan.")
        process_playlist(playlist_url)
        print("Selesai semua. 🎉 File ada di folder 'downloads'.")
    except Exception as e:
        print(f"Error fatal: {e}")
