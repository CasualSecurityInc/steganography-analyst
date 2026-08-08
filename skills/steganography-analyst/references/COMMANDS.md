# Command Reference

Detailed usage for each steganography tool. See [SKILL.md](../SKILL.md) for the decision tree.

## Multi-Purpose Tools

### stegoveritas

```bash
stegoveritas image.png                    # full automated analysis → results/
stegoveritas image.png -meta              # metadata only
stegoveritas image.png -imageTransform    # color plane extraction only
stegoveritas image.png -extractLSB        # LSB extraction only
```

### binwalk

```bash
binwalk file.png                          # scan for embedded files
binwalk -e file.png                       # extract known types
binwalk --dd='.*' file.png                # extract everything
binwalk -Me file.png                      # recursive extraction
binwalk -E file.png                       # entropy analysis
```

### foremost

```bash
foremost -i suspicious_file -o output_dir/
foremost -t pdf,jpg,zip -i data.bin -o output/
```

## Image Tools

### zsteg

```bash
zsteg image.png                           # auto-detect all LSB patterns
zsteg image.png -a                        # try all known methods
zsteg image.png -b 1                      # bit plane 1
zsteg image.png -E "b1,rgb,lsb,xy"       # specific extraction pattern
zsteg image.png -E "b1,r,lsb,xy"         # red channel only
zsteg image.png -E "b2,bgr,msb,yx"       # MSB, BGR order
zsteg image.png -E "b1,rgb,lsb,xy" > extracted.bin
```

### bit_plane_extract.py

CLI replacement for StegSolve (no Java required).

```bash
python3 scripts/bit_plane_extract.py image.png --list              # all planes with stats
python3 scripts/bit_plane_extract.py image.png --plane r0          # red LSB
python3 scripts/bit_plane_extract.py image.png --plane g7          # green MSB
python3 scripts/bit_plane_extract.py image.png --channel r --all   # all 8 red planes
python3 scripts/bit_plane_extract.py image.png --composite 0,0,0   # RGB LSB composite
python3 scripts/bit_plane_extract.py image.png --plane r0 --xor g0 # XOR two planes
python3 scripts/bit_plane_extract.py image.png --reorder bgr       # swap channels
python3 scripts/bit_plane_extract.py image.png --lsb-half r        # lower 4 bits
python3 scripts/bit_plane_extract.py image.png --msb-half g        # upper 4 bits
```

### steghide

```bash
steghide info image.jpg                   # check if data is embedded
steghide extract -sf image.jpg            # extract (no password)
steghide extract -sf image.jpg -p "pass"  # extract with password
steghide embed -cf cover.jpg -ef secret.txt -p "pass"  # embed (testing)
```

### stegseek

```bash
stegseek --seed image.jpg                 # detect steghide data (no wordlist needed)
stegseek image.jpg /path/to/wordlist.txt  # crack passphrase (ask operator for wordlist path)
```

### jsteg

```bash
jsteg reveal image.jpg                    # extract hidden data
jsteg hide cover.jpg secret.txt out.jpg   # embed (testing)
```

### pngcheck

```bash
pngcheck -v image.png                     # validate + chunk info
pngcheck -t image.png                     # show text chunks
pngcheck -vtp7f image.png                 # full verbose
```

### exiftool

```bash
exiftool image.jpg                        # all metadata
exiftool -Comment image.jpg               # specific field
exiftool -b -ThumbnailImage image.jpg > thumb.jpg  # extract thumbnail
exiftool -v3 image.jpg                    # verbose structure
exiftool -all= image.jpg                  # strip all metadata
```

### png_crc_fix.py

```bash
python3 scripts/png_crc_fix.py image.png  # brute-force correct dimensions
```

## Audio Tools

### sox (spectrogram)

```bash
sox audio.wav -n spectrogram -o spectro.png
```

### multimon-ng

```bash
multimon-ng -t wav -a DTMF audio.wav                  # DTMF decode
multimon-ng -t wav -a DTMF -a MORSE_CW audio.wav      # multiple decoders
sox audio.wav -t raw -r 22050 -e signed -b 16 -c 1 - | multimon-ng -t raw -
```

### wavsteg.py

```bash
python3 scripts/wavsteg.py -i audio.wav -o out.txt -n 1       # 1 LSB
python3 scripts/wavsteg.py -i audio.wav -o out.txt -n 2       # 2 LSBs
python3 scripts/wavsteg.py -i audio.wav -o out.bin -n 1 -m 1024  # max bytes
```

### wav_header_check.py

```bash
python3 scripts/wav_header_check.py audio.wav
```

## Text Tools

### stegsnow

```bash
stegsnow -C message.txt                   # extract hidden message
stegsnow -C -p "password" message.txt     # extract with password
stegsnow -C -m "hidden" -p "pass" cover.txt stego.txt  # embed (testing)
```

### zero_width_decode.py

```bash
python3 scripts/zero_width_decode.py message.txt          # decode and print
python3 scripts/zero_width_decode.py message.txt --raw    # hex output
python3 scripts/zero_width_decode.py message.txt -o out.bin
```

### homoglyph_detect.py

```bash
python3 scripts/homoglyph_detect.py message.txt
python3 scripts/homoglyph_detect.py message.txt --context 20  # wider context
```
