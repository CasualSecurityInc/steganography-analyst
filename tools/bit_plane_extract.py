#!/usr/bin/env python3
"""Bit plane extraction and analysis — CLI replacement for StegSolve's core functionality.

Extracts individual bit planes from R, G, B channels of an image.
Supports XOR, AND, OR operations between planes and channel reordering.
"""

import argparse
import os
import sys

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERROR: Requires Pillow and numpy. Install with:")
    print("  uv pip install Pillow numpy")
    sys.exit(1)


def load_image(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGBA")
    return np.array(img)


def extract_bit_plane(channel: np.ndarray, bit: int) -> np.ndarray:
    """Extract a single bit plane from a channel (0=LSB, 7=MSB)."""
    return ((channel >> bit) & 1) * 255


def extract_half(channel: np.ndarray, half: str) -> np.ndarray:
    """Extract lower 4 bits (lsb) or upper 4 bits (msb) of a channel."""
    if half == "lsb":
        return (channel & 0x0F) * 16
    else:
        return channel & 0xF0


def channel_from_name(img: np.ndarray, name: str) -> np.ndarray:
    """Get channel array by name. Supports RGBA and reverse (BGR) order."""
    mapping = {"r": 0, "g": 1, "b": 2, "a": 3}
    idx = mapping.get(name.lower())
    if idx is None:
        raise ValueError(f"Unknown channel: {name}. Use r, g, b, or a.")
    if idx >= img.shape[2]:
        raise ValueError(f"Image has no {name.upper()} channel")
    return img[:, :, idx]


def apply_operation(plane_a: np.ndarray, plane_b: np.ndarray, op: str) -> np.ndarray:
    """Apply bitwise operation between two planes."""
    ops = {"xor": np.bitwise_xor, "and": np.bitwise_and, "or": np.bitwise_or}
    fn = ops.get(op.lower())
    if fn is None:
        raise ValueError(f"Unknown operation: {op}. Use xor, and, or or.")
    return fn(plane_a, plane_b)


def reorder_channels(img: np.ndarray, order: str) -> np.ndarray:
    """Reorder RGB channels. E.g., 'bgr', 'rbg', 'gbr'."""
    mapping = {"r": 0, "g": 1, "b": 2}
    indices = [mapping[c] for c in order.lower()]
    rgba = img.copy()
    rgba[:, :, :3] = img[:, :, indices]
    return rgba


def plane_to_image(plane: np.ndarray, width: int, height: int) -> Image.Image:
    """Convert a 2D numpy array to a PIL Image."""
    return Image.fromarray(plane.reshape(height, width).astype(np.uint8), mode="L")


def composite_rgb(img: np.ndarray, r_bit: int, g_bit: int, b_bit: int) -> Image.Image:
    """Create an RGB composite from individual bit planes of each channel."""
    r = extract_bit_plane(img[:, :, 0], r_bit)
    g = extract_bit_plane(img[:, :, 1], g_bit)
    b = extract_bit_plane(img[:, :, 2], b_bit)
    composite = np.stack([r, g, b], axis=-1)
    return Image.fromarray(composite.astype(np.uint8), mode="RGB")


def list_planes(img: np.ndarray) -> list[dict]:
    """List all available bit planes for each channel."""
    info = []
    h, w = img.shape[:2]
    for ch_idx, ch_name in enumerate(["R", "G", "B"]):
        if ch_idx >= img.shape[2]:
            continue
        for bit in range(8):
            plane = extract_bit_plane(img[:, :, ch_idx], bit)
            # Calculate how many "on" pixels
            on_count = int(np.sum(plane > 0))
            info.append({
                "channel": ch_name,
                "bit": bit,
                "on_pixels": on_count,
                "total_pixels": w * h,
                "ratio": on_count / (w * h),
            })
    return info


def main():
    parser = argparse.ArgumentParser(
        description="Bit plane extraction and analysis (StegSolve CLI replacement)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  %(prog)s image.png --plane r0              # Red channel, bit 0 (LSB)
  %(prog)s image.png --plane g7              # Green channel, bit 7 (MSB)
  %(prog)s image.png --plane r0 --xor g0     # XOR red bit 0 with green bit 0
  %(prog)s image.png --composite 0,0,0       # RGB composite of LSBs
  %(prog)s image.png --list                  # List all bit planes with stats
  %(prog)s image.png --channel r --all       # All 8 bit planes of red channel
  %(prog)s image.png --reorder bgr           # Swap red and blue channels
  %(prog)s image.png --lsb-half r            # Lower 4 bits of red channel
"""
    )
    parser.add_argument("image", help="Input image file")
    parser.add_argument("-o", "--output", help="Output image file (default: auto-named)")
    parser.add_argument("--plane", metavar="C_BIT",
                        help="Extract bit plane: channel + bit (e.g., r0, g7, b3)")
    parser.add_argument("--xor", metavar="C_BIT",
                        help="XOR with another bit plane")
    parser.add_argument("--and", metavar="C_BIT", dest="and_plane",
                        help="AND with another bit plane")
    parser.add_argument("--or", metavar="C_BIT", dest="or_plane",
                        help="OR with another bit plane")
    parser.add_argument("--composite", metavar="R_BIT,G_BIT,B_BIT",
                        help="RGB composite from bit planes (e.g., 0,0,0 for all LSBs)")
    parser.add_argument("--reorder", metavar="ORDER",
                        help="Reorder channels (e.g., bgr, rbg)")
    parser.add_argument("--lsb-half", metavar="CHANNEL",
                        help="Extract lower 4 bits of channel")
    parser.add_argument("--msb-half", metavar="CHANNEL",
                        help="Extract upper 4 bits of channel")
    parser.add_argument("--list", action="store_true",
                        help="List all bit planes with pixel statistics")
    parser.add_argument("--all", action="store_true",
                        help="Extract all 8 bit planes of specified channel (with --plane)")
    parser.add_argument("--dir", help="Output directory for --all (default: ./bit_planes)")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: file not found: {args.image}")
        sys.exit(1)

    img = load_image(args.image)
    h, w = img.shape[:2]
    base = os.path.splitext(os.path.basename(args.image))[0]

    # --list: show all planes
    if args.list:
        planes = list_planes(img)
        print(f"{'Channel':>7} {'Bit':>3} {'On Pixels':>10} {'Total':>10} {'Ratio':>8}")
        print("-" * 45)
        for p in planes:
            print(f"{p['channel']:>7} {p['bit']:>3} {p['on_pixels']:>10} {p['total_pixels']:>10} {p['ratio']:>8.4f}")
        return

    # --reorder
    if args.reorder:
        reordered = reorder_channels(img, args.reorder)
        out = args.output or f"{base}_reorder_{args.reorder}.png"
        Image.fromarray(reordered).save(out)
        print(f"Saved: {out}")
        return

    # --composite
    if args.composite:
        parts = args.composite.split(",")
        if len(parts) != 3:
            print("Error: --composite needs R_BIT,G_BIT,B_BIT (e.g., 0,0,0)")
            sys.exit(1)
        r_bit, g_bit, b_bit = int(parts[0]), int(parts[1]), int(parts[2])
        result = composite_rgb(img, r_bit, g_bit, b_bit)
        out = args.output or f"{base}_composite_r{r_bit}g{g_bit}b{b_bit}.png"
        result.save(out)
        print(f"Saved: {out}")
        return

    # --lsb-half / --msb-half
    if args.lsb_half:
        ch = channel_from_name(img, args.lsb_half)
        plane = extract_half(ch, "lsb")
        out = args.output or f"{base}_{args.lsb_half}_lsb_half.png"
        plane_to_image(plane, w, h).save(out)
        print(f"Saved: {out}")
        return
    if args.msb_half:
        ch = channel_from_name(img, args.msb_half)
        plane = extract_half(ch, "msb")
        out = args.output or f"{base}_{args.msb_half}_msb_half.png"
        plane_to_image(plane, w, h).save(out)
        print(f"Saved: {out}")
        return

    # --plane (with optional --all)
    if args.plane:
        ch_name = args.plane[0]
        bit = int(args.plane[1:])
        ch = channel_from_name(img, ch_name)

        if args.all:
            out_dir = args.dir or "bit_planes"
            os.makedirs(out_dir, exist_ok=True)
            for b in range(8):
                plane = extract_bit_plane(ch, b)
                out = os.path.join(out_dir, f"{base}_{ch_name}_bit{b}.png")
                plane_to_image(plane, w, h).save(out)
            print(f"Saved 8 planes to {out_dir}/")
            return

        plane_a = extract_bit_plane(ch, bit)

        # Apply operation if specified
        if args.xor or args.and_plane or args.or_plane:
            op_str = "xor" if args.xor else ("and" if args.and_plane else "or")
            op_val = args.xor or args.and_plane or args.or_plane
            ch2_name = op_val[0]
            bit2 = int(op_val[1:])
            ch2 = channel_from_name(img, ch2_name)
            plane_b = extract_bit_plane(ch2, bit2)
            result = apply_operation(plane_a, plane_b, op_str)
            suffix = f"_{op_str}_{op_val}"
        else:
            result = plane_a
            suffix = ""

        out = args.output or f"{base}_{args.plane}{suffix}.png"
        plane_to_image(result, w, h).save(out)
        print(f"Saved: {out}")
        return

    # No action specified
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
