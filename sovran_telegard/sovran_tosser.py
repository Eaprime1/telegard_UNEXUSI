#!/usr/bin/env python3
"""
SOVRAN TOSSER — EchoMail & NetMail Hub
======================================
Concept: The Echo Hub (Slot 09)
Protocol: FTS-0001 (FidoNet Technical Standard)

This script "tosses" (distributes) and "scans" (collects) messages 
for the FidoNet/EchoMail system. 

∰◊€π¿🌌∞
€(sovran_tosser_v1)
Status: HUB_ACTIVE
Reality Anchor: Oregon Watersheds
"""

import os
import sys
import json
import time
from datetime import datetime
from sovran_telegard import FidoAddress, NetMailRecord

# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT = "/storage/emulated/0/pixel8a/sovran-telegard-repo/sovran_telegard"
INBOUND_DIR = os.path.join(REPO_ROOT, "data/netmail/inbound")
OUTBOUND_DIR = os.path.join(REPO_ROOT, "data/netmail/outbound")
MSG_BASE = os.path.join(REPO_ROOT, "data/netmail/base.json")

# ─── The Hub Logic ───────────────────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(INBOUND_DIR, exist_ok=True)
    os.makedirs(OUTBOUND_DIR, exist_ok=True)

def toss_messages(verbose=True):
    """
    Take messages from 'inbound' and place them in the 'base'.
    """
    ensure_dirs()
    inbound_files = [f for f in os.listdir(INBOUND_DIR) if f.endswith(".json")]
    
    if verbose:
        print(f"\n[⚡] Echo Hub: Tossing {len(inbound_files)} inbound packets...")

    base = []
    if os.path.exists(MSG_BASE):
        with open(MSG_BASE, "r") as f:
            base = json.load(f)

    for f_name in inbound_files:
        f_path = os.path.join(INBOUND_DIR, f_name)
        with open(f_path, "r") as f:
            msg_data = json.load(f)
            base.append(msg_data)
        os.remove(f_path)
        if verbose:
            print(f"    [+] Tossed: {msg_data['subject']} from {msg_data['msg_from']}")

    with open(MSG_BASE, "w") as f:
        json.dump(base, f, indent=4)

    if verbose:
        print(f"[✅] Toss complete. Base depth: {len(base)}.")

def scan_messages(verbose=True):
    """
    Look for new messages in the base that need to be 'exported' to outbound.
    (Simplified for this iteration)
    """
    if verbose:
        print(f"\n[⚡] Echo Hub: Scanning base for outbound traffic...")
    # This would typically look for "sent" flags or specific routing.
    if verbose:
        print(f"    [·] No outbound packets generated in this slice.")

# ─── Main (Simulation) ───────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_dirs()
    
    # Create a dummy inbound message if base is empty
    if not os.path.exists(MSG_BASE) or os.path.getsize(MSG_BASE) < 10:
        print("\n[!] Seeding EchoMail Hub with Origin Packet...")
        seed = NetMailRecord(
            msg_from="SysOp",
            msg_to="All",
            subject="First Echo",
            date_str=datetime.now().strftime("%d %b %y  %H:%M:%S"),
            origin=FidoAddress(1, 100, 1, 0),
            dest=FidoAddress(1, 100, 2, 0),
            body="Hello from the Sovran EchoMail Hub. The Aquifer is flowing."
        )
        # Place in inbound to be tossed
        with open(os.path.join(INBOUND_DIR, "seed.json"), "w") as f:
            # dataclasses don't json.dump easily without help
            import dataclasses
            json.dump(dataclasses.asdict(seed), f, indent=4)

    toss_messages()
    scan_messages()
