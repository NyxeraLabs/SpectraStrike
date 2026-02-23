# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

"""Check that tracked source/docs/config files include the license header."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_MARKERS = (
    "Copyright (c) 2026 NyxeraLabs",
    "Author: José María Micoli",
    "Licensed under BSL 1.1",
    "Change Date: 2033-02-22 -> Apache-2.0",
)

TARGET_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".mjs",
    ".md",
    ".txt",
    ".sh",
    ".yml",
    ".yaml",
    ".toml",
    ".conf",
}

HEADER_SCAN_LINES = 40


def is_target(path: Path) -> bool:
    if path.name == "Makefile" or path.name == "Dockerfile":
        return True
    if path.suffix in TARGET_EXTENSIONS:
        return True
    return False


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def has_license_header(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            first_lines = "".join(handle.readline() for _ in range(HEADER_SCAN_LINES))
    except OSError:
        return False
    return all(marker in first_lines for marker in REQUIRED_MARKERS)


def main(argv: list[str]) -> int:
    files = [Path(arg) for arg in argv] if argv else tracked_files()
    missing: list[Path] = []

    for file_path in files:
        if not file_path.exists() or file_path.is_dir() or not is_target(file_path):
            continue
        if not has_license_header(file_path):
            missing.append(file_path)

    if not missing:
        return 0

    print("Missing or incomplete license header in:")
    for file_path in missing:
        print(f"- {file_path}")
    print("\nExpected header markers in first lines:")
    for marker in REQUIRED_MARKERS:
        print(f"- {marker}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
