#!/usr/bin/env python3
"""
Spotify Playlist Downloader
Download semua lagu dari playlist Spotify dengan metadata lengkap
"""

import json
import os
import sys
import subprocess
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    print("❌ Rich library belum terinstall!")
    print("Jalankan: pip install rich")
    sys.exit(1)


class SpotifyDownloader:
    def __init__(self, config_path: str = "config.json"):
        """Initialize downloader dengan konfigurasi"""
        self.console = Console()
        self.config = self.load_config(config_path)
        
    def load_config(self, config_path: str) -> dict:
        """Load konfigurasi dari file JSON"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.console.print(f"[yellow]⚠️  Config file tidak ditemukan, menggunakan default settings[/yellow]")
                return {
                    "output_folder": "downloads",
                    "audio_format": "mp3",
                    "bitrate": "256k",
                    "filename_template": "{artist} - {title}",
                    "download_lyrics": True,
                    "threads": 4,
                    "skip_existing": True
                }
        except Exception as e:
            self.console.print(f"[red]❌ Error loading config: {e}[/red]")
            sys.exit(1)
    
    def display_banner(self):
        """Tampilkan banner aplikasi"""
        banner = """
[bold cyan]╔═══════════════════════════════════════════════╗
║                                               ║
║     🎵  SPOTIFY PLAYLIST DOWNLOADER  🎵       ║
║                                               ║
║   Download lagu dari playlist Spotify dengan  ║
║        metadata lengkap & cover art           ║
║                                               ║
╚═══════════════════════════════════════════════╝[/bold cyan]
"""
        self.console.print(banner)
    
    def display_config(self):
        """Tampilkan konfigurasi aktif"""
        table = Table(title="⚙️  Konfigurasi Aktif", show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Output Folder", self.config.get("output_folder", "downloads"))
        table.add_row("Audio Format", self.config.get("audio_format", "mp3").upper())
        table.add_row("Bitrate", self.config.get("bitrate", "256k"))
        table.add_row("Download Lyrics", "✅" if self.config.get("download_lyrics", True) else "❌")
        table.add_row("Skip Existing", "✅" if self.config.get("skip_existing", True) else "❌")
        
        self.console.print(table)
        self.console.print()
    
    def get_playlist_url(self) -> str:
        """Minta input URL playlist dari user"""
        self.console.print("[bold yellow]📋 Masukkan URL Spotify Playlist:[/bold yellow]")
        self.console.print("[dim](Contoh: https://open.spotify.com/playlist/...)[/dim]")
        self.console.print("[dim]Support: playlist, album, track, atau artist[/dim]")
        
        url = input("\n🔗 URL: ").strip()
        
        if not url:
            self.console.print("[red]❌ URL tidak boleh kosong![/red]")
            sys.exit(1)
        
        # Validasi basic
        if "spotify.com" not in url and "spotify:" not in url:
            self.console.print("[yellow]⚠️  URL tidak terlihat seperti Spotify URL, tapi akan dicoba...[/yellow]")
        
        return url
    
    def check_spotdl(self):
        """Check if spotdl is installed"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "spotdl", "--help"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def download_playlist(self, url: str) -> dict:
        """Download playlist dari URL menggunakan spotdl"""
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }
        
        try:
            # Check if spotdl available
            if not self.check_spotdl():
                self.console.print("[red]❌ spotdl tidak ditemukan atau tidak bisa dijalankan![/red]")
                self.console.print("[yellow]Coba install ulang dengan: pip uninstall spotdl && pip install spotdl[/yellow]")
                return stats
            
            self.console.print(f"\n[bold cyan]🔍 Memulai download dari Spotify...[/bold cyan]\n")
            
            # Get output folder
            output_folder = self.config.get("output_folder", "downloads")
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            # Build spotdl command menggunakan python -m
            cmd = [
                sys.executable, "-m", "spotdl",
                url,
                "--output", output_folder,
                "--output-format", self.config.get("audio_format", "mp3"),
            ]

            
            self.console.print(f"[dim]Running: python -m spotdl ...[/dim]\n")
            
            # Run spotdl
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Stream output
            download_count = 0
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Tampilkan output dengan color coding
                    if "Downloaded" in line or "Success" in line or "✓" in line:
                        self.console.print(f"[green]✅ {line}[/green]")
                        download_count += 1
                    elif "Skipping" in line or "exists" in line.lower():
                        self.console.print(f"[yellow]⏭️  {line}[/yellow]")
                        stats["skipped"] += 1
                    elif "error" in line.lower() or "failed" in line.lower() or "✗" in line:
                        self.console.print(f"[red]❌ {line}[/red]")
                        stats["failed"] += 1
                    elif "Downloading" in line or "Found" in line or "Searching" in line:
                        self.console.print(f"[cyan]🔄 {line}[/cyan]")
                    else:
                        # Print other lines without emoji
                        self.console.print(f"[dim]{line}[/dim]")
            
            process.wait()
            
            # Count files in output folder
            output_path = Path(output_folder)
            audio_format = self.config.get("audio_format", "mp3")
            audio_files = list(output_path.glob(f"*.{audio_format}"))
            stats["total"] = len(audio_files)
            
            if process.returncode == 0:
                self.console.print(f"\n[green]✅ Proses selesai![/green]")
                stats["success"] = max(download_count, stats["total"] - stats["skipped"] - stats["failed"])
            else:
                self.console.print(f"\n[yellow]⚠️  Proses selesai dengan beberapa warning (exit code: {process.returncode})[/yellow]")
                stats["success"] = stats["total"] - stats["skipped"] - stats["failed"]
                
        except FileNotFoundError:
            self.console.print(f"\n[red]❌ Error: spotdl tidak ditemukan![/red]")
            self.console.print(f"[yellow]Install dengan: pip install spotdl[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error saat download: {e}[/red]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
            
        return stats
    
    def display_summary(self, stats: dict):
        """Tampilkan ringkasan hasil download"""
        self.console.print("\n")
        
        # Create summary panel
        summary_text = f"""
[bold]Total File di Folder:[/bold] {stats['total']}
[bold green]✅ Berhasil:[/bold green] {stats['success']}
[bold yellow]⏭️  Dilewati:[/bold yellow] {stats['skipped']}
[bold red]❌ Gagal:[/bold red] {stats['failed']}
"""
        
        self.console.print(Panel(
            summary_text,
            title="📊 Ringkasan Download",
            border_style="cyan"
        ))
        
        # Final message
        if stats["total"] > 0:
            output_folder = self.config.get("output_folder", "downloads")
            abs_path = Path(output_folder).absolute()
            self.console.print(f"\n[bold green]🎉 File tersimpan di: {abs_path}[/bold green]")
            self.console.print(f"[dim]Total {stats['total']} file .{self.config.get('audio_format', 'mp3')}[/dim]")
        else:
            self.console.print(f"\n[yellow]⚠️  Tidak ada file yang didownload[/yellow]")
        
    def run(self):
        """Main function untuk menjalankan downloader"""
        try:
            self.display_banner()
            self.display_config()
            
            # Get playlist URL
            url = self.get_playlist_url()
            
            # Download playlist
            stats = self.download_playlist(url)
            
            # Display summary
            self.display_summary(stats)
            
        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]⚠️  Download dibatalkan oleh user (Ctrl+C)[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
            import traceback
            self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
            sys.exit(1)


def main():
    """Entry point"""
    downloader = SpotifyDownloader()
    downloader.run()


if __name__ == "__main__":
    main()
