---
name: stego-tools-guide
description: >-
  Steganography tool reference — setup, usage patterns, and command reference for image, audio, file, and text stego analysis.
---

# STEGANOGRAPHY TOOLS GUIDE

> Supplementary reference for [SKILL.md](./SKILL.md). Setup and usage for each tool.

---

## 1. QUICK SETUP

```bash
./setup.sh
source tools/env.sh
```

This installs everything project-locally into `.venv/` and `tools/`. No sudo, no system-wide changes.

What gets installed:
- **Python tools** (stegoveritas, binwalk) → `.venv/`
- **jsteg** binary → `tools/bin/`
- **StegSolve** JAR → `tools/lib/`
- **zsteg** gem → `~/.gem/ruby/` (user-local)
- **Bundled scripts** → `tools/*.py` (already present, no install needed)

System tools (exiftool, pngcheck, foremost, steghide, stegsnow, multimon-ng) are checked and brew install hints are printed if missing.

---

## 2. MULTI-PURPOSE TOOLS

### stegoveritas

Automated steganography analysis — runs multiple tools in one pass.

```bash
# Full automated analysis
stegoveritas image.png
# Runs: exiftool, binwalk, zsteg, foremost, trailing data check
# Output: results/ directory with all findings

stegoveritas image.png -meta         # metadata only
stegoveritas image.png -imageTransform   # color plane extraction only
stegoveritas image.png -extractLSB   # LSB extraction only
```

### binwalk

Firmware/file analysis and extraction.

```bash
# Scan for embedded files
binwalk file.png

# Extract embedded files
binwalk -e file.png                  # extract known types
binwalk --dd='.*' file.png           # extract everything
binwalk -Me file.png                 # recursive extraction

# Entropy analysis (detect encrypted/compressed regions)
binwalk -E file.png
```

### foremost

File carving tool — recovers files from raw data.

```bash
# Carve files
foremost -i suspicious_file -o output_dir/
foremost -t all -i disk_image.raw -o carved/

# Specific file types
foremost -t pdf,jpg,zip -i data.bin -o output/
```

---

## 3. IMAGE TOOLS

### zsteg

PNG/BMP LSB steganography detector.

```bash
# Auto-detect all LSB patterns
zsteg image.png

# Verbose scan with all methods
zsteg image.png -a

# Specific extraction
zsteg image.png -b 1                        # bit plane 1
zsteg image.png -E "b1,rgb,lsb,xy"          # specific pattern
zsteg image.png -E "b1,r,lsb,xy"            # red channel only
zsteg image.png -E "b2,bgr,msb,yx"          # MSB, BGR order

# Extract to file
zsteg image.png -E "b1,rgb,lsb,xy" > extracted.bin
```

### Bit Plane Extract (bundled)

CLI replacement for StegSolve's core functionality. No Java required.

```bash
# List all bit planes with pixel statistics
python3 tools/bit_plane_extract.py image.png --list

# Extract single bit plane
python3 tools/bit_plane_extract.py image.png --plane r0      # red LSB
python3 tools/bit_plane_extract.py image.png --plane g7      # green MSB
python3 tools/bit_plane_extract.py image.png --plane b3      # blue bit 3

# Extract all 8 bit planes of a channel
python3 tools/bit_plane_extract.py image.png --channel r --all
python3 tools/bit_plane_extract.py image.png --channel g --all --dir output/

# RGB composite from individual bit planes
python3 tools/bit_plane_extract.py image.png --composite 0,0,0   # all LSBs
python3 tools/bit_plane_extract.py image.png --composite 7,7,7   # all MSBs

# XOR/AND/OR between two bit planes
python3 tools/bit_plane_extract.py image.png --plane r0 --xor g0
python3 tools/bit_plane_extract.py image.png --plane r0 --and b0

# Swap color channels
python3 tools/bit_plane_extract.py image.png --reorder bgr

# Extract lower/upper 4 bits
python3 tools/bit_plane_extract.py image.png --lsb-half r
python3 tools/bit_plane_extract.py image.png --msb-half g
```

### StegSolve (optional, requires Java)

Java GUI for visual bit plane analysis. Download from `Giotino/stegsolve` on GitHub.

```bash
java -jar tools/lib/StegSolve.jar
# Arrow keys: cycle through color planes (R0-R7, G0-G7, B0-B7, Alpha)
# Analyse → Data Extract: specify bit planes to extract
```

### steghide

JPEG/WAV/BMP/AU steganography with encryption.

```bash
# Check if data is embedded
steghide info image.jpg

# Extract (no password)
steghide extract -sf image.jpg

# Extract with password
steghide extract -sf image.jpg -p "password"

# Embed data (for testing)
steghide embed -cf cover.jpg -ef secret.txt -p "password"
```

### stegseek

Fast steghide passphrase cracker (~10000x faster than stegcracker).

```bash
# Crack passphrase
stegseek image.jpg wordlist.txt

# Seed crack (try without wordlist)
stegseek --seed image.jpg
```

### jsteg

JPEG LSB steganography.

```bash
# Extract
jsteg reveal image.jpg

# Embed (for testing)
jsteg hide cover.jpg secret.txt output.jpg
```

### pngcheck

PNG structure validator.

```bash
# Validate and show chunk info
pngcheck -v image.png

# Show text chunks
pngcheck -t image.png

# Full verbose with data
pngcheck -vtp7f image.png
```

### exiftool

Metadata extraction and manipulation.

```bash
# All metadata
exiftool image.jpg

# Specific fields
exiftool -Comment image.jpg
exiftool -UserComment image.jpg
exiftool -GPSLatitude -GPSLongitude image.jpg

# Extract thumbnail
exiftool -b -ThumbnailImage image.jpg > thumbnail.jpg

# Verbose structure
exiftool -v3 image.jpg

# Strip all metadata
exiftool -all= image.jpg
```

### PNG CRC Dimension Fix

```bash
# Brute-force correct dimensions when CRC doesn't match declared size
python3 tools/png_crc_fix.py image.png
```

---

## 4. AUDIO TOOLS

### Sonic Visualiser

Best spectrogram viewer for stego analysis. Install via `brew install sonic-visualiser`.

```
1. Open audio file
2. Layer → Add Spectrogram
3. Adjust: Window=4096, Overlap=87.5%, Scale=dBV
4. Look for patterns (text, QR codes, images in frequency domain)
```

### sox

Command-line spectrogram generation.

```bash
sox audio.wav -n spectrogram -o spectro.png
```

### multimon-ng

Decoder for DTMF, POCSAG, and other digital modes.

```bash
# DTMF decode
multimon-ng -t wav -a DTMF audio.wav

# Multiple decoders
multimon-ng -t wav -a DTMF -a MORSE_CW audio.wav

# From raw audio input
sox audio.wav -t raw -r 22050 -e signed -b 16 -c 1 - | multimon-ng -t raw -
```

### WavSteg (bundled)

LSB extraction from WAV files.

```bash
python3 tools/wavsteg.py -i audio.wav -o output.txt -n 1   # 1 LSB
python3 tools/wavsteg.py -i audio.wav -o output.txt -n 2   # 2 LSBs
python3 tools/wavsteg.py -i audio.wav -o output.bin -n 1 -m 1024  # max 1024 bytes
```

### WAV Header Check (bundled)

```bash
python3 tools/wav_header_check.py audio.wav
```

---

## 5. TEXT TOOLS

### stegsnow

Whitespace steganography in text files.

```bash
# Extract hidden message
stegsnow -C message.txt

# Extract with password
stegsnow -C -p "password" message.txt

# Embed (for testing)
stegsnow -C -m "hidden message" -p "password" cover.txt stego.txt
```

### Zero-Width Decoder (bundled)

```bash
python3 tools/zero_width_decode.py message.txt
python3 tools/zero_width_decode.py message.txt --raw       # hex output
python3 tools/zero_width_decode.py message.txt -o out.bin  # write to file
```

### Homoglyph Detector (bundled)

```bash
python3 tools/homoglyph_detect.py message.txt
```

---

## 6. ANALYSIS WORKFLOWS

### Quick Triage (Any File)

```bash
file suspicious_file
exiftool suspicious_file
strings -n 8 suspicious_file | head -50
binwalk suspicious_file
xxd suspicious_file | head -20
```

### Image Deep Analysis

```bash
exiftool -v3 image.*
pngcheck -v image.png         # if PNG
steghide info image.jpg       # if JPEG
zsteg -a image.png            # if PNG/BMP
stegoveritas image.*          # comprehensive automated scan
binwalk -e image.*            # embedded file extraction
```

### Audio Deep Analysis

```bash
exiftool audio.*
file audio.*
sox audio.wav -n spectrogram -o spectro.png
multimon-ng -t wav -a DTMF audio.wav
python3 tools/wav_header_check.py audio.wav
```

### Password Recovery for Steghide

```bash
# Fast: stegseek
stegseek image.jpg wordlist.txt

# Manual: try common passwords
for p in password flag secret admin test ""; do
    steghide extract -sf image.jpg -p "$p" 2>/dev/null && echo "Password: '$p'" && break
done
```

---

## 7. MANUAL INSTALLATION (FALLBACK)

If `setup.sh` fails or you need to install tools individually:

### Python tools (requires `uv`)

```bash
uv venv .venv
source .venv/bin/activate
uv pip install stegoveritas binwalk
```

### zsteg (requires Ruby)

```bash
gem install --user-install zsteg
```

### jsteg (pre-built binary)

Download from https://github.com/lukechampine/jsteg/releases — pick your platform (`darwin-arm64`, `darwin-amd64`, `linux-amd64`, `linux-arm64`).

### StegSolve (Java JAR)

Download from https://github.com/Giotino/stegsolve/releases/tag/v1.4 — place in `tools/lib/StegSolve.jar`. Requires Java runtime.

### stegseek

- **macOS**: `brew install stegseek`
- **Linux**: Download `.deb` from https://github.com/RickdeJager/stegseek/releases and extract the binary

### System tools (macOS)

```bash
brew install exiftool pngcheck foremost steghide stegsnow multimon-ng
```
