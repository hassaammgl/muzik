import os
import queue
import struct
import subprocess
import tempfile
import threading

import numpy as np
from textual.widgets import Static

NUM_BINS = 24
BLOCKS = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"

CAVA_CONF = """[general]
bars = {bars}
sleep_timer = 0

[input]
method = fifo
source = {fifo_path}
sample_rate = 44100
sample_bits = 16
channels = 1

[output]
method = raw
raw_target = /dev/stdout
bit_format = 16bit
channels = mono
data_format = binary
"""

FALLBACK_CHUNK_NUM_BINS = 24


class Visualizer(Static):
    def __init__(self, player) -> None:
        super().__init__("")
        self._player = player
        self._smoothed = np.zeros(NUM_BINS, dtype=float)
        self._peak = np.zeros(NUM_BINS, dtype=float)
        self._cava_proc: subprocess.Popen | None = None
        self._cava_data: np.ndarray | None = None
        self._cava_lock = threading.Lock()
        self._cava_active = False

    def on_mount(self) -> None:
        self._start_cava()

    def _start_cava(self) -> None:
        fifo_path = tempfile.mktemp(prefix="muzik_cava_", suffix=".fifo")
        try:
            os.mkfifo(fifo_path)
        except OSError:
            self._start_cava_fallback()
            return

        conf_path = tempfile.mktemp(prefix="muzik_cava_", suffix=".conf")
        try:
            with open(conf_path, "w") as f:
                f.write(CAVA_CONF.format(
                    bars=NUM_BINS,
                    fifo_path=fifo_path,
                ))
        except OSError:
            os.unlink(fifo_path)
            os.unlink(conf_path)
            self._start_cava_fallback()
            return

        try:
            self._cava_proc = subprocess.Popen(
                ["cava", "-p", conf_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self._cava_proc = None
            os.unlink(fifo_path)
            os.unlink(conf_path)
            self._start_cava_fallback()
            return

        self._fifo_path = fifo_path
        self._conf_path = conf_path
        self._player.set_audio_pipe(fifo_path)
        self._cava_active = True

        self._cava_thread = threading.Thread(target=self._read_cava, daemon=True)
        self._cava_thread.start()

    def _start_cava_fallback(self) -> None:
        self._cava_active = False

    def _read_cava(self) -> None:
        proc = self._cava_proc
        if proc is None or proc.stdout is None:
            return
        frame_size = NUM_BINS * 2
        buf = b""
        try:
            while proc.poll() is None:
                data = proc.stdout.read(frame_size)
                if not data:
                    break
                buf += data
                while len(buf) >= frame_size:
                    frame = buf[:frame_size]
                    buf = buf[frame_size:]
                    values = np.array(
                        struct.unpack(f"<{NUM_BINS}H", frame), dtype=float
                    )
                    with self._cava_lock:
                        self._cava_data = values
        except (OSError, struct.error):
            pass
        finally:
            self._cleanup_cava()

    def _cleanup_cava(self) -> None:
        self._player.clear_audio_pipe()
        if self._cava_proc:
            try:
                self._cava_proc.kill()
            except OSError:
                pass
            self._cava_proc = None
        self._cava_active = False
        for p in [self._fifo_path, self._conf_path]:
            try:
                os.unlink(p)
            except (OSError, AttributeError):
                pass

    def _process_queue(self) -> None:
        q = self._player.chunk_queue
        while q.qsize() > 0:
            try:
                chunk = q.get_nowait()
            except queue.Empty:
                break
            if chunk.ndim > 1:
                chunk = chunk.mean(axis=1)
            N = len(chunk)
            if N < 2:
                continue
            fft_vals = np.abs(np.fft.rfft(chunk))[:N // 2]
            fft_vals = fft_vals[1:]
            if len(fft_vals) < 2:
                continue
            bin_size = len(fft_vals) // FALLBACK_CHUNK_NUM_BINS
            if bin_size == 0:
                bin_size = 1
            bins = fft_vals[:FALLBACK_CHUNK_NUM_BINS * bin_size]
            bins = bins.reshape(FALLBACK_CHUNK_NUM_BINS, bin_size).mean(axis=1) + 1e-10
            db = 20 * np.log10(bins)
            self._smoothed = 0.4 * db + 0.6 * self._smoothed
            self._peak = np.maximum(self._smoothed, self._peak * 0.92)

    def _get_cava_values(self) -> np.ndarray | None:
        with self._cava_lock:
            if self._cava_data is not None:
                return self._cava_data.copy()
            return None

    def render(self) -> str:
        data = None
        if self._cava_active:
            cava_vals = self._get_cava_values()
            if cava_vals is not None:
                data = cava_vals
        if data is None:
            self._process_queue()
            data = self._peak
        else:
            self._smoothed = 0.4 * data + 0.6 * self._smoothed
            self._peak = np.maximum(self._smoothed, self._peak * 0.92)
            data = self._peak
        if data.max() - data.min() < 1:
            return ""
        norm = (data - data.min()) / (data.max() - data.min() + 1e-10)
        scaled = np.clip((norm * 7).astype(int), 0, 7)
        width = min(self.size.width - 2, NUM_BINS)
        visible = scaled[:width]
        return "\u2502" + "".join(BLOCKS[v] for v in visible) + "\u2502"
