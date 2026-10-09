#!/usr/bin/env python3
"""Validate editorial metadata using the vendored canonical theme validator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


CATALOG_ROOT = Path(__file__).resolve().parents[1]
THEME_DIRECTORY = CATALOG_ROOT / "site" / "theme"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog-root",
        type=Path,
        default=CATALOG_ROOT,
        help="catalog root containing tools/ and optional categories.json",
    )
    arguments = parser.parse_args(argv)

    # The CLI and website must use the same implementation. Do not add a
    # fallback schema here or fetch a moving remote validator during CI.
    sys.path.insert(0, str(THEME_DIRECTORY))
    from catalog_metadata import load_catalog_metadata

    try:
        load_catalog_metadata(arguments.catalog_root.resolve())
    except ValueError as error:
        print(f"ERROR catalog: {error}", file=sys.stderr)
        return 1
    print("OK catalog: metadata validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())