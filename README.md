# steganography-analyst

[![skills.sh](https://skills.sh/b/CasualSecurityInc/steganography-analyst)](https://skills.sh/CasualSecurityInc/steganography-analyst)

An AI agent skill for steganography detection and extraction. Provides a structured decision tree and toolchain for analyzing images, audio, files, and text for hidden data — designed for CTF challenges, digital forensics, and security research.

## Quick start

```bash
./setup.sh                              # install everything project-locally (no sudo)
source steganography-analyst/scripts/env.sh  # add tools to PATH
```

Then point your agent at `steganography-analyst/SKILL.md`.

## Installation

```bash
npx skills add CasualSecurityInc/steganography-analyst
```

Or install from a specific path inside the repo:

```bash
npx skills add https://github.com/CasualSecurityInc/steganography-analyst/tree/main/steganography-analyst
```

## Skill structure

```
steganography-analyst/
├── SKILL.md                    # Decision tree + when-to-use (< 500 lines)
├── scripts/                    # Executable tools
│   ├── bit_plane_extract.py    # Bit plane analysis (StegSolve replacement)
│   ├── png_crc_fix.py          # PNG dimension brute-forcer
│   ├── wavsteg.py              # WAV LSB extraction
│   ├── wav_header_check.py     # WAV appended data detector
│   ├── zero_width_decode.py    # Zero-width Unicode decoder
│   └── homoglyph_detect.py     # Lookalike character detector
└── references/                 # On-demand detail
    ├── COMMANDS.md             # Full per-tool command reference
    ├── SETUP.md                # Manual installation fallback
    └── WORKFLOWS.md            # Step-by-step analysis procedures
```

## Techniques covered

- **Image**: LSB analysis, PNG chunk inspection, JPEG DCT, EXIF metadata, palette manipulation, dimension/CRC tricks, bit plane visualization
- **Audio**: Spectrogram analysis, WAV LSB, DTMF decoding, SSTV, appended data detection
- **File**: Polyglot detection, embedded file carving, NTFS alternate data streams
- **Text**: Whitespace encoding, zero-width Unicode steganography, homoglyph substitution

## External tools (installed by setup.sh)

| Tool | Install method |
|------|---------------|
| [stegoveritas](https://github.com/bannsec/stegoveritas) | `uv pip install` |
| [binwalk](https://github.com/ReFirmLabs/binwalk) | `uv pip install` |
| [zsteg](https://github.com/zed-0xff/zsteg) | `gem install --user-install` |
| [jsteg](https://github.com/lukechampine/jsteg) | Pre-built binary |
| [stegseek](https://github.com/RickdeJager/stegseek) | Binary (Linux) / brew (macOS) |
| [StegSolve](https://github.com/Giotino/stegsolve) | JAR download (optional, needs Java) |

## Design principles

- **Project-local only** — everything installs into `.venv/` and `scripts/`, nothing goes system-wide
- **Progressive disclosure** — SKILL.md is the entry point, references load on demand
- **`uv` over `pip`** — Python packages managed via uv in a project venv
- **Pre-built binaries** — Go/Ruby tools downloaded as binaries, no compilation needed
- **Bundled where possible** — 6 Python scripts ship with the repo, stdlib-only
