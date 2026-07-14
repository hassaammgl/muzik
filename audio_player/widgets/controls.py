from textual.widgets import Static


class ProgressBar(Static):
    def __init__(self, player) -> None:
        super().__init__("")
        self._player = player

    def render(self) -> str:
        dur = self._player.duration_seconds
        pos = self._player.position_seconds
        if dur <= 0:
            return ""
        pct = pos / dur
        width = self.size.width - 2
        filled = int(width * pct)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar}"


class VolumeBar(Static):
    def __init__(self, player) -> None:
        super().__init__("")
        self._player = player

    def render(self) -> str:
        vol = self._player.volume
        width = self.size.width - 2
        filled = int(width * vol)
        bar = "█" * filled + "░" * (width - filled)
        return f"Vol {bar}"


class StatusBar(Static):
    def __init__(self, player) -> None:
        super().__init__("")
        self._player = player

    def render(self) -> str:
        loop = self._player.loop_mode.upper()
        shuffle = "S" if self._player.shuffle else " "
        return f"Loop: {loop}  Shuffle: {shuffle}"
