#!/usr/bin/env python3
"""
Flatten a chapter JSON (list-of-lists of line dicts) into a single list,
save it, and report the unique moods found.

Usage:
    python flatten_chapter.py chapter01.json [-o chapter01_flat.json]
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any


def load_lists(path: Path) -> List[List[Dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten(nested: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    return [item for sublist in nested for item in sublist]


def collect_moods(items: List[Dict[str, Any]]) -> List[str]:
    return sorted({d.get("mood", "") for d in items if d.get("mood")})


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flatten chapter JSON and list unique moods."
    )
    parser.add_argument("input_json", help="input JSON file (list of lists)")
    parser.add_argument(
        "-o", "--output",
        help="output JSON file (default: <input_basename>_flat.json)"
    )
    args = parser.parse_args()

    in_path = Path(args.input_json)
    out_path = Path(args.output) if args.output else in_path.with_stem(in_path.stem + "_flat")

    # 1. read → flatten → write
    nested_lists = load_lists(in_path)
    flat_list = flatten(nested_lists)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(flat_list, f, ensure_ascii=False, indent=2)

    # 2. collect & report moods
    moods = collect_moods(flat_list)
    print(f"✅ Wrote flattened chapter to: {out_path}")
    print(f"🎭 Unique moods used ({len(moods)}): {moods}")
    return 0


if __name__ == "__main__":
    main()
