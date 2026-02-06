import random
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType

class Visualizer(Widget):
    """A simple bar visualizer widget."""
    
    # We'll react to a "tick" or playback progress to animate
    bars = reactive([0] * 20)

    def on_mount(self) -> None:
        self.set_interval(0.1, self.update_bars)

    def update_bars(self) -> None:
        if self.app.player.engine.is_playing():
            # Simulated animation for now
            self.bars = [random.randint(1, 10) for _ in range(20)]
        else:
            self.bars = [0] * 20

    def render(self) -> RenderableType:
        text = Text()
        for bar in self.bars:
            text.append("█" * bar, style="bold cyan")
            text.append("\n")
        return text
