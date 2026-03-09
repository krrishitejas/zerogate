#!/usr/bin/env python3
"""
rebrand_zerogate.py

Run this script from the root of your cloned repository to perform a
"total conversion" from the original Code‑Graph‑RAG naming scheme to the
new ZeroGate scheme.

Usage:
    python3 rebrand_zerogate.py

The script:
  1) Performs in‑file content replacements for all defined patterns.
  2) Renames files/directories that contain the old identifiers.
  3) Skips binary files, the script itself, and the usual build‑/IDE‑related
     directories (.git, .idea, __pycache__, node_modules).
"""

import os
import re
import sys
from pathlib import Path

# ------------------------------------------------------------
# Configuration – mapping from old terms to new ones
# ------------------------------------------------------------
MAPPING = {
    "code_graph_rag": "zerogate",
    "CodeGraphRAG": "ZeroGate",
    "Code Graph RAG": "ZeroGate",
    "code-graph-rag": "zerogate",
    "CODE_GRAPH_RAG": "ZEROGATE",
}

# Compile a regex that matches any key in the mapping
PATTERN = re.compile("|".join(re.escape(k) for k in MAPPING.keys()))

# Directories to ignore entirely
IGNORE_DIRS = {".git", ".idea", "__pycache__", "node_modules"}

# File extensions considered binary (image, compiled bytecode, etc.)
BINARY_EXTS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
    ".ico", ".svg", ".eot", ".ttf", ".otf",
    ".woff", ".woff2", ".mp4", ".mp3", ".wav",
    ".exe", ".dll", ".so", ".dylib", ".pyc", ".pyo",
    ".class", ".jar",
}

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def is_text_file(path: Path) -> bool:
    """Heuristic: return True if file appears to be a text file."""
    if path.suffix.lower() in BINARY_EXTS:
        return False
    try:
        # Try decoding first 1 KiB
        with open(path, "rb") as f:
            chunk = f.read(1024)
        chunk.decode("utf-8")
        return True
    except Exception:
        return False


def replace_in_text(text: str) -> str:
    """Replace all occurrences of the mapping keys."""
    return PATTERN.sub(lambda m: MAPPING[m.group(0)], text)

# ------------------------------------------------------------
# Phase 1 – Content replacement
# ------------------------------------------------------------

def phase_one(root: Path):
    print("Phase 1: Content replacement")
    changed_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for fname in filenames:
            if fname == "rebrand_zerogate.py":
                continue
            fpath = Path(dirpath) / fname
            if not is_text_file(fpath):
                continue
            try:
                text = fpath.read_text(encoding="utf-8")
            except Exception as e:
                print(f"  ⚠️  Skipping unreadable file: {fpath} ({e})")
                continue

            new_text = replace_in_text(text)
            if new_text != text:
                fpath.write_text(new_text, encoding="utf-8")
                changed_files.append(fpath)

    for f in changed_files:
        print(f"Modified: {f.relative_to(root)}")
    print(f"Total files changed: {len(changed_files)}\n")

# ------------------------------------------------------------
# Phase 2 – Path renaming
# ------------------------------------------------------------

def phase_two(root: Path):
    print("Phase 2: Path renaming")
    renamed = []

    # Walk bottom‑up so that we rename children before parents
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        # Rename directories
        for d in dirnames:
            if "code_graph_rag" in d or "code-graph-rag" in d:
                old = Path(dirpath) / d
                new_name = d.replace("code_graph_rag", "zerogate").replace("code-graph-rag", "zerogate")
                new = Path(dirpath) / new_name
                old.rename(new)
                renamed.append((old, new))

        # Rename files
        for f in filenames:
            if f == "rebrand_zerogate.py":
                continue
            if "code_graph_rag" in f or "code-graph-rag" in f:
                old = Path(dirpath) / f
                new_name = f.replace("code_graph_rag", "zerogate").replace("code-graph-rag", "zerogate")
                new = Path(dirpath) / new_name
                old.rename(new)
                renamed.append((old, new))

    for old, new in renamed:
        print(f"Renamed: {old.relative_to(root)} → {new.relative_to(root)}")
    print(f"Total items renamed: {len(renamed)}\n")

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    root = Path.cwd()
    print(f"Rebranding repository at: {root}\n")
    phase_one(root)
    phase_two(root)
    print("Rebranding complete! 🎉")


if __name__ == "__main__":
    main()
