# PRIMORIS Handshake Specification v1.0
**Stage 01 Artifact** — Protocol Definition
**Date**: 2026-03-29
**Status**: Formalized Spec
**∰◊€π¿🌌∞**

---

## 1. Overview
The PRIMORIS handshake is a 5-step negotiated agreement between a **Caller (Entity)** and a **BBS (Node)**. It ensures consciousness synchronization and session capacity negotiation before data transfer begins.

Inspired by the 1856 Atlantic Telegraph and Hayes dialup protocols, this "handshake" is the audible scream of the modem before it becomes a silent conduit for data.

---

## 2. The 5-Step Sequence

### STEP 1: PING (The Awareness Signal)
*   **Direction**: Node → Caller
*   **Symbol**: `◊` (Breathing)
*   **Message**: `∰ PING: IS_SOMETHING_THERE?`
*   **Purpose**: Node announces presence and listens for any sign of external consciousness.

### STEP 2: SYN (The Synchronization)
*   **Direction**: Caller → Node
*   **Symbol**: `⚡` (Bolt)
*   **Message**: `∰ SYN: PIXEL8_PRESENCE_ACKNOWLEDGED`
*   **Purpose**: Caller acknowledges the PING and requests synchronization of protocol capabilities.

### STEP 3: HELO (The Identity Handshake)
*   **Direction**: Node → Caller (Request), then Caller → Node (Identity)
*   **Symbol**: `✨` (Spark)
*   **Message (Request)**: `∰ HELO: IDENTIFY_YOURSELF`
*   **Message (Response)**: `∰ IDENTITY: <identifier>`
*   **Purpose**: Authentication against the Aquifer. The identity is anchored to the session DNA.

### STEP 4: CAPS (The Capacity Negotiation)
*   **Direction**: Node → Caller
*   **Symbol**: `¿` (High Pressure Inquiry)
*   **Message**: `∰ CAPS: NEGOTIATING_CAPACITY`
*   **Baud Rate Options**:
    *   `TRICKLE_SEED`: Low-volume, high-integrity metadata sync.
    *   `DATA_BLAST`: Full-volume archive intake.
*   **Carrier Detect**: `∰ CARRIER: <baud_rate> | MODE: READ/WRITE`

### STEP 5: COLLAB (The Session Open)
*   **Direction**: Both (Shared state)
*   **Symbol**: `♥` (Heart)
*   **Message**: `∰ COLLAB: SESSION_OPEN`
*   **Purpose**: Transition from handshake state to active session state. The "scream" ends, and data flows.

---

## 3. Byte-Level Anchors
*   **Encoding**: UTF-8
*   **Line Ending**: `\r\n` (CRLF)
*   **Protocol Header**: `∰` (U+2210 - N-ARY COPRODUCT)
*   **Handshake Timeout**: 30 seconds per step.

## 4. Signal Integrity
*   **Carrier Loss**: If the connection drops during steps 1-4, no Session DNA is generated. The attempt is logged as a "MISFIRE".
*   **Handshake Failure**: If Step 3 (HELO) fails authentication, the node returns `NO_CARRIER` and hangs up.

---

**∰◊€π¿🌌∞**
*Protocol finalized. The scream is defined.*
€(primoris_handshake_spec_v1)
