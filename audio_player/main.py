import sys

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header

from audio_player.player import Player
from audio_player.utils import scan_folder_with_metadata
from audio_player.widgets.controls import ProgressBar, StatusBar, VolumeBar
from audio_player.widgets.playlist import Playlist
from audio_player.widgets.visualizer import Visualizer


class MuzikApp(App):
    BINDINGS = [
        Binding("space", "play_pause", "Play/Pause"),
        Binding("n", "next_track", "Next"),
        Binding("p", "prev_track", "Previous"),
        Binding("left", "seek_back", "Seek -5s"),
        Binding("right", "seek_fwd", "Seek +5s"),
        Binding("plus", "vol_up", "Volume +"),
        Binding("minus", "vol_down", "Volume -"),
        Binding("l", "cycle_loop", "Loop"),
        Binding("s", "toggle_shuffle", "Shuffle"),
    ]

    def __init__(self, folder: str) -> None:
        super().__init__()
        self._folder = folder
        self.player = Player()

    def compose(self) -> ComposeResult:
        tracks = scan_folder_with_metadata(self._folder)
        self.player.set_tracks(tracks)
        yield Header()
        yield Visualizer(self.player)
        yield ProgressBar(self.player)
        yield VolumeBar(self.player)
        yield StatusBar(self.player)
        yield Playlist(tracks)

    def on_mount(self) -> None:
        self.set_interval(0.5, self._refresh_progress)
        self.set_interval(1 / 30, self._refresh_visualizer)

    def _refresh_visualizer(self) -> None:
        self.query_one(Visualizer).refresh()

    def _refresh_progress(self) -> None:
        self.query_one(ProgressBar).refresh()
        self.query_one(VolumeBar).refresh()
        self.query_one(StatusBar).refresh()

    def action_play_pause(self) -> None:
        track = self.player.current_track
        if track is None:
            return
        if self.player.is_playing or self.player.is_paused:
            self.player.toggle_pause()
        else:
            self.player.play()

    def action_next_track(self) -> None:
        self.player.next()

    def action_prev_track(self) -> None:
        self.player.previous()

    def action_seek_back(self) -> None:
        self.player.seek_relative(-5)

    def action_seek_fwd(self) -> None:
        self.player.seek_relative(5)

    def action_vol_up(self) -> None:
        self.player.volume = min(1.0, self.player.volume + 0.1)

    def action_vol_down(self) -> None:
        self.player.volume = max(0.0, self.player.volume - 0.1)

    def action_cycle_loop(self) -> None:
        self.player.cycle_loop()

    def action_toggle_shuffle(self) -> None:
        self.player.toggle_shuffle()


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    app = MuzikApp(folder)
    app.run()


if __name__ == "__main__":
    main()
