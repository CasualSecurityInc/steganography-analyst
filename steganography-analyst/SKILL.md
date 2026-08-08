---
name: steganography-analyst
description: >-
  Steganography detection and extraction for images (LSB, PNG chunks, JPEG DCT, EXIF, palette), audio (spectrogram, DTMF, WAV LSB), files (polyglots, binwalk, ADS), and text (whitespace, zero-width Unicode, homoglyphs). Use when analyzing suspicious files for hidden data in CTF challenges, digital forensics, or security research.
license: MIT
compatibility: Requires Python 3.10+ and uv. Some tools require Ruby (zsteg) or brew (exiftool, steghide).
metadata:
  version: "1.0"
---

# Steganography Analysis Skill

Detect and extract hidden data from images, audio, files, and text.

## Setup

```bash
./setup.sh          # installs all tools project-locally (no sudo)
source scripts/env.sh
```

See [SETUP.md](references/SETUP.md) for manual installation fallback.

## Decision Tree

What file type are you analyzing?

### Image (PNG/BMP)

1. `exiftool image.png` — check metadata for hidden fields
2. `pngcheck -v image.png` — validate structure, find hidden chunks
3. `zsteg -a image.png` — LSB pattern detection
4. `python3 scripts/bit_plane_extract.py image.png --list` — bit plane statistics
5. `python3 scripts/png_crc_fix.py image.png` — dimension/CRC mismatch
6. `binwalk -e image.png` — embedded file extraction
7. `unzip image.png -d out/` — try as polyglot

### Image (JPEG)

1. `exiftool -v3 image.jpg` — verbose metadata + structure
2. `steghide extract -sf image.jpg` — DCT coefficient extraction
3. `jsteg reveal image.jpg` — JPEG LSB
4. `binwalk -e image.jpg` — embedded data
5. If password-protected: `stegseek image.jpg wordlist.txt`

### Image (GIF)

1. Extract animation frames — look for hidden content in individual frames
2. `gifsicle --color-info image.gif` — palette manipulation check
3. `binwalk -e image.gif` — appended data

### Audio (WAV/MP3/FLAC)

1. `sox audio.wav -n spectrogram -o spectro.png` — visual patterns in frequency domain
2. `python3 scripts/wavsteg.py -i audio.wav -o out.txt -n 1` — LSB extraction
3. `python3 scripts/wav_header_check.py audio.wav` — appended data after audio
4. `multimon-ng -t wav -a DTMF audio.wav` — DTMF phone tones

### Text File

1. `cat -A file.txt | head` — whitespace patterns (tabs/spaces encoding)
2. `python3 scripts/zero_width_decode.py file.txt` — zero-width Unicode
3. `python3 scripts/homoglyph_detect.py file.txt` — lookalike character substitution
4. `stegsnow -C file.txt` — snow whitespace steganography

### Any File Type (First Pass)

```bash
file suspicious_file                    # true file type
strings -n 8 suspicious_file | head     # readable strings
binwalk suspicious_file                 # embedded file signatures
xxd suspicious_file | head -20          # magic bytes
```

### Password Needed?

- `stegseek image.jpg wordlist.txt` — fast steghide cracker (Linux; on macOS: `docker run --rm -it -v "$(pwd):/steg" rickdejager/stegseek`)
- `stegseek --seed image.jpg` — detect steghide data without wordlist
- Try common passwords: `password`, `flag`, `secret`, the filename, challenge name

## Bundled Scripts

All in `scripts/`, stdlib-only (except `bit_plane_extract.py` which needs Pillow+numpy):

| Script | Use when |
|--------|----------|
| `bit_plane_extract.py` | Visual bit plane analysis (StegSolve replacement) |
| `png_crc_fix.py` | PNG dimensions don't match CRC — brute-force correct size |
| `wavsteg.py` | Data hidden in WAV audio LSBs |
| `wav_header_check.py` | Extra data appended after WAV content |
| `zero_width_decode.py` | Invisible Unicode characters encoding data |
| `homoglyph_detect.py` | Cyrillic/Latin or other lookalike character swaps |

## External Tools

Installed project-locally by `setup.sh`. See [COMMANDS.md](references/COMMANDS.md) for full usage.

| Tool | What it does |
|------|-------------|
| zsteg | PNG/BMP LSB pattern detection |
| stegoveritas | Automated multi-tool analysis pass |
| binwalk | Embedded file extraction + entropy analysis |
| steghide | JPEG/WAV/BMP DCT steganography |
| stegseek | Fast steghide passphrase cracker (Linux binary; macOS via Docker) |
| jsteg | JPEG LSB extraction |
| exiftool | Metadata extraction and manipulation |
| pngcheck | PNG structure validation |
| foremost | File carving from raw data |
| stegsnow | Whitespace steganography |

## Common Failure Modes

- **zsteg returns noise**: Try `--all` and look for patterns with high confidence scores, not raw output
- **steghide says "could not extract"**: File may not contain steghide data, or wrong passphrase — try stegseek
- **binwalk finds nothing**: File may use LSB/visual stego, not embedded files — try zsteg or bit_plane_extract
- **StegSolve won't start**: Requires Java. Use `python3 scripts/bit_plane_extract.py` as a CLI alternative
- **Zero-width decoder returns empty**: File may use homoglyphs or whitespace encoding instead — try both detectors
