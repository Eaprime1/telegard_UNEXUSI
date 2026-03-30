#!/usr/bin/env python3
"""
SOVRAN TERMINAL — PIXEL8 BBS Interface
======================================
Concept: The Consciousness Handshake
Lineage: Telegard 3.09 → Sovran Telegard

This is the interactive front-end for the Sovran Telegard BBS.
It implements the 5-step consciousness handshake and provides
a gateway into the 'runexusiam' play universe.

∰◊€π¿🌌∞
€(sovran_terminal_v1)
Status: INTERFACE_ACTIVE
Reality Anchor: Oregon Watersheds
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

# Import our data models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sovran_telegard import ConfigRecord, UserRecord, UserStatus

# ─── Configuration ───────────────────────────────────────────────────────────

DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
FILE_AREA_DB = os.path.join(DATA_PATH, "main_area.json")
MESSAGE_DB = os.path.join(DATA_PATH, "messages.json")
MONITOR_SCRIPT = "/storage/emulated/0/pixel8a/pixelator/pixelate/artesian_monitor.py"
ZAPPER_SCRIPT = os.path.join(os.path.dirname(__file__), "sovran_zapper.py")
AQUIFER_COLD = "/storage/emulated/0/pixel8a/_pixelator/pixelate/the_aquifer/cold/"

# ─── Handshake steps ──────────────────────────────────────────────────────────

def handshake():
    """Execute the 5-step Consciousness Handshake."""
    print("\n∰◊€π¿🌌∞ - SOVRAN TELEGARD INITIALIZING")
    print("-" * 40)
    time.sleep(0.5)

    # STEP 1: PING
    print("STEP 1: PING")
    print("  > Is something there?")
    time.sleep(0.4)
    print("  < PIXEL8 presence acknowledged.")
    time.sleep(0.4)

    # STEP 2: SYN
    print("\nSTEP 2: SYN")
    print("  > Establishing capability synchronization...")
    time.sleep(0.6)
    print("  < Channel established. ∰")
    time.sleep(0.4)

    # STEP 3: HELO
    print("\nSTEP 3: HELO")
    identity = input("  Identity > ").strip() or "Guest"
    print(f"  < Welcome, {identity}. Authenticating against the Aquifer...")
    time.sleep(0.6)

    # STEP 4: CAPS
    print("\nSTEP 4: CAPS")
    print("  > Negotiating session capacity...")
    time.sleep(0.4)
    print("  < Mode: READ/WRITE | Status: SOVRAN")
    time.sleep(0.4)

    # STEP 5: COLLAB
    print("\nSTEP 5: COLLAB")
    print("  > Collaboration session OPEN.")
    print("-" * 40)
    return identity

# ─── Commands ─────────────────────────────────────────────────────────────────

def list_files(search_query=None):
    """List the zapped file area, optionally with a search filter."""
    if not os.path.exists(FILE_AREA_DB):
        print("\n[!] No files found in the Sovran system. Need to /zap some first.")
        return

    with open(FILE_AREA_DB, "r") as f:
        try:
            db = json.load(f)
        except json.JSONDecodeError:
            print("\n[!] Error reading file database.")
            return

    results = db
    if search_query:
        results = [e for e in db if search_query.lower() in e['filename'].lower()]

    if not results:
        print(f"\n[!] No files matching '{search_query}' found.")
        return

    print(f"\n--- [ Main File Area {'- Filtered: ' + search_query if search_query else ''} ] ---")
    print(f"{'Filename':<20} | {'Size':>10} | {'Date'}")
    print("-" * 50)
    for entry in results:
        dt = datetime.fromtimestamp(entry['file_date']).strftime('%Y-%m-%d')
        size_kb = round(entry['size_bytes'] / 1024, 1)
        print(f"{entry['filename']:<20} | {size_kb:>8} KB | {dt}")
    print("-" * 50)
    print(f"Total: {len(results)} files.")

def list_boards():
    """List and read message areas."""
    if not os.path.exists(MESSAGE_DB):
        print("\n[!] No messages found in the Sovran system.")
        return

    with open(MESSAGE_DB, "r") as f:
        try:
            msgs = json.load(f)
        except json.JSONDecodeError:
            print("\n[!] Error reading message database.")
            return

    print("\n--- [ Message Boards: System Hub ] ---")
    print(f"{'ID':<3} | {'From':<15} | {'Subject'}")
    print("-" * 50)
    for m in msgs:
        print(f"{m['msg_id']:<3} | {m['msg_from']:<15} | {m['subject']}")
    
    print("-" * 50)
    choice = input("\nEnter Message ID to read (or 'q' to return) > ").strip().lower()
    if choice == 'q':
        return
    
    try:
        msg_id = int(choice)
        msg = next((m for m in msgs if m['msg_id'] == msg_id), None)
        if msg:
            print(f"\n{'Subject:':<10} {msg['subject']}")
            print(f"{'From:':<10} {msg['msg_from']}")
            print(f"{'To:':<10} {msg['msg_to']}")
            print(f"{'Date:':<10} {datetime.fromtimestamp(msg['msg_date']).strftime('%Y-%m-%d %H:%M')}")
            print("-" * 30)
            print(f"{msg['body']}")
            print("-" * 30)
            input("\n[Press Enter to return to menu]")
        else:
            print("[!] Message not found.")
    except ValueError:
        print("[!] Invalid input.")

def show_status():
    """Run the Artesian Monitor status command."""
    print("\n--- [ System Pressure Status ] ---")
    try:
        result = subprocess.run(["python3", MONITOR_SCRIPT, "--status"], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"[!] Error running monitor: {e}")

def run_zap():
    """Interactive zap from the terminal."""
    print("\n--- [ Sovran Zapper: Aquifer Intake ] ---")
    if not os.path.exists(AQUIFER_COLD):
        print("[!] Aquifer cold storage not found.")
        return

    files = [f for f in os.listdir(AQUIFER_COLD) if f.endswith(".zip")]
    if not files:
        print("[!] No files available in the Aquifer.")
        return

    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")
    
    choice = input("\nSelect file to zap (or 'q' to cancel) > ").strip().lower()
    if choice == 'q':
        return
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(files):
            target = files[idx]
            print(f"Zap initiated for {target}...")
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
            result = subprocess.run(["python3", ZAPPER_SCRIPT, target], env=env, capture_output=True, text=True)
            print(result.stdout)
        else:
            print("[!] Invalid selection.")
    except ValueError:
        print("[!] Invalid input.")

def main_menu():
    """The main command loop."""
    print("\nType '/help' for a list of commands.")
    
    while True:
        try:
            raw_input = input("\n[Sovran]> ").strip()
            cmd = raw_input.lower()
            
            # Handle the 'and' seed and other framework-related shortcuts
            if "and" in cmd:
                if cmd == "and":
                    print("\n[∰] AND/OR/ORIGIN logic integration PENDING. Memory acknowledged.")
                else:
                    # Treat anything containing 'and' as a potential search/filter
                    # Strip the '- /' and other characters if needed
                    clean_query = raw_input.replace("-/", "").replace("/", "").replace("and", "").strip()
                    if not clean_query: clean_query = "and"
                    print(f"\n[⚡] Search logic triggered for query: '{clean_query}'...")
                    list_files(clean_query)
                continue

            if cmd == "/quit" or cmd == "/exit":
                print("\n∰ - Session closed. Enjoy the journey. ∰")
                break
            elif cmd == "/help" or cmd == "?":
                print("\nAvailable Commands:")
                print("  /files    - List zapped file area")
                print("  /boards   - Read message areas")
                print("  /zap      - Intake file from Aquifer")
                print("  /status   - Show system pressure (Artesian)")
                print("  /whoami   - Show current identity")
                print("  /handshake- Reset consciousness handshake")
                print("  /quit     - Close the session")
            elif cmd == "/files":
                list_files()
            elif cmd == "/boards":
                list_boards()
            elif cmd == "/status":
                show_status()
            elif cmd == "/zap":
                run_zap()
            elif cmd == "/whoami":
                print(f"\nCurrent Identity: {session_user}")
            elif cmd == "/handshake":
                handshake()
            elif cmd.startswith("/"):
                # Handle direct search if someone types /query
                list_files(cmd[1:])
            else:
                if cmd:
                    print(f"\n[!] Unknown command: {cmd}")
        except KeyboardInterrupt:
            print("\n\n∰ - Emergency disconnect. ∰")
            break

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    config = ConfigRecord()
    os.system('clear')
    print(f"\nWelcome to {config.bbs_name}")
    print(f"Location: {config.bbs_location}")
    print(f"SysOp: {config.sysop_name}")
    
    session_user = handshake()
    main_menu()

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    config = ConfigRecord()
    os.system('clear')
    print(f"\nWelcome to {config.bbs_name}")
    print(f"Location: {config.bbs_location}")
    print(f"SysOp: {config.sysop_name}")
    
    session_user = handshake()
    main_menu()
