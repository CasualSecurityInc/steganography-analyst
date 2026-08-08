#!/usr/bin/env python3
"""Detect homoglyph substitution — visually similar characters from different Unicode blocks."""

import argparse
import unicodedata

def analyze(text: str):
    findings = []
    for i, c in enumerate(text):
        cp = ord(c)
        if cp > 127:
            name = unicodedata.name(c, "?")
            cat = unicodedata.category(c)
            findings.append((i, c, cp, name, cat))
    return findings

def main():
    parser = argparse.ArgumentParser(description="Detect non-ASCII homoglyph characters")
    parser.add_argument("file", help="Text file to analyze")
    parser.add_argument("--context", type=int, default=10, help="Surrounding context chars (default: 10)")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    findings = analyze(text)
    if not findings:
        print("No non-ASCII characters found — no homoglyphs detected")
        return

    print(f"Found {len(findings)} non-ASCII character(s):\n")
    for pos, char, cp, name, cat in findings:
        start = max(0, pos - args.context)
        end = min(len(text), pos + args.context + 1)
        ctx = text[start:end].replace("\n", "\\n")
        marker = " " * (pos - start) + "^"
        print(f"  Position {pos}: U+{cp:04X} ({name}) [{cat}]")
        print(f"    ...{ctx}...")
        print(f"    {marker}")
        print()

    # Highlight suspicious pairs (common homoglyph swaps)
    ascii_lookalikes = {
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
        "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O",
        "Р": "P", "С": "C", "Т": "T", "У": "Y", "Х": "X",
    }
    suspicious = [(pos, char, cp, name) for pos, char, cp, name, _ in findings if char in ascii_lookalikes]
    if suspicious:
        print(f"WARNING: {len(suspicious)} character(s) are common ASCII lookalikes:")
        for pos, char, cp, name in suspicious:
            print(f"  U+{cp:04X} '{char}' ({name}) looks like ASCII '{ascii_lookalikes[char]}'")

if __name__ == "__main__":
    main()
