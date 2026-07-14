from textual.widgets import ListView, ListItem, Label

from audio_player.utils import get_display_text


class Playlist(ListView):
    def __init__(self, tracks: list[dict]) -> None:
        self.tracks = [t for t in tracks]
        items = [ListItem(Label(get_display_text(t))) for t in self.tracks]
        if not items:
            items = [ListItem(Label("(empty)"), disabled=True)]
        super().__init__(*items)

    def get_selected_track(self):
        if self.index is None or not self.tracks:
            return None
        return self.tracks[self.index]
