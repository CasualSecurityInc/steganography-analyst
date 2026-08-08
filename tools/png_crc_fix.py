#!/usr/bin/env python3
"""Brute-force correct PNG dimensions when IHDR CRC doesn't match declared size."""

import argparse
import struct
import zlib

def fix_dimensions(png_path: str):
    with open(png_path, "rb") as f:
        data = f.read()

    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("Error: not a valid PNG file")
        return

    # IHDR chunk starts at offset 8 (length) + 4 (type) = 12
    # Width: bytes 12-15, Height: bytes 16-19
    # CRC covers type + data: bytes 8-28, stored at 29-32
    ihdr_type = data[8:12]
    ihdr_data = data[12:29]
    stored_crc = struct.unpack(">I", data[29:33])[0]

    declared_w = struct.unpack(">I", ihdr_data[0:4])[0]
    declared_h = struct.unpack(">I", ihdr_data[4:8])[0]
    print(f"Declared dimensions: {declared_w}x{declared_h}")

    found = []
    for h in range(1, 4096):
        for w in range(1, 4096):
            new_data = struct.pack(">II", w, h) + ihdr_data[8:]
            if zlib.crc32(ihdr_type + new_data) & 0xFFFFFFFF == stored_crc:
                found.append((w, h))

    if found:
        for w, h in found:
            print(f"Valid dimensions: {w}x{h}")
    else:
        print("No matching dimensions found in range 1-4095")

def main():
    parser = argparse.ArgumentParser(description="Brute-force correct PNG dimensions from IHDR CRC")
    parser.add_argument("png", help="PNG file to analyze")
    args = parser.parse_args()
    fix_dimensions(args.png)

if __name__ == "__main__":
    main()
