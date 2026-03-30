#!/usr/bin/env python3
"""
soft_modem.py — Navigo BBS Soft Modem
Stage 02 // Iteration 1

A virtual Hayes-compatible modem for the PRIMORIS BBS stack.
Mimics the dialup interaction pattern over TCP sockets.

State machine:
  INIT → DIAL → HANDSHAKE → CONNECTED → SESSION → HANGUP

Philosophy: The modem screamed into the wire before it could listen.
That scream WAS the protocol. — Primoris Navigo Plan

Usage:
    python3 soft_modem.py               # interactive AT command mode
    python3 soft_modem.py --dial HOST PORT  # dial a BBS
    python3 soft_modem.py --listen PORT     # answer mode (be the BBS)

Iteration 1 scope:
    - State machine
    - AT command parser (core Hayes subset)
    - Connection log
    - TCP dial + answer

Next iteration (Iteration 2):
    - ANSI terminal emulator
    - Baud rate negotiation simulation
    - Session content archiver
"""

import socket
import sys
import time
import threading
import json
import hashlib
import uuid
import argparse
import re
from datetime import datetime
from enum import Enum, auto
from pathlib import Path


# ── ANSI Terminal Support ──────────────────────────────────────

class ANSITerminal:
    """
    Minimal ANSI escape sequence processor.
    Handles standard SGR (Select Graphic Rendition) for colors/styles.
    """
    
    # ANSI escape regex: ESC [ [params] m
    ANSI_SGR_RE = re.compile(r'\x1b\[([\d;]*)m')
    
    # Mapping of ANSI SGR codes to basic descriptions (for logging)
    SGR_CODES = {
        "0":  "reset",
        "1":  "bold",
        "4":  "underline",
        "5":  "blink",
        "7":  "reverse",
        "30": "black", "31": "red", "32": "green", "33": "yellow",
        "34": "blue",  "35": "magenta", "36": "cyan", "37": "white",
        "40": "bg_black", "41": "bg_red", "42": "bg_green", "43": "bg_yellow",
        "44": "bg_blue",  "45": "bg_magenta", "46": "bg_cyan", "47": "bg_white"
    }

    @classmethod
    def strip(cls, text):
        """Strip all ANSI SGR sequences from text."""
        return cls.ANSI_SGR_RE.sub('', text)

    @classmethod
    def get_styles(cls, text):
        """Identify all SGR styles used in a string."""
        codes = []
        for match in cls.ANSI_SGR_RE.finditer(text):
            params = match.group(1).split(';')
            for p in params:
                if p in cls.SGR_CODES:
                    codes.append(cls.SGR_CODES[p])
        return codes


# ── State Machine ──────────────────────────────────────────────

class ModemState(Enum):
    INIT       = "INIT"        # Ready, awaiting AT commands
    DIAL       = "DIAL"        # Processing ATDT, dialing
    HANDSHAKE  = "HANDSHAKE"   # Negotiating connection
    CONNECTED  = "CONNECTED"   # Data connection established
    SESSION    = "SESSION"     # Active BBS session
    HANGUP     = "HANGUP"      # Terminating connection


# ── AT Response Codes (Hayes standard) ────────────────────────

class ATResponse:
    OK           = "OK"
    ERROR        = "ERROR"
    CONNECT      = "CONNECT"
    NO_CARRIER   = "NO CARRIER"
    NO_DIALTONE  = "NO DIALTONE"
    BUSY         = "BUSY"
    NO_ANSWER    = "NO ANSWER"
    RING         = "RING"


# ── Session Log ────────────────────────────────────────────────

class SessionLog:
    """
    Chain-of-custody session logger.
    Every exchange archived — PRIMORIS principle: additive only.
    """

    def __init__(self, log_dir=None):
        if log_dir is None:
            log_dir = Path.home() / ".navigo_bbs" / "sessions"
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.session_id  = str(uuid.uuid4())[:8]
        self.started_at  = datetime.now().isoformat()
        self.entries     = []
        self.log_file    = self.log_dir / f"session_{self.session_id}.json"
        self.identity    = "Unknown"
        self.outcome     = "ACTIVE"
        self._running_hash = hashlib.sha256(self.session_id.encode()).hexdigest()

        self._write()

    def set_identity(self, identity):
        """Update identity once established by handshake."""
        self.identity = identity
        self.event("SYS", f"Identity established: {identity}")

    def set_outcome(self, outcome):
        """Set the final outcome of the session."""
        self.outcome = outcome
        self.event("SYS", f"Session outcome: {outcome}")

    def event(self, direction, content, state=None):
        """
        Log a modem event.
        direction: 'AT' (command sent), 'RESP' (response received),
                   'DATA' (session data), 'STATE' (state change), 'SYS'
        """
        # Calculate incremental hash
        payload = f"{direction}{content}{state or ''}".encode('utf-8', errors='replace')
        entry_hash = hashlib.sha256(payload).hexdigest()[:12]
        
        # Update running hash
        self._running_hash = hashlib.sha256((self._running_hash + entry_hash).encode()).hexdigest()

        entry = {
            "ts":        datetime.now().isoformat(),
            "direction": direction,
            "content":   content,
            "state":     state,
            "hash":      entry_hash
        }
        self.entries.append(entry)
        self._write()

        # Console display
        ts = entry["ts"][11:19]
        icons = {
            "AT":    "▶",
            "RESP":  "◀",
            "DATA":  "~",
            "STATE": "●",
            "SYS":   "·"
        }
        icon = icons.get(direction, "?")
        print(f"  {ts} {icon} [{direction}] {content}")

    def generate_dna(self):
        """
        Slot 06: BBS Session DNA
        Generate a unique manifest representing the session essence.
        """
        total_tx = sum(len(e['content']) for e in self.entries if e['direction'] == 'DATA' and e['content'].startswith('TX:'))
        total_rx = sum(len(e['content']) for e in self.entries if e['direction'] == 'DATA' and e['content'].startswith('RX:'))
        
        # Monster Cable Integrity Check
        integrity_score = "MAXIMUM" if len(self._running_hash) == 64 else "DEGRADED"
        
        dna = {
            "session_id": self.session_id,
            "identity":   self.identity,
            "started_at": self.started_at,
            "finished_at": datetime.now().isoformat(),
            "outcome":    self.outcome,
            "metrics": {
                "tx_bytes": total_tx,
                "rx_bytes": total_rx,
                "event_count": len(self.entries),
                "shielding": "Monster Cable Certified (RadioShack Lineage)"
            },
            "integrity": {
                "final_hash": self._running_hash,
                "score": integrity_score,
                "protocol": "PRIMORIS_DNA_v1"
            },
            "signature": f"∰◊€π¿🌌∞::{self.identity}::{self.session_id}"
        }
        return dna

    def _write(self):
        try:
            manifest = {
                "session_id": self.session_id,
                "identity":   self.identity,
                "started_at": self.started_at,
                "outcome":    self.outcome,
                "running_hash": self._running_hash,
                "entry_count": len(self.entries),
                "entries": self.entries
            }
            
            # If session is finished, include DNA
            if self.outcome != "ACTIVE":
                manifest["session_dna"] = self.generate_dna()

            with open(self.log_file, "w") as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            # Avoid infinite recursion if event() fails
            print(f"  [!] Log write error: {e}")


# ── AT Command Parser ──────────────────────────────────────────

class ATParser:
    """
    Hayes AT command subset parser.
    Real modems were remarkably terse. We honor that.
    """

    COMMANDS = {
        "ATZ":    "reset",
        "ATI":    "identify",
        "AT&F":   "factory_reset",
        "ATE0":   "echo_off",
        "ATE1":   "echo_on",
        "ATH":    "hangup",
        "ATH0":   "hangup",
        "ATA":    "answer",
        "AT+MS":  "modulation_select",
    }

    @classmethod
    def parse(cls, raw):
        """
        Parse an AT command string.
        Returns (command_type, params) or ('unknown', raw)
        """
        cmd = raw.strip().upper()

        if not cmd.startswith("AT"):
            return ("not_at", raw)

        # ATDT/ATDP — dial
        if cmd.startswith("ATDT") or cmd.startswith("ATDP"):
            number = raw.strip()[4:].strip()
            mode   = "tone" if "T" in cmd[:5] else "pulse"
            return ("dial", {"number": number, "mode": mode})

        # Direct lookup
        for at_cmd, name in cls.COMMANDS.items():
            if cmd == at_cmd or cmd.startswith(at_cmd + " "):
                return (name, {})

        # AT alone = ping
        if cmd == "AT":
            return ("ping", {})

        return ("unknown", raw)


# ── Soft Modem ─────────────────────────────────────────────────

class SoftModem:
    """
    Virtual Hayes-compatible modem.

    Iteration 1: State machine + TCP dial/answer + AT parsing + session log.
    Iteration 2: Will add ANSI emulation, baud negotiation, content archiver.
    """

    VERSION = "0.1.0-iter1"
    BAUD_RATES = [300, 1200, 2400, 9600, 14400, 28800, 33600, 56000]

    def __init__(self, baud=2400, log_dir=None):
        self.state      = ModemState.INIT
        self.baud       = baud
        self.log        = SessionLog(log_dir)
        self.conn       = None   # active socket
        self.echo       = True   # ATE1 default
        self.host       = None
        self.port       = None
        self.process_ansi = True # New: handle ANSI sequences

        self._transition(ModemState.INIT, "modem ready")

    # ── State ──────────────────────────────────────────────────

    def _transition(self, new_state, reason=""):
        old = self.state.value if self.state else "—"
        self.state = new_state
        self.log.event("STATE",
                       f"{old} → {new_state.value}  ({reason})",
                       state=new_state.value)

    # ── AT Command Handling ────────────────────────────────────

    def send_at(self, raw):
        """Process an AT command. Returns response string."""
        if self.echo:
            print(f"\n  > {raw}")

        self.log.event("AT", raw, state=self.state.value)

        cmd_type, params = ATParser.parse(raw)

        handlers = {
            "ping":          self._at_ping,
            "reset":         self._at_reset,
            "identify":      self._at_identify,
            "factory_reset": self._at_reset,
            "echo_off":      lambda p: self._set_echo(False),
            "echo_on":       lambda p: self._set_echo(True),
            "hangup":        self._at_hangup,
            "answer":        self._at_answer,
            "dial":          self._at_dial,
            "not_at":        lambda p: ATResponse.ERROR,
            "unknown":       lambda p: ATResponse.ERROR,
        }

        handler  = handlers.get(cmd_type, lambda p: ATResponse.ERROR)
        response = handler(params)
        self.log.event("RESP", response, state=self.state.value)
        return response

    def _at_ping(self, _):
        return ATResponse.OK

    def _at_reset(self, _):
        if self.conn:
            self.conn.close()
            self.conn = None
        self._transition(ModemState.INIT, "ATZ reset")
        return ATResponse.OK

    def _at_identify(self, _):
        return f"Navigo Soft Modem {self.VERSION} / PRIMORIS BBS Stack"

    def _set_echo(self, val):
        self.echo = val
        return ATResponse.OK

    def _at_hangup(self, _):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None
        self._transition(ModemState.HANGUP, "ATH")
        self._transition(ModemState.INIT, "ready")
        return ATResponse.OK

    def _at_answer(self, _):
        self.log.event("SYS", "ATA — answer mode not in dial context")
        return ATResponse.ERROR

    def _at_dial(self, params):
        number = params.get("number", "")
        mode   = params.get("mode", "tone")

        # Parse host:port from "number"
        # Supports: 192.168.1.5:2323  or  bbs.example.com:23
        if ":" in number:
            parts = number.rsplit(":", 1)
            host  = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return ATResponse.ERROR
        else:
            host = number
            port = 23  # telnet default

        return self._dial(host, port, mode)

    # ── TCP Dial ───────────────────────────────────────────────

    def _dial(self, host, port, mode="tone"):
        """
        Establish TCP connection to BBS host:port.
        Simulates Hayes dialup sequence with timing.
        """
        self._transition(ModemState.DIAL,
                         f"ATDT {host}:{port} ({mode})")

        # Simulated dial tone + dialing
        self.log.event("SYS", f"DIALING {host}:{port}")
        self._dial_tone_sequence(host)

        # TCP connect
        try:
            self.log.event("SYS", "connecting...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((host, port))
            self.conn = sock
            self.host = host
            self.port = port
        except socket.timeout:
            self._transition(ModemState.INIT, "timeout")
            return ATResponse.NO_ANSWER
        except ConnectionRefusedError:
            self._transition(ModemState.INIT, "refused")
            return ATResponse.NO_CARRIER
        except socket.gaierror:
            self._transition(ModemState.INIT, "host not found")
            return ATResponse.NO_DIALTONE
        except Exception as e:
            self._transition(ModemState.INIT, f"error: {e}")
            return ATResponse.NO_CARRIER

        # Handshake negotiation
        self._transition(ModemState.HANDSHAKE, "TCP connected")
        negotiated_baud = self._negotiate_baud()

        self._transition(ModemState.CONNECTED,
                         f"baud={negotiated_baud}")
        return f"{ATResponse.CONNECT} {negotiated_baud}"

    def _dial_tone_sequence(self, host):
        """Simulate the classic modem dial tone sequence."""
        chars = f"ATDT{host}"
        self.log.event("SYS", "♪ dialing tones...")
        # In a real version this would generate actual DTMF tones
        time.sleep(0.3)

    def _negotiate_baud(self):
        """
        Simulate baud rate handshake.
        Iteration 2 will do real capability exchange.
        For now: agree on configured baud.
        """
        self.log.event("SYS",
                       f"♪ HANDSHAKE — negotiating baud rate...")
        time.sleep(0.5)  # simulated negotiation time
        agreed = self.baud
        self.log.event("SYS", f"CARRIER {agreed}")
        return agreed

    # ── Session (once CONNECTED) ───────────────────────────────

    def session_loop(self):
        """
        Interactive session once connected.
        Iteration 2 will add ANSI rendering here.
        """
        if self.state != ModemState.CONNECTED:
            print("  Not connected.")
            return

        self._transition(ModemState.SESSION, "session start")
        print(f"\n  ── SESSION OPEN ──  (type ~~. to disconnect)\n")

        # Thread: receive from BBS
        self._recv_active = True
        recv_thread = threading.Thread(
            target=self._recv_loop, daemon=True)
        recv_thread.start()

        # Main thread: send to BBS
        outcome = "NORMAL_DISCONNECT"
        try:
            first_input = True
            while self.state == ModemState.SESSION:
                try:
                    line = input()
                except EOFError:
                    outcome = "EOF_DISCONNECT"
                    break
                except KeyboardInterrupt:
                    outcome = "INTERRUPT_DISCONNECT"
                    break

                if line == "~~.":
                    break

                # Heuristic: First input after connect is often the identity
                if first_input:
                    self.log.set_identity(line)
                    first_input = False

                self.log.event("DATA", f"TX: {line}")
                try:
                    self.conn.sendall((line + "\r\n").encode("utf-8",
                                                              errors="replace"))
                except Exception:
                    outcome = "CONNECTION_LOST"
                    break

        finally:
            self._recv_active = False
            self.log.set_outcome(outcome)
            self.send_at("ATH")

        print(f"\n  ── SESSION CLOSED: {outcome} ──")
        print(f"  Log: {self.log.log_file}")

    def _recv_loop(self):
        """Background thread: receive BBS output."""
        buf = b""
        while self._recv_active and self.conn:
            try:
                chunk = self.conn.recv(256)
                if not chunk:
                    break
                buf += chunk
                # Flush complete lines
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    text_raw = line.decode("utf-8", errors="replace").rstrip("\r")
                    
                    # Log clean text, but display raw (for ANSI)
                    text_clean = ANSITerminal.strip(text_raw)
                    styles = ANSITerminal.get_styles(text_raw)
                    style_info = f" [{','.join(styles)}]" if styles else ""
                    
                    self.log.event("DATA", f"RX: {text_clean}{style_info}")
                    print(f"\r  {text_raw}")
            except socket.timeout:
                continue
            except Exception:
                break

    # ── Listen / Answer Mode ───────────────────────────────────

    def listen(self, port=2323):
        """
        Answer mode — act as the BBS endpoint.
        Listens for incoming connections.
        """
        self.log.event("SYS", f"ANSWER MODE — listening on port {port}")
        print(f"\n  Navigo BBS — listening on port {port}")
        print(f"  Dial: ATDT 127.0.0.1:{port}\n")

        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", port))
        srv.listen(1)

        try:
            while True:
                conn, addr = srv.accept()
                self.log.event("RESP",
                               f"{ATResponse.RING} from {addr}")
                print(f"\n  {ATResponse.RING} — {addr}")
                self._handle_incoming(conn, addr)
        except KeyboardInterrupt:
            print("\n  ATH — modem offline")
        finally:
            srv.close()

    def _handle_incoming(self, conn, addr):
        """Handle one incoming BBS caller."""
        self.conn = conn
        self._transition(ModemState.HANDSHAKE,
                         f"incoming from {addr}")
        self._negotiate_baud()
        self._transition(ModemState.CONNECTED, f"caller {addr}")
        self._transition(ModemState.SESSION, "session")

        # Send banner
        banner = (
            "\r\n"
            "╔══════════════════════════════════╗\r\n"
            "║   NAVIGO BBS — PRIMORIS NODE     ║\r\n"
            "║   Suxen Adventure // Stage 02    ║\r\n"
            "║   ∰◊€π¿🌌∞                       ║\r\n"
            "╚══════════════════════════════════╝\r\n"
            "\r\n"
            "CONNECT " + str(self.baud) + "\r\n"
        )
        try:
            conn.sendall(banner.encode("utf-8"))
        except Exception:
            pass

        # Echo session
        outcome = "NORMAL_DISCONNECT"
        try:
            while True:
                data = conn.recv(256)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace")
                
                # Heuristic for listener: try to find identity in first data chunk
                if self.log.identity == "Unknown":
                    # Simple assumption: identity is the first word if it looks like a name
                    potential_id = text.strip().split()[0] if text.strip() else ""
                    if potential_id:
                        self.log.set_identity(potential_id)

                self.log.event("DATA", f"RX from {addr}: {text!r}")
                conn.sendall(data)  # echo back
        except Exception as e:
            outcome = f"ERROR: {e}"
        finally:
            self.log.set_outcome(outcome)
            conn.close()
            self._transition(ModemState.HANGUP, f"caller {addr} disconnected")
            self._transition(ModemState.INIT, "ready")

    # ── Status ─────────────────────────────────────────────────

    def status(self):
        print(f"\n  ══ Navigo Soft Modem {self.VERSION} ══")
        print(f"  State:    {self.state.value}")
        print(f"  Baud:     {self.baud}")
        print(f"  Session:  {self.log.session_id}")
        print(f"  Log:      {self.log.log_file}")
        if self.host:
            print(f"  Remote:   {self.host}:{self.port}")
        print(f"  ∰◊€π¿🌌∞\n")


# ── Interactive AT Console ─────────────────────────────────────

def at_console(modem):
    """Interactive Hayes AT command console."""
    print(f"\n  Navigo Soft Modem {SoftModem.VERSION}")
    print(f"  AT command mode — type 'quit' to exit")
    print(f"")
    print(f"  Dial:   ATDT 127.0.0.1:2323   (or shorthand: d 127.0.0.1:2323)")
    print(f"  Status: ATI   Hang up: ATH   Reset: ATZ")
    print(f"")
    modem.status()

    while True:
        try:
            raw = input("AT> ")
        except (EOFError, KeyboardInterrupt):
            print("\n  ATH")
            break

        raw = raw.strip()

        if raw.lower() in ("quit", "exit", "q"):
            break

        if raw == "":
            continue

        # ── Friendly shorthands ──────────────────────────────
        # Allow: d 127.0.0.1:2323  →  ATDT 127.0.0.1:2323
        if raw.lower().startswith("d "):
            raw = "ATDT " + raw[2:].strip()
        # Allow: 127.0.0.1:2323  (bare address)
        elif "." in raw and ":" in raw and not raw.upper().startswith("AT"):
            raw = "ATDT " + raw
        # Allow: connect HOST PORT
        elif raw.lower().startswith("connect "):
            parts = raw.split()
            if len(parts) == 3:
                raw = f"ATDT {parts[1]}:{parts[2]}"

        resp = modem.send_at(raw)
        print(f"  {resp}")

        if "CONNECT" in resp and modem.state == ModemState.CONNECTED:
            modem.session_loop()


# ── Entry Point ────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Navigo Soft Modem — PRIMORIS BBS Stack // Stage 02 Iter 1"
    )
    parser.add_argument("--dial",   nargs=2,
                        metavar=("HOST", "PORT"),
                        help="Dial a BBS: --dial 127.0.0.1 2323")
    parser.add_argument("--listen", type=int,
                        metavar="PORT",
                        help="Answer mode: --listen 2323")
    parser.add_argument("--baud",   type=int, default=2400,
                        help="Baud rate (default 2400)")
    parser.add_argument("--status", action="store_true",
                        help="Show modem status and exit")
    args = parser.parse_args()

    modem = SoftModem(baud=args.baud)

    if args.status:
        modem.status()

    elif args.listen:
        modem.listen(port=args.listen)

    elif args.dial:
        host, port = args.dial[0], int(args.dial[1])
        resp = modem._dial(host, port)
        print(f"\n  {resp}")
        if "CONNECT" in resp:
            modem.session_loop()

    else:
        at_console(modem)
