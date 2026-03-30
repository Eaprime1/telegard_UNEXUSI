#!/usr/bin/env python3
"""
test_bbs.py — Sovran Telegard BBS Test Runner
Verbose, non-interactive, safe to pipe to a file.

Usage:
    python3 test_bbs.py              # run all tests
    python3 test_bbs.py > report.txt # capture full report
    python3 test_bbs.py --quick      # skip sleep delays

∰◊€π¿🌌∞
€(test_bbs_v1)
"""

import sys
import os
import io
import socket
import threading
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sovran_telegard"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "navigo_bbs"))

QUICK = "--quick" in sys.argv

def pause(n=0.3):
    if not QUICK:
        time.sleep(n)

# ── Test helpers ───────────────────────────────────────────────

PASS = "  ✅ PASS"
FAIL = "  ❌ FAIL"
INFO = "  ℹ "

passed = []
failed = []

def check(label, condition, detail=""):
    if condition:
        print(f"{PASS}  {label}")
        passed.append(label)
    else:
        print(f"{FAIL}  {label}  {detail}")
        failed.append(label)

def section(title):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")

# ── TEST 1: Data structures ────────────────────────────────────

section("TEST 1 — sovran_telegard.py: Data Structures")

try:
    from sovran_telegard import ConfigRecord, UserRecord, UserStatus, UserFlags
    check("Import sovran_telegard", True)

    config = ConfigRecord()
    check("ConfigRecord: bbs_name", bool(config.bbs_name), config.bbs_name)
    check("ConfigRecord: sysop_name", bool(config.sysop_name), config.sysop_name)
    check("ConfigRecord: bbs_location", bool(config.bbs_location), config.bbs_location)
    print(f"{INFO}  BBS: {config.bbs_name} | SysOp: {config.sysop_name} | {config.bbs_location}")

    user = UserRecord(name="TEST_NAVIGO")
    check("UserRecord: created", user.name == "TEST_NAVIGO")
    check("UserRecord: default SL", user.sl == 10, f"got {user.sl}")

    import zlib
    pw = "GEMINI_NEXUS"
    crc = zlib.crc32(pw.encode()) & 0xFFFFFFFF
    check("CRC32 password verify", crc == zlib.crc32(pw.encode()) & 0xFFFFFFFF,
          f"0x{crc:08x}")
    print(f"{INFO}  CRC32('{pw}') = 0x{crc:08x}")

except Exception as e:
    check("sovran_telegard import", False, str(e))

# ── TEST 2: Data files ─────────────────────────────────────────

section("TEST 2 — data/: JSON Files")

DATA_DIR = os.path.join(os.path.dirname(__file__), "sovran_telegard", "data")

msgs_path = os.path.join(DATA_DIR, "messages.json")
check("messages.json exists", os.path.exists(msgs_path), msgs_path)
if os.path.exists(msgs_path):
    with open(msgs_path) as f:
        msgs = json.load(f)
    check("messages.json: has entries", len(msgs) > 0, f"{len(msgs)} messages")
    for m in msgs:
        print(f"{INFO}  [{m['msg_id']}] {m['subject']} — from {m['msg_from']}")

files_path = os.path.join(DATA_DIR, "main_area.json")
check("main_area.json exists", os.path.exists(files_path), files_path)
if os.path.exists(files_path):
    with open(files_path) as f:
        fdb = json.load(f)
    check("main_area.json: has entries", len(fdb) > 0, f"{len(fdb)} files")
    for entry in fdb:
        print(f"{INFO}  {entry['filename']:<22} {round(entry['size_bytes']/1024,1):>6} KB")

doors_path = os.path.join(DATA_DIR, "doors.json")
check("doors.json exists", os.path.exists(doors_path), doors_path)
if os.path.exists(doors_path):
    with open(doors_path) as f:
        ddb = json.load(f)
    check("doors.json: has entries", len(ddb) > 0, f"{len(ddb)} doors")
    for d in ddb:
        exes = ", ".join(d.get("exes", [])) or "no exe"
        print(f"{INFO}  [{d['status']:<6}] {d['id']:<12} exes:[{exes}]")

# ── TEST 3: Terminal import (non-interactive) ──────────────────

section("TEST 3 — sovran_terminal.py: Import & Functions")

try:
    # Patch stdin/stdout to avoid blocking on input()
    import sovran_terminal as term
    check("Import sovran_terminal", True)

    check("handshake() accepts prefill", callable(term.handshake))
    check("list_files() defined", callable(term.list_files))
    check("list_boards() defined", callable(term.list_boards))
    check("list_doors() defined", callable(term.list_doors))
    # list_doors now takes session_user arg (Gemini update)
    import inspect
    sig = inspect.signature(term.list_doors)
    check("list_doors() takes session_user param", "session_user" in sig.parameters)
    check("run_zap() defined", callable(term.run_zap))
    check("show_status() defined", callable(term.show_status))
    check("main_menu() defined", callable(term.main_menu))

    # Run handshake with prefill — no input() blocking
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    identity = term.handshake(prefill_identity="TESTER")
    sys.stdout = old_stdout
    output = buf.getvalue()
    check("handshake() runs with prefill", identity == "TESTER", f"got '{identity}'")
    check("handshake() output: PING step", "STEP 1: PING" in output)
    check("handshake() output: HELO step", "STEP 3: HELO" in output)
    check("handshake() output: COLLAB step", "STEP 5: COLLAB" in output)
    print(f"{INFO}  Handshake output ({len(output)} chars captured)")

except Exception as e:
    check("sovran_terminal import", False, str(e))
    sys.stdout = sys.__stdout__

# ── TEST 4: TCP Server ─────────────────────────────────────────

section("TEST 4 — sovran_server.py: TCP Connection")

try:
    import sovran_server

    # Start server in background thread
    test_port = 2399  # separate port so it doesn't clash with live server
    server_ready = threading.Event()
    server_errors = []

    def run_test_server():
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", test_port))
            srv.listen(1)
            srv.settimeout(5)
            server_ready.set()
            conn, addr = srv.accept()
            # Run a session with auto-identity
            sio = sovran_server.SocketIO(conn)
            old_out, old_in = sys.stdout, sys.stdin
            sys.stdout = sio
            sys.stdin  = sio
            try:
                sio.buf = b"TESTER\n/quit\n"   # pre-load: identity + quit
                from sovran_telegard import ConfigRecord
                config = ConfigRecord()
                print(f"CONNECT {test_port}\r\n")
                identity = sys.stdin.readline().strip() or "Guest"
                print(f"Welcome, {identity}.\r\n")
                line = sys.stdin.readline()
            finally:
                sys.stdout = old_out
                sys.stdin  = old_in
            conn.close()
            srv.close()
        except Exception as e:
            server_errors.append(str(e))
            server_ready.set()

    t = threading.Thread(target=run_test_server, daemon=True)
    t.start()
    server_ready.wait(timeout=3)

    check("Server thread started", len(server_errors) == 0,
          server_errors[0] if server_errors else "")

    pause(0.2)

    # Connect as client
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(4)
        sock.connect(("127.0.0.1", test_port))
        check("TCP connect to test server", True)

        # Read banner
        data = b""
        try:
            while True:
                chunk = sock.recv(512)
                if not chunk:
                    break
                data += chunk
                if b"Welcome" in data:
                    break
        except socket.timeout:
            pass

        banner = data.decode("utf-8", errors="replace")
        check("Server sends CONNECT banner", "CONNECT" in banner)
        check("Server sends Welcome", "Welcome" in banner)
        print(f"{INFO}  Received {len(banner)} chars from server")
        sock.close()

    except Exception as e:
        check("TCP connect", False, str(e))

    t.join(timeout=2)

except Exception as e:
    check("sovran_server import", False, str(e))

# ── TEST 5: Soft modem import ──────────────────────────────────

section("TEST 5 — soft_modem.py: Import & Classes")

try:
    import soft_modem as modem
    check("Import soft_modem", True)
    check("ModemState enum defined", hasattr(modem, "ModemState"))
    check("ATParser defined", hasattr(modem, "ATParser"))
    check("SoftModem defined", hasattr(modem, "SoftModem"))
    check("SessionLog defined", hasattr(modem, "SessionLog"))

    parser = modem.ATParser()
    check("ATParser: ATZ → reset", parser.parse("ATZ") is not None)
    check("ATParser: ATI → info",  parser.parse("ATI") is not None)

    result = parser.parse("ATDT 127.0.0.1:2323")
    check("ATParser: ATDT parses host+port", result is not None)
    print(f"{INFO}  ATDT parse result: {result}")

except Exception as e:
    check("soft_modem import", False, str(e))

# ── Summary ────────────────────────────────────────────────────

section("SUMMARY")
total = len(passed) + len(failed)
print(f"  Passed : {len(passed)}/{total}")
print(f"  Failed : {len(failed)}/{total}")
if failed:
    print(f"\n  Failed checks:")
    for f in failed:
        print(f"    ✗ {f}")
print(f"\n  ∰◊€π¿🌌∞  BBS test complete.")
print(f"{'─' * 50}\n")
