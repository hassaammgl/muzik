import vlc
import yt_dlp
import threading
import time
from typing import Optional, Callable

class PlayerEngine:
    def __init__(self):
        self.instance = vlc.Instance("--no-video", "--quiet")
        self.player = self.instance.media_player_new()
        self.current_media = None
        self.is_url = False
        
        # yt-dlp options for audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }

    def load(self, source: str):
        """Load a local file path or a URL."""
        if source.startswith(('http://', 'https://')):
            self.is_url = True
            self._load_url(source)
        else:
            self.is_url = False
            media = self.instance.media_new(source)
            self.player.set_media(media)

    def _load_url(self, url: str):
        """Extract audio stream URL using yt-dlp and load into VLC."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                stream_url = info.get('url')
                if stream_url:
                    media = self.instance.media_new(stream_url)
                    self.player.set_media(media)
        except Exception as e:
            print(f"Error loading URL: {e}")

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def get_time(self) -> int:
        """Get current time in milliseconds."""
        return self.player.get_time()

    def set_time(self, ms: int):
        """Set current time in milliseconds."""
        self.player.set_time(ms)

    def get_length(self) -> int:
        """Get total length in milliseconds."""
        return self.player.get_length()

    def is_playing(self) -> bool:
        return self.player.is_playing()

    def get_state(self):
        return self.player.get_state()
