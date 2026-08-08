# Setup Reference

## Quick Setup

```bash
./setup.sh
source scripts/env.sh
```

This installs everything project-locally into `.venv/` and `steganography-analyst/scripts/bin/`. No sudo, no system-wide changes.

## What Gets Installed

| Tool | Location | Method |
|------|----------|--------|
| stegoveritas, binwalk, Pillow, numpy | `.venv/` | `uv pip install` |
| jsteg | `steganography-analyst/scripts/bin/` | Pre-built binary download |
| StegSolve | `steganography-analyst/scripts/lib/` | JAR download (optional) |
| zsteg | `~/.gem/ruby/` | `gem install --user-install` |
| stegseek | `steganography-analyst/scripts/bin/` (Linux) | Binary from .deb |

System tools (exiftool, pngcheck, foremost, steghide, stegsnow, multimon-ng) are checked and `brew install` hints are printed if missing.

## Manual Installation (Fallback)

If `setup.sh` fails or you need individual tools:

### Python tools

```bash
uv venv .venv
source .venv/bin/activate
uv pip install stegoveritas binwalk Pillow numpy
```

### zsteg (requires Ruby)

```bash
gem install --user-install zsteg
```

### jsteg (pre-built binary)

Download from https://github.com/lukechampine/jsteg/releases — pick `darwin-arm64`, `darwin-amd64`, `linux-amd64`, or `linux-arm64`.

### StegSolve (Java JAR, optional)

Download from https://github.com/Giotino/stegsolve/releases/tag/v1.4 — place in `steganography-analyst/scripts/lib/StegSolve.jar`. Requires Java runtime.

### stegseek

- **macOS**: `brew install stegseek`
- **Linux**: Download `.deb` from https://github.com/RickdeJager/stegseek/releases and extract the binary

### System tools (macOS)

```bash
brew install exiftool pngcheck foremost steghide stegsnow multimon-ng
```
