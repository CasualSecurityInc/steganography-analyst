#!/usr/bin/env python3
"""Extract data hidden in WAV file LSBs."""

import argparse
import struct
import wave

def extract_lsb(wav_path: str, output_path: str, num_lsb: int = 1, max_bytes: int | None = None):
    with wave.open(wav_path, "rb") as w:
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        n_frames = w.getnframes()
        raw = w.readframes(n_frames)

    if sampwidth != 2:
        print(f"Warning: expected 16-bit audio, got {sampwidth * 8}-bit. Results may be wrong.")

    samples = struct.unpack(f"<{n_frames * n_channels}h", raw)
    bits = []
    for sample in samples:
        for bit in range(num_lsb):
            bits.append((sample >> bit) & 1)

    # Convert bits to bytes
    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for bit in range(8):
            byte |= bits[i + bit] << bit
        data.append(byte)
        if max_bytes and len(data) >= max_bytes:
            break

    with open(output_path, "wb") as f:
        f.write(data)
    print(f"Extracted {len(data)} bytes to {output_path} (using {num_lsb} LSB(s))")

def main():
    parser = argparse.ArgumentParser(description="Extract data from WAV LSB steganography")
    parser.add_argument("-i", "--input", required=True, help="Input WAV file")
    parser.add_argument("-o", "--output", required=True, help="Output file for extracted data")
    parser.add_argument("-n", "--lsb", type=int, default=1, help="Number of LSBs to extract (1-4, default: 1)")
    parser.add_argument("-m", "--max-bytes", type=int, default=None, help="Max bytes to extract")
    args = parser.parse_args()
    extract_lsb(args.input, args.output, args.lsb, args.max_bytes)

if __name__ == "__main__":
    main()
