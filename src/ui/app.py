from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, ListItem, ListView, Label
from textual.binding import Binding
from textual.reactive import reactive

from src.tools.player import AudioPlayer
from src.tools.playlist_manager import PlaylistManager
from src.tools.config_manager import ConfigManager
from src.ui.widgets.visualizer import Visualizer

import os

class MuzikApp(App):
    """The main TUI for Muzik."""
    
    CSS = """
    Screen {
        background: #1a1b26;
    }
    
    #main_view {
        height: 1fr;
    }
    
    #song_list {
        width: 60%;
        border: solid green;
    }
    
    #visualizer_panel {
        width: 40%;
        border: solid cyan;
        align: center middle;
    }
    
    #footer_ctrls {
        height: 3;
        background: #24283b;
        border-top: solid #414868;
        padding: 0 1;
    }
    
    #command_bar {
        dock: bottom;
        display: none;
    }
    
    .playing {
        color: lime;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("space", "toggle_play", "Play/Pause", show=True),
        Binding("l", "seek_forward", "Seek +10s", show=False),
        Binding("h", "seek_backward", "Seek -10s", show=False),
        Binding("right", "seek_forward", "Seek +10s", show=True),
        Binding("left", "seek_backward", "Seek -10s", show=True),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("colon", "show_command_bar", "Command", show=True),
        Binding("escape", "hide_command_bar", "Back", show=False),
    ]

    current_song = reactive("No song playing")
    progress_text = reactive("00:00 / 00:00")

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.player = AudioPlayer()
        self.playlist_mgr = PlaylistManager()
        self.songs = self.load_local_songs()

    def load_local_songs(self):
        # Use saved directory or default to 'audios'
        audio_dir = self.config.get("music_dir", "/media/mrclammity/Codes/Python/muzik/audios")
        if not os.path.exists(audio_dir):
            try:
                os.makedirs(audio_dir)
            except Exception:
                return []
        EXTS = ('.mp3', '.m4a', '.wav', '.flac', '.mp4', '.mkv', '.webm', '.ogg')
        return sorted([f for f in os.listdir(audio_dir) if f.lower().endswith(EXTS)])

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main_view"):
            with ListView(id="song_list"):
                for song in self.songs:
                    yield ListItem(Label(song), name=song)
            with Vertical(id="visualizer_panel"):
                yield Label("VISUALIZER", id="vis_label")
                yield Visualizer()
        
        with Horizontal(id="footer_ctrls"):
            yield Label(self.current_song, id="current_song_label")
            yield Label(" | ", id="separator")
            yield Label(self.progress_text, id="progress_label")
            
        yield Input(placeholder="Enter command...", id="command_bar")
        yield Footer()

    def on_mount(self) -> None:
        self.set_interval(1.0, self.update_progress)

    def update_progress(self) -> None:
        if self.player.engine.is_playing():
            curr, total = self.player.get_progress()
            curr_s = curr // 1000
            total_s = total // 1000
            self.progress_text = f"{curr_s//60:02}:{curr_s%60:02} / {total_s//60:02}:{total_s%60:02}"
            self.query_one("#progress_label").update(self.progress_text)

    def action_toggle_play(self) -> None:
        if self.player.is_paused:
            self.player.play()
        else:
            self.player.pause()

    def action_seek_forward(self) -> None:
        self.player.skip_forward(10)

    def action_seek_backward(self) -> None:
        self.player.skip_backward(10)

    def action_cursor_down(self) -> None:
        self.query_one(ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(ListView).action_cursor_up()

    def action_show_command_bar(self) -> None:
        cmd_bar = self.query_one("#command_bar")
        cmd_bar.display = True
        cmd_bar.focus()

    def action_hide_command_bar(self) -> None:
        cmd_bar = self.query_one("#command_bar")
        cmd_bar.display = False
        self.query_one(ListView).focus()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        song_name = event.item.name
        audio_dir = self.config.get("music_dir", "/media/mrclammity/Codes/Python/muzik/audios")
        path = os.path.join(audio_dir, song_name)
        self.player.load(path)
        self.player.play()
        self.current_song = song_name
        self.query_one("#current_song_label").update(f"Playing: {song_name}")
        self.config.add_to_history(song_name)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if cmd.startswith("open "):
            url = cmd[5:].strip()
            self.player.load(url)
            self.player.play()
            self.current_song = url
            self.query_one("#current_song_label").update(f"Streaming: {url}")
            self.config.add_to_history(url)
        
        elif cmd.startswith("setdir "):
            new_dir = cmd[7:].strip().strip('"').strip("'")
            if os.path.isdir(new_dir):
                self.config.set("music_dir", new_dir)
                EXTS = ('.mp3', '.m4a', '.wav', '.flac', '.mp4', '.mkv', '.webm', '.ogg')
                self.songs = sorted([f for f in os.listdir(new_dir) if f.lower().endswith(EXTS)])
                # Update ListView
                list_view = self.query_one("#song_list", ListView)
                list_view.clear()
                for song in self.songs:
                    list_view.append(ListItem(Label(song), name=song))
                list_view.focus()
                self.notify(f"Directory changed to: {new_dir}")
            else:
                self.notify(f"Invalid directory: {new_dir}", severity="error")

        self.action_hide_command_bar()
        self.query_one("#command_bar").value = ""

if __name__ == "__main__":
    app = MuzikApp()
    app.run()
