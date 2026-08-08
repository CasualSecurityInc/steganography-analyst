---
name: steganalysis
description: >-
  Detection-first tactics for finding hidden data in images, audio, files, and text. Use when you need to determine WHETHER something is hidden, WHERE to look, and WHAT signals indicate steganographic content — before attempting extraction. Covers contextual analysis, structural anomalies, statistical tells, and modern AI-based steganography detection.
license: MIT
compatibility: Works alongside steganography-analyst for extraction. No tools required — this skill is about reasoning and observation.
metadata:
  version: "1.0"
---

# Steganalysis — Detection Tactics

How to determine whether hidden data exists, where to look, and what signals to trust. This skill complements steganography-analyst (which handles extraction).

## Core Principle

Steganalysis is observation-first. Before running any tool, ask: **what about this file is unusual, inconsistent, or suspicious?** The answer guides which extraction techniques to try.

## 1. Contextual Signals

The richest detection channel is often not the file itself but its context.

### Challenge / Source Metadata

- **Challenge descriptions** frequently encode hints: "the answer is in the red," "look deeper than the surface," "not everything is as it appears"
- **File names** may be literal: `hidden.png`, `secret.wav`, `challenge_not_what_you_think.txt`
- **File provenance**: Where did this come from? A "screenshot" that's 2MB is suspicious. A "photo" that's 300KB with no EXIF camera data is suspicious.
- **Multiple files in a challenge**: One may be the key/password for another. Look for relationships.

### Size Anomalies

A file's size relative to its content is a strong signal:

| Observation | What it might mean |
|-------------|-------------------|
| PNG/BMP much larger than visual complexity suggests | LSB payload, appended data, or hidden chunks |
| JPEG oddly large for its resolution | Embedded files, EXIF bloat, or DCT steganography |
| Audio file much larger than expected duration | Appended data after audio content |
| Text file larger than its visible content | Zero-width characters, whitespace encoding |
| File size not a round number / doesn't match format norms | Trailing data appended after format end marker |

### Behavioral Signals

- A file that "works" as two different formats (open as image, also `unzip` succeeds) — **polyglot**
- A file that crashes some viewers but not others — format manipulation
- Metadata that contradicts the file content (EXIF says "Photoshop" but the challenge says "raw screenshot")

## 2. Visual / Structural Anomalies

### Images — What to Notice

**Without any tools:**
- Unusual color banding or noise patterns in specific bit planes — LSB stego often creates subtle grain
- Image looks "normal" but has a suspiciously large file size
- Thumbnail doesn't match the full image (EXIF thumbnail may predate stego modification)
- Transparency (alpha channel) in a format that shouldn't need it — data may be in the alpha

**PNG-specific structural tells:**
- Non-standard chunks (anything beyond IHDR/PLTE/IDAT/IEND) — `pngcheck -v` reveals these
- Dimensions that seem wrong or are "magic numbers" (256x256, 512x512) — may have been cropped to hide rows/columns
- CRC mismatch on IHDR — dimensions were tampered with to conceal content

**JPEG-specific tells:**
- Multiple SOI (Start of Image) markers — embedded JPEG
- Data after the EOI (End of Image) marker — appended content
- Thumbnail in EXIF that shows different content than the main image

### Audio — What to Notice

- Spectrogram shows visual patterns (text, QR codes, images) — **visual steganography in frequency domain**
- Unnatural silence gaps — Morse code or on/off encoding
- File size vs duration mismatch — data appended after audio
- DTMF tones that spell out digits — phone-number encoding

### Text — What to Notice

- Lines that "feel" uneven or have invisible padding — whitespace encoding
- Copy-paste from a document that has odd character counts — zero-width Unicode
- Characters that look identical but aren't (Latin 'a' vs Cyrillic 'а') — homoglyph substitution
- Text that renders differently across viewers — encoding tricks

## 3. Statistical Tells

When context and visual inspection aren't enough, statistical analysis reveals what the eye can't see.

### Entropy

- **High entropy in unexpected places**: Natural images have structured entropy. Random-looking regions in a smooth image suggest encrypted or compressed hidden data.
- **Low entropy in expected-random regions**: An encrypted payload that's been LSB-embedded may actually *lower* the entropy of the LSB plane compared to noise.
- `binwalk -E` visualizes entropy — look for flat-line regions (encrypted data) or anomalies at specific offsets.

### Bit Plane Analysis

The most revealing statistical technique for images:

- **Clean images**: Bit planes show structured, correlated patterns that follow the image content
- **LSB-stego images**: The least significant bit plane looks random/noisy instead of correlated
- **Higher-bit stego**: Bits 1-2 may show noise while bits 3-7 show clean image structure

Use `bit_plane_extract.py --list` to check the ratio of on/off pixels per plane. In clean images, lower bits should correlate with image content. In stego images, they approach 50/50 randomness.

### Channel Correlation

- In natural images, R/G/B channels are correlated. LSB stego decorrelates the modified channel.
- XOR between channel bit planes: clean images show structure, stego images show noise.

## 4. Modern / AI-Based Steganography

Recent research uses neural networks to hide data in ways that defeat classical detection. Key tactics for identifying these:

### What AI Stego Looks Like

- **No LSB artifacts**: Classical tools (zsteg, StegSolve) find nothing. The data is encoded in learned features, not bit planes.
- **"Too clean"**: The image looks perfect — no noise, no artifacts, no structural anomalies. Natural images always have some imperfections.
- **Consistent statistical profile**: AI stego is trained to match the statistical distribution of clean images. It passes chi-square and RS tests.
- **High capacity with no visible change**: Papers report hiding entire images (23+ bpp) with only 0.76% pixel modification. If an image seems to contain more information than its visual complexity suggests, consider neural stego.

### Detection Approaches (No Samples Needed)

1. **Ensemble steganalysis**: Run multiple detection methods and look for disagreement. If chi-square says clean but SRM features say suspicious, investigate further.
2. **Feature-space analysis**: Neural stego modifies learned features, not pixels. Tools that analyze deep features (not just pixel statistics) are more likely to detect it.
3. **Adversarial awareness**: Modern stego can be adversarially trained to fool specific detectors. If one detector says clean, try a different one — transferability is limited.

### Practical Implications for CTF

- If classical tools all come up empty on an image that contextually *should* contain hidden data, suspect AI stego
- Look for hints about the method in the challenge: "deep," "neural," "learned," "generated" suggest AI-based hiding
- Entropy analysis is still useful: `binwalk -E` may reveal patterns even when LSB analysis doesn't
- Consider the challenge author's style — if they've used AI stego before, expect it again

## 5. Decision Framework

```
Is there hidden data?
│
├── Context says yes (challenge hint, file provenance, size anomaly)?
│   ├── YES → Start extraction (steganography-analyst skill)
│   └── MAYBE → Continue below
│
├── Structural anomaly? (wrong format, extra chunks, appended data)
│   ├── file + binwalk + xxd → format mismatch or embedded content?
│   └── pngcheck / exiftool → metadata inconsistencies?
│
├── Visual anomaly? (noise, banding, suspicious alpha)
│   ├── Bit plane analysis → LSB plane looks random?
│   └── Channel XOR → decorrelated channels?
│
├── Statistical anomaly? (entropy, bit distribution)
│   ├── binwalk -E → entropy spikes or flat regions?
│   └── bit_plane_extract.py --list → on/off ratio near 0.5?
│
├── All classical tests pass clean?
│   └── Suspect AI stego or no stego at all
│       ├── Context still says yes? → Try ensemble detection, deep feature analysis
│       └── Context says no? → Probably no hidden data
│
└── Found it → Switch to steganography-analyst for extraction
```

## 6. Common False Positives

- **JPEG compression** creates LSB noise that looks like stego — always check if the file is a re-saved JPEG
- **Camera sensor noise** in photos produces random-looking LSB patterns — this is normal
- **PNG optimization** tools may reorder chunks or add metadata — not stego
- **Text encoding differences** (UTF-8 vs Latin-1) can create apparent "hidden" characters — check the declared encoding
