#!/usr/bin/env python3
"""Decode data hidden in zero-width Unicode characters."""

import argparse

ZERO_WIDTH_CHARS = {
    0x200B: 0,  # Zero-Width Space
    0x200C: 1,  # Zero-Width Non-Joiner
    0x200D: 1,  # Zero-Width Joiner
    0xFEFF: 0,  # BOM / Zero-Width No-Break Space
}

def decode(text: str) -> bytes:
    hidden = [c for c in text if ord(c) in ZERO_WIDTH_CHARS]
    if not hidden:
        return b""

    bits = "".join(str(ZERO_WIDTH_CHARS[ord(c)]) for c in hidden)
    data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        data.append(int(bits[i:i+8], 2))
    return bytes(data)

def main():
    parser = argparse.ArgumentParser(description="Decode zero-width character steganography")
    parser.add_argument("file", help="Text file to analyze")
    parser.add_argument("-o", "--output", help="Write decoded bytes to file (default: print as text)")
    parser.add_argument("--raw", action="store_true", help="Print raw hex instead of text")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    hidden_count = sum(1 for c in text if ord(c) in ZERO_WIDTH_CHARS)
    print(f"Found {hidden_count} zero-width characters")

    result = decode(text)
    if not result:
        print("No hidden data decoded")
        return

    if args.output:
        with open(args.output, "wb") as f:
            f.write(result)
        print(f"Wrote {len(result)} bytes to {args.output}")
    elif args.raw:
        print(result.hex())
    else:
        try:
            print(result.decode("utf-8"))
        except UnicodeDecodeError:
            print(f"(not valid UTF-8, {len(result)} raw bytes)")
            print(result.hex())

if __name__ == "__main__":
    main()
