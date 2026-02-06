from pathlib import Path
from tkinter import Tk, filedialog


class FileManager:

    VIDEO_EXTS = {".mp4", ".mkv", ".webm", ".3gp"}
    AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

    def __init__(self) -> None:
        self.files: list[dict] = []

    def print_in_kbs(self, bytes_):
        return f"{bytes_/1024:.2f}Kb"

    def ask_for_directory(self):
        Tk().withdraw()
        return filedialog.askdirectory()

    def scan(self, folder: str, mode: str = "audio") -> list[dict]:
        """
        mode: "audio" or "video"
        """
        self.files.clear()
        base = Path(folder).expanduser().resolve()

        if not base.exists():
            return []

        if mode == "audio":
            allowed_exts = self.AUDIO_EXTS
        elif mode == "video":
            allowed_exts = self.VIDEO_EXTS
        else:
            raise ValueError("Mode Must be 'audio' or 'video'")

        for item in base.rglob("*"):
            if not item.is_file():
                continue
            elif item.is_dir():
                continue
            else:
                if item.suffix.lower() in allowed_exts:
                    obj = {
                        "name": item.name,
                        "path": str(item),
                        "ext": item.suffix.lower(),
                        "size": self.print_in_kbs(item.stat().st_size),
                    }
                    self.files.append(obj)

        return self.files
