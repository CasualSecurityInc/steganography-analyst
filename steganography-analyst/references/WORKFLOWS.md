# Analysis Workflows

Step-by-step procedures for common stego analysis scenarios. See [SKILL.md](../SKILL.md) for the decision tree.

## Quick Triage (Any File)

```bash
file suspicious_file
exiftool suspicious_file
strings -n 8 suspicious_file | head -50
binwalk suspicious_file
xxd suspicious_file | head -20
```

## Image Deep Analysis

```bash
exiftool -v3 image.*
pngcheck -v image.png         # if PNG
steghide info image.jpg       # if JPEG
zsteg -a image.png            # if PNG/BMP
stegoveritas image.*          # comprehensive automated scan
binwalk -e image.*            # embedded file extraction
python3 scripts/bit_plane_extract.py image.png --list  # bit plane statistics
```

## Audio Deep Analysis

```bash
exiftool audio.*
file audio.*
sox audio.wav -n spectrogram -o spectro.png
multimon-ng -t wav -a DTMF audio.wav
python3 scripts/wav_header_check.py audio.wav
python3 scripts/wavsteg.py -i audio.wav -o out.txt -n 1
```

## Password Recovery for Steghide

```bash
# Fast: stegseek
stegseek image.jpg wordlist.txt

# Manual: try common passwords
for p in password flag secret admin test ""; do
    steghide extract -sf image.jpg -p "$p" 2>/dev/null && echo "Password: '$p'" && break
done
```

## PNG Dimension Tampering

When `pngcheck` reports CRC mismatch or the image looks truncated:

```bash
python3 scripts/png_crc_fix.py image.png
# Output: Valid dimensions: WxH
# Then use an image editor or Python to resize/reveal hidden content
```

## Zero-Width Unicode Stego

When text looks normal but may contain invisible characters:

```bash
python3 scripts/zero_width_decode.py message.txt
python3 scripts/zero_width_decode.py message.txt --raw    # if binary data
```

## Polyglot File Detection

When a file works as multiple formats simultaneously:

```bash
file suspicious.jpg               # check declared type
unzip -l suspicious.jpg           # is it also a ZIP?
7z l suspicious.jpg               # or a 7z/RAR?
binwalk -e suspicious.jpg         # extract embedded content
```
