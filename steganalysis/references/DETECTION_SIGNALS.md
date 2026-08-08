# Detection Signals Catalog

A reference catalog of specific signals that indicate hidden data, organized by file type. Use this when you need to match an observation to a likely steganographic technique.

## Image Signals

### File-Level Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| `file` says image but `unzip` succeeds | Polyglot (image+ZIP) | `unzip` or `7z x` to extract |
| Size doesn't match declared dimensions × color depth | Appended data or dimension tampering | `binwalk`, `pngcheck`, `png_crc_fix.py` |
| Multiple image signatures found by binwalk | Embedded/concatenated images | `binwalk -e` |
| PNG has non-standard chunks (not IHDR/PLTE/IDAT/IEND) | Hidden data in custom chunks | `pngcheck -v`, extract chunk data |
| JPEG data after EOI marker (0xFFD9) | Appended content | `dd` or `binwalk` from offset |
| EXIF thumbnail differs from main image | Pre-modification thumbnail preserved | `exiftool -b -ThumbnailImage` |
| Alpha channel present in format that shouldn't have it | Data in transparency | Extract alpha channel separately |

### Pixel-Level Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| LSB plane looks random (not correlated with image) | LSB steganography | `zsteg -a`, `bit_plane_extract.py` |
| On/off pixel ratio near 0.5 in lower bit planes | Random data embedded | Check if this matches expected image statistics |
| Color channel decorrelation (XOR between channels shows noise) | Channel-specific LSB | Extract individual channels |
| Visible grain/noise in smooth color regions | LSB modification | Compare with expected smoothness |
| Unusual color palette ordering in GIF | Data in palette structure | `gifsicle --color-info` |

### Metadata Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| EXIF Comment/UserComment field populated | Hidden text in metadata | `exiftool -Comment` |
| Artist/Copyright/Description fields with encoded data | Text stego in metadata | Decode the field content |
| Software tag says "steghide" or similar | Known tool used | Try the indicated tool |
| GPS coordinates that don't match the image content | Misdirection or encoded data | Decode GPS values |
| Timestamp inconsistencies (creation < modification) | File was modified after creation | Check what changed |

## Audio Signals

### File-Level Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| File size ≠ expected (frames × channels × sample_size + header) | Appended data | `wav_header_check.py` |
| Non-standard WAV chunks | Hidden data in chunks | Hex inspection of chunk data |
| MP3 with embedded ID3 tag larger than expected | Data in ID3 | Extract ID3 content |
| Audio file also recognized as another format | Polyglot | Try opening as the other format |

### Content-Level Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| Spectrogram shows visual patterns (text, shapes, QR) | Visual steganography | Open in Sonic Visualiser, screenshot |
| Regular on/off pattern in waveform | Morse code or binary encoding | Visual inspection, multimon-ng |
| DTMF tones in audio | Phone number or message encoding | `multimon-ng -t wav -a DTMF` |
| Unnatural silence gaps | On/off keying (binary encoding) | Measure gap durations |
| Frequency bands with unnatural patterns | LSB or spread spectrum in frequency domain | Spectrogram analysis at different FFT sizes |

## Text Signals

### Character-Level Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| Invisible characters (zero-width spaces, etc.) | Unicode steganography | `zero_width_decode.py` |
| Characters that look identical but have different codepoints | Homoglyph substitution | `homoglyph_detect.py` |
| Mixed tabs and spaces with no formatting purpose | Whitespace binary encoding | `cat -A`, `stegsnow -C` |
| Trailing whitespace on lines | Whitespace encoding | Hex inspection |
| Base64-like strings embedded in text | Encoded payload | Decode the base64 |

### Structural Signals

| Signal | Likely technique | Next step |
|--------|-----------------|-----------|
| Lines with consistent but unusual length | Binary encoding via line structure | Analyze line lengths |
| First/last character of each line spells something | Acrostic / edge encoding | Extract first/last chars |
| Text file much larger than visible content suggests | Hidden content (zero-width, whitespace) | Compare byte count to visible character count |
| Unusual Unicode categories (Cf, Cc) in "normal" text | Control/format characters hiding data | `homoglyph_detect.py` |

## Any File Type — Universal Signals

| Signal | What it means |
|--------|--------------|
| `strings -n 8` finds flag/key/password patterns | Direct hidden text — extract it |
| `xxd` shows magic bytes for a different format | Wrong extension or polyglot |
| Entropy plot (`binwalk -E`) has flat-line region | Encrypted/compressed embedded data |
| File ends with null bytes or repeated patterns | Padding to conceal appended data |
| Multiple different magic byte signatures | Concatenated files | `binwalk -e`, `foremost` |
| File references other files by name | Embedded content expects companion files |
