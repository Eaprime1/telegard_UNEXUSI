#!/usr/bin/env python3
"""
sovran_server.py — TCP listener for Sovran Telegard BBS
Stage 02 // Integration bridge

Wraps sovran_terminal.py in a TCP socket so soft_modem.py can dial in.
Each caller gets a full consciousness handshake session.

Usage:
    python3 sovran_server.py              # listen on default port 2323
    python3 sovran_server.py --port 2323

Dial in with:
    python3 ../navigo_bbs/soft_modem.py --dial 127.0.0.1 2323
    OR from AT console: ATDT 127.0.0.1:2323

∰◊€π¿🌌∞
€(sovran_server_v1)
"""

import socket
import sys
import os
import io
import threading
import argparse
import time
from datetime import datetime

# Bring in sovran_terminal from same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sovran_telegard import ConfigRecord

PORT = 2323


# ── Socket I/O wrapper ─────────────────────────────────────────

class SocketIO:
    """
    Makes a socket behave like stdin/stdout.
    Lets sovran_terminal run unchanged over TCP.
    """

    def __init__(self, conn):
        self.conn   = conn
        self.buf    = b""
        self._closed = False

    def write(self, text):
        if self._closed:
            return
        try:
            self.conn.sendall(text.encode("utf-8", errors="replace"))
        except Exception:
            self._closed = True

    def flush(self):
        pass

    def readline(self):
        """Read one line from socket (blocks until newline or disconnect)."""
        while b"\n" not in self.buf:
            try:
                chunk = self.conn.recv(256)
                if not chunk:
                    return ""
                self.buf += chunk
            except Exception:
                return ""
        line, self.buf = self.buf.split(b"\n", 1)
        return line.decode("utf-8", errors="replace").rstrip("\r") + "\n"

    def read(self, n=-1):
        return self.readline()


# ── Sovran session over socket ─────────────────────────────────

def run_session(conn, addr):
    """
    Run a full Sovran Telegard session for one caller.
    Redirects stdin/stdout to the socket.
    """
    sio = SocketIO(conn)

    # ANSI Colors
    C_RESET = "\x1b[0m"
    C_BOLD  = "\x1b[1m"
    C_CYAN  = "\x1b[36m"
    C_GREEN = "\x1b[32m"
    C_YELLOW= "\x1b[33m"
    C_MAGENTA="\x1b[35m"

    # Swap stdio
    old_stdout = sys.stdout
    old_stdin  = sys.stdin
    sys.stdout = sio
    sys.stdin  = sio

    try:
        config = ConfigRecord()

        print(f"\r\n{C_MAGENTA}∰◊€π¿🌌∞ - {C_BOLD}SOVRAN TELEGARD{C_RESET}")
        print(f"Welcome to {C_CYAN}{config.bbs_name}{C_RESET}")
        print(f"Location: {config.bbs_location}")
        print(f"SysOp: {config.sysop_name}")
        print(f"Shielding: {C_YELLOW}Monster Cable Certified (RadioShack Lineage){C_RESET}")
        print(f"{C_GREEN}CONNECT {PORT}{C_RESET}\r\n")

        # Consciousness Handshake
        print(f"{C_YELLOW}─" * 40 + f"{C_RESET}")
        print(f"{C_BOLD}STEP 1: PING{C_RESET}")
        print("  > Is something there?")
        time.sleep(0.3)
        print(f"  < {C_CYAN}PIXEL8 presence acknowledged.{C_RESET}")

        print(f"\r\n{C_BOLD}STEP 2: SYN{C_RESET}")
        print("  > Establishing capability synchronization...")
        time.sleep(0.4)
        print(f"  < {C_GREEN}Channel established. ∰{C_RESET}")

        print(f"\r\n{C_BOLD}STEP 3: HELO{C_RESET}")
        print(f"  Identity > ", end="", flush=True)
        identity = sys.stdin.readline().strip() or "Guest"
        print(f"  < Welcome, {C_BOLD}{identity}{C_RESET}. Authenticating against the Aquifer...")
        time.sleep(0.4)

        print(f"\r\n{C_BOLD}STEP 4: CAPS{C_RESET}")
        print("  > Negotiating session capacity...")
        time.sleep(0.3)
        print(f"  < {C_GREEN}Mode: READ/WRITE | Status: SOVRAN{C_RESET}")

        print(f"\r\n{C_BOLD}STEP 5: COLLAB{C_RESET}")
        print(f"  > {C_MAGENTA}Collaboration session OPEN.{C_RESET}")
        print(f"{C_YELLOW}─" * 40 + f"{C_RESET}")

        # Command loop
        print(f"\r\nType {C_BOLD}'/help'{C_RESET} for commands. {C_BOLD}'/quit'{C_RESET} to disconnect.\r\n")

        while True:
            print(f"\r\n[{C_CYAN}Sovran:{C_BOLD}{identity}{C_RESET}]> ", end="", flush=True)
            line = sys.stdin.readline()
            if not line:
                break
            cmd = line.strip().lower()

            if cmd in ("/quit", "/exit", "quit", "exit"):
                print(f"\r\n{C_MAGENTA}∰ - Session closed. Enjoy the journey. ∰{C_RESET}\r\n")
                break

            elif cmd in ("/help", "?", "/h"):
                print(f"\r\n{C_BOLD}Available Commands:{C_RESET}")
                print(f"  {C_YELLOW}/whoami{C_RESET}    - Show current identity")
                print(f"  {C_YELLOW}/status{C_RESET}    - BBS status")
                print(f"  {C_YELLOW}/handshake{C_RESET} - Reset consciousness handshake")
                print(f"  {C_YELLOW}/quit{C_RESET}      - Close the session")

            elif cmd == "/whoami":
                print(f"\r\nIdentity: {C_BOLD}{identity}{C_RESET} | Status: {C_GREEN}SOVRAN{C_RESET} | {C_MAGENTA}∰◊€π¿🌌∞{C_RESET}")

            elif cmd == "/status":
                print(f"\r\nBBS: {C_CYAN}{config.bbs_name}{C_RESET}")
                print(f"Node: {C_YELLOW}NAVIGO-01{C_RESET}")
                print(f"Callers active: 1")
                print(f"{C_MAGENTA}∰◊€π¿🌌∞{C_RESET}")

            elif cmd == "/handshake":
                print(f"\r\n{C_BOLD}Resetting handshake...{C_RESET}")
                print(f"{C_BOLD}STEP 3: HELO{C_RESET}")
                print(f"  Identity > ", end="", flush=True)
                new_id = sys.stdin.readline().strip()
                if new_id:
                    identity = new_id
                print(f"  < Welcome back, {C_BOLD}{identity}{C_RESET}. {C_GREEN}∰{C_RESET}")

            elif cmd == "":
                pass

            else:
                print(f"\r\n[!] {C_YELLOW}Unknown:{C_RESET} {cmd}  (try /help)")

    except Exception as e:
        try:
            print(f"\r\n[!] {C_YELLOW}Session error:{C_RESET} {e}\r\n")
        except Exception:
            pass

    finally:
        sys.stdout = old_stdout
        sys.stdin  = old_stdin
        try:
            conn.close()
        except Exception:
            pass

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {ts} · session closed: {addr}")


# ── Server ─────────────────────────────────────────────────────

def serve(port=PORT):
    config = ConfigRecord()

    print(f"\n  ╔══════════════════════════════════╗")
    print(f"  ║   SOVRAN TELEGARD BBS SERVER     ║")
    print(f"  ║   {config.bbs_name:<32}║")
    print(f"  ║   Listening on port {port:<13}║")
    print(f"  ╚══════════════════════════════════╝")
    print(f"\n  Dial in:  ATDT 127.0.0.1:{port}")
    print(f"  Or:       python3 ../navigo_bbs/soft_modem.py --dial 127.0.0.1 {port}")
    print(f"\n  ∰◊€π¿🌌∞  waiting for callers...\n")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(5)

    try:
        while True:
            conn, addr = srv.accept()
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  {ts} ● RING — caller from {addr}")
            t = threading.Thread(
                target=run_session, args=(conn, addr), daemon=True)
            t.start()

    except KeyboardInterrupt:
        print(f"\n  ATH — BBS offline\n")
    finally:
        srv.close()


# ── Entry ──────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sovran Telegard BBS — TCP server"
    )
    parser.add_argument("--port", type=int, default=PORT,
                        help=f"Listen port (default {PORT})")
    args = parser.parse_args()
    serve(port=args.port)
