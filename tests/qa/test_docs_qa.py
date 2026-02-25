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

from __future__ import annotations

import csv
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_docs_manual_index_references_existing_files() -> None:
    index_path = REPO_ROOT / "docs/manuals/INDEX.md"
    content = index_path.read_text(encoding="utf-8")
    referenced_paths = re.findall(
        r"`((?:docs/|README\.md|SECURITY\.md)[^`]+)`", content
    )
    assert referenced_paths, "expected at least one referenced path in manuals index"

    for relative_path in referenced_paths:
        absolute_path = REPO_ROOT / relative_path
        assert (
            absolute_path.exists()
        ), f"missing referenced documentation file: {relative_path}"


def test_roadmap_sprints_95_96_97_are_marked_complete() -> None:
    roadmap_path = REPO_ROOT / "docs/ROADMAP.md"
    content = roadmap_path.read_text(encoding="utf-8")

    required_lines = [
        "### Sprint 9.5 (Week 18): Messaging Backbone (Kafka/RabbitMQ)",
        "### Sprint 9.6 (Week 18-19): User Interface Foundation (Before Cobalt Strike)",
        "### Sprint 9.7 (Week 19): Security & Container Platform Hardening "
        "(Before Cobalt Strike)",
    ]
    for line in required_lines:
        assert line in content, f"missing roadmap milestone: {line}"

    for section_title in required_lines:
        section_start = content.index(section_title)
        next_section = content.find("\n### ", section_start + 1)
        section = (
            content[section_start:]
            if next_section == -1
            else content[section_start:next_section]
        )
        assert (
            "- [ ]" not in section
        ), f"incomplete items found in section: {section_title}"


def test_roadmap_sprints_11_12_13_are_marked_complete() -> None:
    roadmap_path = REPO_ROOT / "docs/ROADMAP.md"
    content = roadmap_path.read_text(encoding="utf-8")

    required_lines = [
        "### Sprint 11 (Week 23-24): The Armory (Tool Registry)",
        "### Sprint 12 (Week 25-26): The Universal Edge Runner",
        "### Sprint 13 (Week 27): Execution Fabric QA",
    ]
    for line in required_lines:
        assert line in content, f"missing roadmap milestone: {line}"

    for section_title in required_lines:
        section_start = content.index(section_title)
        next_section = content.find("\n### ", section_start + 1)
        section = (
            content[section_start:]
            if next_section == -1
            else content[section_start:next_section]
        )
        assert (
            "- [ ]" not in section
        ), f"incomplete items found in section: {section_title}"


def test_kanban_csv_has_expected_columns() -> None:
    kanban_path = REPO_ROOT / "docs/kanban-board.csv"
    with kanban_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        expected_columns = ["Name", "Description", "List", "Labels", "Checklist"]
        assert reader.fieldnames == expected_columns
