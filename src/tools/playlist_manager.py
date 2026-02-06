import json
import os
from typing import List, Dict

class PlaylistManager:
    def __init__(self, storage_dir: str = "playlists"):
        self.storage_dir = storage_dir
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def save_playlist(self, name: str, tracks: List[Dict]):
        """Saves a playlist as a JSON file."""
        filepath = os.path.join(self.storage_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(tracks, f, indent=4)

    def load_playlist(self, name: str) -> List[Dict]:
        """Loads a playlist from a JSON file."""
        filepath = os.path.join(self.storage_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return []

    def list_playlists(self) -> List[str]:
        """Lists available playlist names."""
        return [f.replace(".json", "") for f in os.listdir(self.storage_dir) if f.endswith(".json")]

    def delete_playlist(self, name: str):
        """Deletes a playlist file."""
        filepath = os.path.join(self.storage_dir, f"{name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
