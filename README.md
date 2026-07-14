# muzik

A terminal audio player built with [Textual](https://textual.textualize.io/).

## Features

- Audio playback via sounddevice/soundfile (MP3, FLAC, WAV, OGG)
- Real-time spectrum visualizer
- Playlist from folder scan (metadata via mutagen)
- Play/Pause, Next/Previous, Seek
- Volume control
- Loop modes: None / One / All
- Shuffle mode

## Installation

Requires Python 3.14+ and `uv`.

```bash
uv sync
```

## Usage

```bash
uv run python -m audio_player.main /path/to/music/folder
```

## Keybindings

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `n` | Next track |
| `p` | Previous track |
| `←` | Seek back 5s |
| `→` | Seek forward 5s |
| `+` | Volume up |
| `-` | Volume down |
| `l` | Cycle loop (none → one → all → none) |
| `s` | Toggle shuffle |
