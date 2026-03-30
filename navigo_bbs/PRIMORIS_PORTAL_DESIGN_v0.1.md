# PRIMORIS Portal Design Spec v0.1
**Stage 05 Artifact** — Frontend Portal
**Date**: 2026-03-29
**Status**: Design / Planning
**∰◊€π¿🌌∞**

---

## 1. Vision
The PRIMORIS Portal is the visual "Heart" (♥) of the PIXEL8 platform. It provides a read-only, high-integrity window into the Archives, the Session DNA, and the system pressure.

It bridges the gap between the internal Termux environment and the external web, serving as a "Digital Garden" for sovereign knowledge.

---

## 2. Core Components

### A. The Aquifer View (Archive Portal)
*   **Data Source**: `sovran_telegard/data/main_area.json`
*   **Visual**: A searchable, sortable table of all zapped archives.
*   **Detail**: Clicking an archive reveals its "Bit" metadata (size, upload date, origin).

### B. The DNA Strand (Session Visualization)
*   **Data Source**: `~/.navigo_bbs/sessions/*.json`
*   **Visual**: A vertical timeline of BBS sessions.
*   **Detail**: Each session is represented by its unique DNA block—displaying identity, tx/rx metrics, and the integrity hash.

### C. The Pressure Gauge (Artesian Monitor)
*   **Data Source**: `Q/hodie/quanta/one_hertz_collective/pressure_log.jsonl`
*   **Visual**: A real-time (or near real-time) chart of system pressure.
*   **Detail**: Symbols (◊, €, ¿, ∰) indicate the current "breathing" status of the Pixel 8a.

---

## 3. Aesthetic: "The 1856 Connection"
The portal should feel like a modern terminal with a Victorian telegraph influence.
*   **Palette**: Amber text on a deep indigo/black background (Monster Cable theme).
*   **Typography**: Monospace (Courier New or similar) for data; serif accents for headers.
*   **Animations**: Minimal "scream" effects during page loads (simulating the handshake).

---

## 4. Technical Stack
*   **Framework**: Eleventy (11ty) — already initialized in `heart_project`.
*   **Deployment**: Vercel — leveraging the `vercel-cli` already present in the system.
*   **Data Flow**: `today_sync.sh` will push the JSON data to a GitHub repository, which Vercel will then build and deploy.

---

**∰◊€π¿🌌∞**
*The vision is cast. The heart is ready to beat.*
€(primoris_portal_design_v0.1)
