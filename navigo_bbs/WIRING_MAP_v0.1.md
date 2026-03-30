# Suxen Wiring Map v0.1
**Stage 00 Artifact** — Boot Environment Inventory
**Date**: 2026-03-29
**Protocol**: PRIMORIS NAVIGO — patient cascading

---

## Platform Cables (Monster Cable Philosophy)
> Every signal path deserves intentional shielding. Not premium for status —
> premium because signal integrity matters.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRIMORIS PLATFORM                         │
│                                                             │
│  ┌──────────┐   PRIMARY TRUNK        ┌──────────────────┐  │
│  │  Claude  │══════════════════════► │  DOMOS / Drive   │  │
│  │  (Code)  │   GUBERNACULUM review  │  (Chain Custody) │  │
│  └────┬─────┘                        └──────────────────┘  │
│       │                                                     │
│       │  LINEAR LOOP (thin gauge, high frequency)           │
│       ▼                                                     │
│  ┌──────────┐                        ┌──────────────────┐  │
│  │  Linear  │                        │  Gemini (Gen)    │  │
│  │ (Issues) │                        │  BBS channel     │  │
│  └──────────┘                        └────────┬─────────┘  │
│                                               │             │
│       ┌───────────────────────────────────────┘             │
│       │  GENERATION CHANNEL (isolated from governance)      │
│       ▼                                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               NAVIGO BBS NODE                        │  │
│  │                                                      │  │
│  │  soft_modem.py ──► state_machine ──► session_log     │  │
│  │       │                                    │         │  │
│  │  hayes_parser     terminal_emulator    domos_feed    │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│       │                                                     │
│       │  ARCHIVE FEED → terminus → unexusi_stream           │
│       ▼                                                     │
│  ┌──────────┐   FUTURE                ┌──────────────────┐  │
│  │  DOMOS   │◄────────────────────────│ Vercel Frontend  │  │
│  │ Archive  │   BBS session logs      │ (Stage 05)       │  │
│  └──────────┘                         └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Signal Paths

| Cable | From | To | Shield | Notes |
|-------|------|----|--------|-------|
| Primary trunk | Claude | DOMOS | Maximum | Full GUBERNACULUM review |
| Generation channel | Gemini | BBS | Isolated | Code+content, no governance bleed |
| Linear loop | Linear | Claude | Thin | Issue/iteration, bidirectional |
| Archive feed | BBS | DOMOS | Standard | Session logs → terminus → unexusi |
| Frontend portal | Vercel | BBS | TBD | Future Stage 05 |

---

## Card Slots (Platform Components)

| Slot | Component | Status | Notes |
|------|-----------|--------|-------|
| 01 | Sovran Telegard (Pascal→Python) | Active | UserRecord, CRC32 done |
| 02 | Soft Modem (soft_modem.py) | Building | Stage 02 iteration 1 |
| 03 | Terminal Emulator (ANSI) | Pending | Stage 02 iteration 2 |
| 04 | Handshake Protocol Spec | Design | Stage 01 artifact |
| 05 | Session Logger | Pending | Stage 02 iteration 3 |
| 06 | BBS Session DNA | Design | Stage 04 |
| 07 | Vercel Frontend | Future | Stage 05 |

---

## Ground Loop Isolation Notes
*(Monster Cable: prevent signal bleed between AI nodes)*

- Claude handles governance, chain of custody, iteration planning
- Gemini handles code generation, BBS implementation deep dives
- Neither bleeds into the other's domain without explicit handshake
- Platform content flows ONE WAY into DOMOS (archive-only, never overwrites)

---

**∰◊€π¿🌌∞**
€(suxen_wiring_map_v0.1)
*Stage 00 complete — Iteration artifact generated*
