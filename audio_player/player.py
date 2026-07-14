import os
import queue
import random
import threading
import time

import numpy as np
import sounddevice as sd
import soundfile as sf


class Player:
    def __init__(self):
        self._thread: threading.Thread | None = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._tracks: list[dict] = []
        self._track_index: int = 0
        self._current_frame: int = 0
        self._samplerate: int = 0
        self._total_frames: int = 0
        self._volume: float = 0.5
        self.chunk_queue: queue.Queue = queue.Queue(maxsize=10)
        self._loop_mode: str = "none"
        self._random = random.Random()
        self._shuffle: bool = False
        self._played_indexes: list[int] = []
        self._audio_pipe_path: str | None = None
        self._audio_pipe_fd: int | None = None

    def set_audio_pipe(self, path: str) -> None:
        self._audio_pipe_path = path

    def clear_audio_pipe(self) -> None:
        if self._audio_pipe_fd is not None:
            try:
                os.close(self._audio_pipe_fd)
            except OSError:
                pass
            self._audio_pipe_fd = None
        self._audio_pipe_path = None

    def set_tracks(self, tracks: list[dict]) -> None:
        self._tracks = tracks

    @property
    def current_track(self) -> dict | None:
        if not self._tracks:
            return None
        return self._tracks[self._track_index]

    @property
    def position_seconds(self) -> float:
        if self._samplerate == 0:
            return 0.0
        return self._current_frame / self._samplerate

    @property
    def duration_seconds(self) -> float:
        if self._samplerate == 0:
            return 0.0
        return self._total_frames / self._samplerate

    def play(self, path: str | None = None, start_frame: int = 0) -> None:
        if path is None:
            path = self.current_track["path"] if self.current_track else None
        if path is None:
            return
        self.stop()
        self._current_frame = start_frame
        self._pause_event.clear()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, args=(path,), daemon=True)
        self._thread.start()

    def pause(self) -> None:
        self._pause_event.set()

    def resume(self) -> None:
        self._pause_event.clear()

    def toggle_pause(self) -> None:
        if self._pause_event.is_set():
            self.resume()
        else:
            self.pause()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        self._thread = None

    def _pick_next_index(self) -> int:
        if not self._shuffle:
            return (self._track_index + 1) % len(self._tracks)
        unplayed = [i for i in range(len(self._tracks)) if i not in self._played_indexes]
        if not unplayed:
            self._played_indexes = []
            unplayed = list(range(len(self._tracks)))
        choice = self._random.choice(unplayed)
        self._played_indexes.append(choice)
        return choice

    def next(self) -> None:
        if not self._tracks:
            return
        self._track_index = self._pick_next_index()
        self.play()

    def previous(self) -> None:
        if not self._tracks:
            return
        self._track_index = (self._track_index - 1) % len(self._tracks)
        self.play()

    @property
    def loop_mode(self) -> str:
        return self._loop_mode

    def cycle_loop(self) -> None:
        modes = ["none", "one", "all"]
        self._loop_mode = modes[(modes.index(self._loop_mode) + 1) % len(modes)]

    @property
    def shuffle(self) -> bool:
        return self._shuffle

    def toggle_shuffle(self) -> None:
        self._shuffle = not self._shuffle
        if self._shuffle:
            self._played_indexes = []

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))

    @property
    def is_playing(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and not self._pause_event.is_set()

    @property
    def is_paused(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and self._pause_event.is_set()

    def seek_relative(self, delta_seconds: float) -> None:
        pos = self._current_frame + int(delta_seconds * self._samplerate)
        pos = max(0, min(pos, self._total_frames))
        path = self.current_track["path"] if self.current_track else None
        if path:
            self.play(path, start_frame=pos)

    def _write_audio_pipe(self, chunk: "np.ndarray") -> None:
        if self._audio_pipe_path is None:
            return
        if self._audio_pipe_fd is None:
            try:
                fd = os.open(self._audio_pipe_path, os.O_WRONLY | os.O_NONBLOCK)
                self._audio_pipe_fd = fd
            except OSError:
                return
        try:
            int_chunk = np.clip(chunk, -1, 1) * 32767
            int_chunk = int_chunk.astype(np.int16)
            if int_chunk.ndim > 1:
                int_chunk = int_chunk.mean(axis=1, keepdims=True).astype(np.int16)
            os.write(self._audio_pipe_fd, int_chunk.tobytes())
        except (OSError, BlockingIOError):
            pass

    def _run(self, path: str) -> None:
        try:
            sf_info = sf.info(path)
        except Exception:
            return
        self._samplerate = sf_info.samplerate
        self._total_frames = sf_info.frames

        try:
            out = sd.OutputStream(samplerate=self._samplerate, channels=sf_info.channels)
        except Exception:
            return

        with out:
            try:
                f = sf.SoundFile(path)
            except Exception:
                return
            with f:
                if self._current_frame > 0:
                    f.seek(self._current_frame)
                while not self._stop_event.is_set():
                    try:
                        chunk = f.read(8192, dtype="float32")
                    except Exception:
                        break
                    if len(chunk) == 0:
                        break
                    try:
                        self.chunk_queue.put_nowait(chunk)
                    except queue.Full:
                        pass
                    self._write_audio_pipe(chunk)
                    if not self._pause_event.is_set():
                        try:
                            out.write(chunk * self._volume)
                        except Exception:
                            break
                        self._current_frame += len(chunk)
                    else:
                        while self._pause_event.is_set() and not self._stop_event.is_set():
                            time.sleep(0.05)

        if self._stop_event.is_set():
            return

        if self._loop_mode == "one":
            self._current_frame = 0
            self._run(path)
        elif self._loop_mode == "all":
            self._track_index = (self._track_index + 1) % len(self._tracks)
            self.play()

    def __del__(self):
        self.clear_audio_pipe()
