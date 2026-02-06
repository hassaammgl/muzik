from .engine import PlayerEngine

class AudioPlayer:
    def __init__(self):
        self.engine = PlayerEngine()
        self.is_paused = False

    def load(self, path: str):
        self.engine.load(path)
        self.is_paused = False

    def play(self):
        self.engine.play()
        self.is_paused = False

    def pause(self):
        self.engine.pause()
        self.is_paused = True

    def stop(self):
        self.engine.stop()
        self.is_paused = False

    def skip_forward(self, seconds: int = 10):
        current = self.engine.get_time()
        self.engine.set_time(current + seconds * 1000)

    def skip_backward(self, seconds: int = 10):
        current = self.engine.get_time()
        self.engine.set_time(max(0, current - seconds * 1000))
        
    def get_progress(self):
        """Returns (current_ms, total_ms)"""
        return self.engine.get_time(), self.engine.get_length()
