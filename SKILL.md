---
name: steganography-techniques
description: >-
  Steganography detection and extraction playbook. Use when analyzing images (LSB, PNG chunks, JPEG DCT, EXIF), audio (spectrogram, DTMF), files (polyglots, appended data, ADS), and text (whitespace, zero-width, homoglyphs) for hidden data.
---

# SKILL: Steganography Techniques — Expert Analysis Playbook

> **AI LOAD INSTRUCTION**: Expert steganography detection and extraction techniques. Covers image steganography (LSB, PNG chunk hiding, JPEG DCT, EXIF metadata, dimension tricks, palette manipulation), audio steganography (spectrogram, LSB, DTMF, morse), file steganography (polyglots, binwalk, NTFS ADS, steghide), and text steganography (whitespace, zero-width Unicode, homoglyphs). Base models miss the systematic file-type-based analysis approach and tool-specific extraction workflows.

## 0. SETUP

Run `./setup.sh` to install all tools project-locally, then `source tools/env.sh`. See `STEGO_TOOLS_GUIDE.md` for detailed tool reference.

### Related Skills

Before going deep, consider:
- PCAP analysis for extracting files from network captures before stego analysis
- Memory forensics for extracting files from memory dumps
- Classical cipher analysis if extracted hidden data is further encrypted/encoded

---

## 1. IMAGE STEGANOGRAPHY

### LSB (Least Significant Bit)

LSB embeds data in the least significant bits of pixel color channels.

```bash
# zsteg — LSB analysis for PNG/BMP
zsteg image.png                       # auto-detect all LSB patterns
zsteg image.png -a                    # try all known methods
zsteg image.png -b 1                  # extract bit plane 1
zsteg image.png -E "b1,rgb,lsb,xy"   # specific extraction pattern

# Bit plane extraction (bundled Python tool — no Java needed)
python3 tools/bit_plane_extract.py image.png --list          # list all planes with stats
python3 tools/bit_plane_extract.py image.png --plane r0      # red channel LSB
python3 tools/bit_plane_extract.py image.png --composite 0,0,0  # RGB LSB composite
python3 tools/bit_plane_extract.py image.png --plane r0 --xor g0  # XOR two planes
python3 tools/bit_plane_extract.py image.png --channel r --all   # all 8 red bit planes

# StegSolve (Java GUI, optional — requires Java runtime)
java -jar tools/lib/StegSolve.jar

# stegoveritas — comprehensive automated analysis
stegoveritas image.png
# Runs: exiftool, binwalk, zsteg, foremost, color plane extraction
```

### PNG Specific

```bash
# pngcheck — validate structure, find hidden chunks
pngcheck -v image.png

# Hidden chunks: tEXt, zTXt (compressed text), iTXt (international text)
# Custom/private chunks may contain hidden data

# CRC vs dimensions trick
# If CRC doesn't match declared dimensions → image was cropped
# Fix: brute-force correct width/height → reveals hidden rows/columns
python3 tools/png_crc_fix.py image.png

# APNG (animated PNG) — hidden frames
# Use apngdis to extract all frames: apngdis image.png
```

### JPEG Specific

```bash
# steghide — embed/extract from JPEG (DCT coefficient modification)
steghide extract -sf image.jpg                 # extract (no passphrase)
steghide extract -sf image.jpg -p PASSWORD     # extract with passphrase
steghide info image.jpg                        # check if data is embedded

# stegseek — brute force steghide passphrase (fast)
stegseek image.jpg wordlist.txt

# jsteg — JPEG LSB steganography
jsteg reveal image.jpg output.txt

# JPEG structure analysis
exiftool -v3 image.jpg       # verbose metadata + structure
```

### EXIF Metadata

```bash
# exiftool — comprehensive metadata extraction
exiftool image.jpg
exiftool -b -ThumbnailImage image.jpg > thumb.jpg   # extract thumbnail
exiftool -all= image.jpg                             # strip all metadata

# Hidden data in EXIF fields (comment, artist, copyright, etc.)
exiftool -Comment image.jpg
exiftool -UserComment image.jpg
strings image.jpg | grep -i "flag\|key\|secret"
```

### Palette-Based (GIF)

```bash
# GIF color table manipulation — data in color palette order
gifsicle -I image.gif                    # info
gifsicle --color-info image.gif          # palette details
# Check for animation frames: convert -coalesce image.gif frame_%d.png
```

---

## 2. AUDIO STEGANOGRAPHY

### Spectrogram Analysis

```bash
# Sonic Visualiser — best for spectrogram viewing (GUI)
# Layer → Add Spectrogram → look for visual patterns (text/images)

# Audacity — Analyze → Plot Spectrum, or view as Spectrogram

# sox for command-line spectrogram generation
sox audio.wav -n spectrogram -o spectro.png
```

### Audio LSB

```bash
# Bundled WavSteg — LSB in WAV files
python3 tools/wavsteg.py -i audio.wav -o output.txt -n 1   # extract 1 LSB
python3 tools/wavsteg.py -i audio.wav -o output.txt -n 2   # extract 2 LSBs
```

### DTMF / Morse Code

```bash
# DTMF decoder (phone tones)
multimon-ng -t wav -a DTMF audio.wav

# Morse code
# Audacity → visual inspection of on/off pattern
# Online decoder or manual: .- = A, -... = B, etc.

# SSTV (Slow-Scan Television) — image in audio
qsstv                    # GUI decoder
```

### WAV Header Manipulation

```bash
# Check for data appended after WAV audio data
python3 tools/wav_header_check.py audio.wav
```

---

## 3. FILE STEGANOGRAPHY

### Polyglot Files

A single file that is valid in two or more formats simultaneously.

```bash
# Detection: check file with multiple tools
file suspicious_file
xxd suspicious_file | head          # check magic bytes
binwalk suspicious_file             # find embedded files

# Common polyglots: PDF+ZIP, JPEG+ZIP, JPEG+RAR, PNG+ZIP
# Try unzip on image files:
unzip image.jpg -d extracted/
7z x image.jpg -oextracted/
```

### Appended / Embedded Data

```bash
# binwalk — scan for embedded files and data
binwalk image.png                   # scan
binwalk -e image.png                # extract embedded files
binwalk --dd='.*' image.png         # extract everything

# foremost — file carving
foremost -i suspicious_file -o output_dir/

# dd — manual extraction
# If binwalk shows embedded ZIP at offset 0x1234:
dd if=suspicious_file bs=1 skip=$((0x1234)) of=extracted.zip
```

### NTFS Alternate Data Streams (ADS)

```cmd
:: List ADS (Windows)
dir /r file.txt
Get-Item file.txt -Stream *

:: Read hidden stream
more < file.txt:hidden_stream
Get-Content file.txt -Stream hidden_stream
```

### Steghide Brute Force

```bash
# stegseek — fast passphrase cracker
stegseek image.jpg wordlist.txt

# Manual: try common passwords
for p in password flag secret admin test ""; do
    steghide extract -sf image.jpg -p "$p" 2>/dev/null && echo "Password: '$p'" && break
done
```

---

## 4. TEXT STEGANOGRAPHY

### Whitespace Encoding

```bash
# Tabs and spaces encode binary (tab=1, space=0 or vice versa)
# stegsnow — whitespace steganography
stegsnow -C message.txt                # extract hidden message
stegsnow -C -p PASSWORD message.txt    # extract with password

# Manual detection:
cat -A file.txt | head     # show tabs (^I) and line endings ($)
xxd file.txt | grep "09 20\|20 09"    # look for tab/space patterns
```

### Zero-Width Characters

```bash
# Unicode invisible characters used for encoding:
# U+200B (Zero-Width Space), U+200C (ZWNJ), U+200D (ZWJ), U+FEFF (BOM)

# Bundled decoder
python3 tools/zero_width_decode.py message.txt
python3 tools/zero_width_decode.py message.txt --raw       # hex output
python3 tools/zero_width_decode.py message.txt -o out.bin  # write to file
```

### Homoglyph Substitution

```bash
# Visually identical characters from different Unicode blocks
# e.g., Latin 'a' (U+0061) vs Cyrillic 'а' (U+0430)

# Bundled detector
python3 tools/homoglyph_detect.py message.txt
```

---

## 5. DECISION TREE

```
Suspect hidden data — what file type?
│
├── Image (PNG/BMP)?
│   ├── Check metadata: exiftool
│   ├── Check structure: pngcheck, binwalk
│   ├── LSB analysis: zsteg, bit_plane_extract.py
│   ├── Check dimensions vs CRC: python3 tools/png_crc_fix.py
│   ├── Check for appended data: binwalk -e
│   └── Try as polyglot: unzip/7z
│
├── Image (JPEG)?
│   ├── Check metadata: exiftool
│   ├── Try steghide: steghide extract
│   │   └── Password protected? → stegseek brute force
│   ├── Try jsteg: jsteg reveal
│   ├── Check for appended data: binwalk -e
│   └── Check thumbnail: exiftool -b -ThumbnailImage
│
├── Image (GIF)?
│   ├── Check frames: extract all animation frames
│   ├── Check palette: gifsicle --color-info
│   └── Check for appended data: binwalk -e
│
├── Audio (WAV/MP3/FLAC)?
│   ├── Spectrogram: Sonic Visualiser / Audacity / sox
│   ├── LSB: python3 tools/wavsteg.py
│   ├── DTMF tones: multimon-ng
│   ├── Morse code: manual or decoder
│   ├── SSTV: qsstv
│   └── Check file size vs expected: python3 tools/wav_header_check.py
│
├── Text file?
│   ├── Check whitespace: cat -A, stegsnow
│   ├── Check zero-width chars: python3 tools/zero_width_decode.py
│   ├── Check homoglyphs: python3 tools/homoglyph_detect.py
│   └── Check encoding: multiple base decodings
│
├── Any file type?
│   ├── strings: strings -n 8 file | grep -i "flag\|key\|pass"
│   ├── binwalk: binwalk -e file (embedded files)
│   ├── file: file suspicious_file (true type)
│   ├── xxd: check magic bytes, compare headers
│   └── NTFS? → check ADS: dir /r
│
└── Password/passphrase needed?
    ├── steghide → stegseek brute force
    ├── Check challenge description for hints
    └── Try common passwords: password, file name, challenge name
```
