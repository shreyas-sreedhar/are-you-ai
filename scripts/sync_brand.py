#!/usr/bin/env python3
"""Copy the canonical design tokens into the places that cannot import them.

The web app imports `brand/tokens.css` directly. A Chrome extension can only
load files inside its own directory, so it gets a generated copy instead.

    python scripts/sync_brand.py [--check]

`--check` exits non-zero if the copy has drifted, which makes this usable as a
CI or pre-commit guard.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "brand" / "tokens.css"
TARGETS = (ROOT / "extension" / "styles" / "tokens.css",)

HEADER = """/* GENERATED FILE — DO NOT EDIT.
 * Source: brand/tokens.css
 * Regenerate with: python scripts/sync_brand.py
 */
"""


def rendered() -> str:
    return HEADER + "\n" + SOURCE.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify copies are up to date instead of writing them",
    )
    args = parser.parse_args()

    content = rendered()
    drifted: list[Path] = []

    for target in TARGETS:
        relative = target.relative_to(ROOT)
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else None
            if current != content:
                drifted.append(relative)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"wrote {relative}")

    if drifted:
        for path in drifted:
            print(f"out of date: {path}", file=sys.stderr)
        print("run: python scripts/sync_brand.py", file=sys.stderr)
        return 1

    if args.check:
        print("design tokens are in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
