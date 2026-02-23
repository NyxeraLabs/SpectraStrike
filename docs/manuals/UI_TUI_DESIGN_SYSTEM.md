<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike UI/TUI Design System

## 1. Palette

Core backgrounds:
- Primary background: `#0B1020`
- Secondary surface: `#131A2E`
- Elevated surface: `#1A2238`
- Border subtle: `#222C4A`

Primary accent:
- Spectral Violet: `#7C5CFF`
- Electric Iris: `#9D8CFF`
- Deep Violet hover: `#5E3FE6`
- Focus ring: `#B6A8FF`

Telemetry/Execution accent:
- Cyan signal: `#00D4FF`
- Deep cyan: `#0095B6`
- Telemetry glow: `#33E1FF`

Status colors:
- Success: `#1ED760`
- Warning: `#F5A524`
- Critical: `#FF4D4F`
- Info: `#3B82F6`

## 2. Typography

Web UI:
- Primary: `Inter` (400, 500, 600, 700)
- Display accents: `Space Grotesk` (major headings only)
- Monospace: `JetBrains Mono` (logs, telemetry, audit, task output)

TUI:
- Primary text: `#E6E9F5`
- Muted text: `#94A3B8`
- Monospace default: `JetBrains Mono` or `IBM Plex Mono`

## 3. Component Rules

Buttons:
- Primary: background `#7C5CFF`, hover `#5E3FE6`, text white, radius `12px`, glow `0 0 12px rgba(124, 92, 255, 0.35)`.
- Secondary: transparent background, `1px` border `#7C5CFF`, hover `rgba(124, 92, 255, 0.1)`.

Cards/Panels:
- Background `#131A2E`, border `#222C4A`, subtle shadow only.

Glow usage:
- Allowed only for active orchestrator task, live telemetry, and critical alerts.
- Avoid glow on static layout elements.

## 4. TUI Semantic Colors

- Command: `#7C5CFF`
- Success: `#1ED760`
- Warning: `#F5A524`
- Error: `#FF4D4F`
- Telemetry event: `#00D4FF`
- Metadata: `#9CA3AF`
