#!/usr/bin/env python3
"""Check for data appended after WAV audio data."""

import argparse
import os
import wave

def check(wav_path: str):
    with wave.open(wav_path, "rb") as w:
        n_frames = w.getnframes()
        n_channels = w.getnchannels()
        sampwidth = w.getsampwidth()
        framerate = w.getframerate()

    audio_data_size = n_frames * n_channels * sampwidth
    header_size = 44  # Standard WAV header
    expected_size = header_size + audio_data_size
    actual_size = os.path.getsize(wav_path)

    print(f"Channels: {n_channels}")
    print(f"Sample width: {sampwidth} bytes ({sampwidth * 8}-bit)")
    print(f"Frame rate: {framerate} Hz")
    print(f"Frames: {n_frames}")
    print(f"Duration: {n_frames / framerate:.2f}s")
    print(f"Audio data: {audio_data_size} bytes")
    print(f"Expected file size: {expected_size} bytes")
    print(f"Actual file size: {actual_size} bytes")

    extra = actual_size - expected_size
    if extra > 0:
        print(f"\nFOUND: {extra} bytes of extra data appended after audio!")
        # Show first bytes of appended data
        with open(wav_path, "rb") as f:
            f.seek(expected_size)
            preview = f.read(min(64, extra))
        print(f"Preview (hex): {preview.hex()}")
        try:
            print(f"Preview (ascii): {preview.decode('ascii', errors='replace')}")
        except Exception:
            pass
    elif extra < 0:
        print(f"\nFile is {-extra} bytes shorter than expected (truncated?)")
    else:
        print("\nFile size matches expected — no appended data detected")

def main():
    parser = argparse.ArgumentParser(description="Check WAV file for appended hidden data")
    parser.add_argument("wav", help="WAV file to analyze")
    args = parser.parse_args()
    check(args.wav)

if __name__ == "__main__":
    main()
