# steganography-analyst

[![skills.sh](https://skills.sh/b/CasualSecurityInc/steganography-analyst)](https://skills.sh/CasualSecurityInc/steganography-analyst)

An AI agent skill for steganography detection and extraction. Provides a structured decision tree and toolchain for analyzing images, audio, files, and text for hidden data — designed for CTF challenges, digital forensics, and security research.

## What's included

### Bundled Python tools (zero external dependencies)

| Tool | Purpose |
|------|---------|
| `tools/bit_plane_extract.py` | Bit plane extraction & XOR/AND/OR — CLI replacement for StegSolve |
| `tools/png_crc_fix.py` | Brute-force correct PNG dimensions when IHDR CRC is tampered |
| `tools/wavsteg.py` | Extract data hidden in WAV LSB steganography |
| `tools/wav_header_check.py` | Detect data appended after WAV audio content |
| `tools/zero_width_decode.py` | Decode zero-width Unicode character steganography |
| `tools/homoglyph_detect.py` | Detect visually-similar character substitution (Cyrillic/Latin swaps etc.) |

### External tools (installed project-locally via `setup.sh`)

| Tool | Category | Install method |
|------|----------|----------------|
| [stegoveritas](https://github.com/bannsec/stegoveritas) | Automated multi-tool analysis | `uv pip install` |
| [binwalk](https://github.com/ReFirmLabs/binwalk) | Embedded file extraction | `uv pip install` |
| [zsteg](https://github.com/zed-0xff/zsteg) | PNG/BMP LSB detection | `gem install --user-install` |
| [jsteg](https://github.com/lukechampine/jsteg) | JPEG LSB extraction | Pre-built binary |
| [stegseek](https://github.com/RickdeJager/stegseek) | Steghide passphrase cracker | Binary (Linux) / brew (macOS) |
| [StegSolve](https://github.com/Giotino/stegsolve) | Visual bit plane GUI | JAR download (optional, needs Java) |

### Techniques covered

- **Image**: LSB analysis, PNG chunk inspection, JPEG DCT, EXIF metadata extraction, palette manipulation, dimension/CRC tricks, bit plane visualization
- **Audio**: Spectrogram analysis, WAV LSB, DTMF decoding, SSTV, appended data detection
- **File**: Polyglot detection, embedded file carving (binwalk/foremost), NTFS alternate data streams
- **Text**: Whitespace encoding (stegsnow), zero-width Unicode steganography, homoglyph substitution

## Quick start

```bash
./setup.sh          # installs everything project-locally (no sudo)
source tools/env.sh # adds tools to PATH
```

Then point your agent at `SKILL.md` for the full analysis playbook.

## Design principles

- **Project-local only** — everything installs into `.venv/` and `tools/`, nothing goes system-wide
- **`uv` over `pip`** — Python packages managed via uv in a project venv
- **Pre-built binaries** — Go/Ruby tools downloaded as binaries, no compilation needed
- **Bundled where possible** — 6 Python scripts ship with the repo, stdlib-only
- **Usage over installation** — SKILL.md focuses on *what to do*, not *how to install*
