#!/usr/bin/env python3
"""
Prepare photos for Claude Code analysis.
Converts HEIC/large images to compressed JPEGs under 256KB.

Usage:
    python tools/prep_photos.py /path/to/photo1.HEIC /path/to/photo2.jpg ...

Output:
    Prints paths to converted files in /tmp (one per line)
"""

import sys
import subprocess
import os
from pathlib import Path


def get_file_size(path: str) -> int:
    """Get file size in bytes."""
    return os.path.getsize(path)


def convert_photo(input_path: str, max_size_kb: int = 200) -> str:
    """
    Convert photo to JPEG, compress until under max_size_kb.
    Returns path to converted file in /tmp.
    """
    input_path = Path(input_path).expanduser()
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    stem = input_path.stem
    output_path = f"/tmp/{stem}.jpg"

    # Start with quality 60, decrease if needed
    quality = 60
    min_quality = 20

    while quality >= min_quality:
        # Use sips for conversion (macOS native, handles HEIC)
        cmd = [
            "sips",
            "-s", "format", "jpeg",
            "-s", "formatOptions", str(quality),
            str(input_path),
            "--out", output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"sips failed: {result.stderr}")

        size_kb = get_file_size(output_path) / 1024

        if size_kb <= max_size_kb:
            return output_path

        # Try lower quality
        quality -= 10

    # If still too large, resize dimensions
    cmd = [
        "sips",
        "-Z", "1200",  # Max dimension 1200px
        "-s", "format", "jpeg",
        "-s", "formatOptions", str(min_quality),
        str(input_path),
        "--out", output_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: prep_photos.py <photo1> [photo2] ...")
        print("Converts photos to compressed JPEGs for Claude Code analysis")
        sys.exit(1)

    output_paths = []
    for input_path in sys.argv[1:]:
        try:
            output = convert_photo(input_path)
            output_paths.append(output)
            size_kb = get_file_size(output) / 1024
            print(f"{output} ({size_kb:.0f}KB)", file=sys.stderr)
        except Exception as e:
            print(f"Error processing {input_path}: {e}", file=sys.stderr)
            sys.exit(1)

    # Print just the paths to stdout (for piping/scripting)
    for p in output_paths:
        print(p)


if __name__ == "__main__":
    main()
