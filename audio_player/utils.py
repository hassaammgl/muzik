import os

import mutagen

AUDIO_EXTENSIONS = {".mp3", ".flac", ".wav", ".ogg"}


def scan_folder(folder_path: str) -> list[str]:
    paths: list[str] = []
    for entry in os.scandir(folder_path):
        if entry.is_file():
            ext = os.path.splitext(entry.name)[1].lower()
            if ext in AUDIO_EXTENSIONS:
                paths.append(entry.path)
    return sorted(paths)


def get_metadata(file_path: str) -> dict:
    title = os.path.splitext(os.path.basename(file_path))[0]
    artist = "Unknown Artist"
    duration = 0.0

    try:
        mf = mutagen.File(file_path, easy=True)
        if mf is not None:
            if "title" in mf and mf["title"]:
                title = str(mf["title"][0])
            if "artist" in mf and mf["artist"]:
                artist = str(mf["artist"][0])
            duration = mf.info.length if hasattr(mf.info, "length") else 0.0
    except Exception:
        pass

    return {"path": file_path, "title": title, "artist": artist, "duration": duration}


def scan_folder_with_metadata(folder_path: str) -> list[dict]:
    return [get_metadata(f) for f in scan_folder(folder_path)]


def get_display_text(t: dict) -> str:
    return f"{t['artist']} - {t['title']}"
