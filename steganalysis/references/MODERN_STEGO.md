# Modern Steganography — What Changed

Distilled from academic research on neural and adversarial steganography. Read this when classical tools find nothing but context says something is hidden.

## The Three Eras

### Classical (1990s–2015): Pixel Manipulation

- **LSB substitution**: Replace least significant bits of pixel values with message bits. Simple, high capacity, easily detected.
- **LSB matching**: Instead of replacing, add ±1 to pixel values. Harder to detect than substitution.
- **DCT steganography** (JPEG): Modify frequency coefficients. Steghide uses this.
- **Spread spectrum**: Spread signal across many pixels, like radio frequency hopping.

**Detection**: Chi-square analysis, RS analysis, sample pair analysis. These exploit the statistical artifact that LSB modification makes the histogram of pixel pair values converge.

### Adaptive (2010–2020): Content-Aware Embedding

- **HUGO, WOW, S-UNIWARD**: Embed only in "complex" image regions (edges, textures) where changes are less visible.
- **Syndrome trellis codes (STC)**: Mathematically optimal embedding that minimizes a distortion cost function.

**Detection**: Spatial rich model (SRM) features + machine learning classifiers. These analyze noise residuals across many filter kernels to find subtle statistical deviations.

### Neural (2017–present): Learned Hiding

- **StegNet, HiDDeN, SteganoGAN**: Train encoder/decoder networks end-to-end. The encoder hides a message in a cover image; the decoder extracts it. The network learns to minimize both detection probability and visual distortion.
- **Key difference**: The modification is not in specific bits — it's distributed across learned features that the network considers imperceptible.
- **Capacity**: Can hide entire images (23+ bpp) with <1% pixel modification. Classical methods max out around 1–4 bpp.

**Detection**: An arms race. Steganalysis networks (SRNet, Zhu-Net) are trained on clean/stego pairs. Adversarial steganography (Natias, 2024) corrupts the features these detectors rely on, improving transferability across different detector architectures.

## Why This Matters for CTF / Forensics

1. **Classical tools are necessary but not sufficient.** zsteg, StegSolve, binwalk catch 90% of CTF stego. But if they all come up empty on a suspicious file, don't give up.

2. **Neural stego leaves no LSB trace.** The bit plane analysis that catches classical LSB stego will show nothing. The data is encoded in a way that preserves statistical properties of the cover image.

3. **The giveaway is often context, not the file.** A challenge that says "AI" or "deep learning" or "generated" is signaling neural stego. A file from an APT campaign that's oddly large for its content is suspicious regardless of what tools say.

4. **Entropy analysis still helps.** Even neural stego must encode information *somewhere*. `binwalk -E` entropy plots may reveal subtle anomalies at specific offsets, even when LSB analysis is clean.

5. **Adversarial stego defeats specific detectors.** If a tool says "clean," it might mean "clean to *this* detector." Try multiple approaches — transferability between detectors is limited.

## Papers for Deeper Reading

| Paper | What it teaches | arXiv |
|-------|----------------|-------|
| StegNet (2018) | How deep CNNs hide full images with mega capacity | [1806.06357](https://arxiv.org/abs/1806.06357) |
| GAN-based stego survey (2019) | Three strategies: modify, select, synthesize covers | [1907.01886](https://arxiv.org/abs/1907.01886) |
| MIAIS (2021) | Hiding identity-bearing images (faces, fingerprints) | [2107.05819](https://arxiv.org/abs/2107.05819) |
| Natias (2024) | Adversarial stego that defeats deep steganalysis via neuron attribution | [2409.04968](https://arxiv.org/abs/2409.04968) |
| CNN vs adversarial embedding (2019) | Game-theoretic framing of steganographer vs steganalyst | [1906.00697](https://arxiv.org/abs/1906.00697) |
| DDSP (2019) | GAN that destroys stego while preserving visual quality | [1912.10070](https://arxiv.org/abs/1912.10070) |
| SCReedSolo (2025) | Modern LSB with Reed-Solomon error correction | [2503.12368](https://arxiv.org/abs/2503.12368) |
| StegExpose (2014) | Detection tool design — what steganalysis looks for | [1410.6656](https://arxiv.org/abs/1410.6656) |
| StegoAppDB (2019) | Real-world stego image database for benchmarking | [1904.09360](https://arxiv.org/abs/1904.09360) |
