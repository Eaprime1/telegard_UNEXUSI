#!/usr/bin/env python3
"""
SOVRAN ZAPPER — Aquifer Intake Tool
==================================
Concept: Spark_Bolt_Bit (✨⚡•)
Action: "Zap" (one-hertz content intake)

This script "zaps" files from the Aquifer (cold storage) into the 
Sovran Telegard data structures, preserving the chain of custody 
and adding the necessary metadata for the Python BBS.

✨ Spark - Origin essence (the zip file)
⚡ Bolt  - Transformative energy (the zap process)
• Bit   - Fundamental units (the FileRecord)

∰◊€π¿🌌∞
€(sovran_zapper_v1)
Status: ACTIVE_ZAPPER
Reality Anchor: Oregon Watersheds
"""

import os
import sys
import json
import time
import datetime
from pathlib import Path
from sovran_telegard import FileRecord, FileStatus

# ─── Configuration ───────────────────────────────────────────────────────────

AQUIFER_COLD = "/storage/emulated/0/pixel8a/_pixelator/pixelate/the_aquifer/cold/"
SOVRAN_DATA  = "/storage/emulated/0/pixel8a/Q/runexusiam/sovran_telegard/data/"
RESULTS_PATH = "/storage/emulated/0/pixel8a/pixelator/pixelate/tester_results.txt"
FILE_AREA_DB = os.path.join(SOVRAN_DATA, "main_area.json")

# ─── Utility ─────────────────────────────────────────────────────────────────

def write_results(line):
    """Log the zap in the tester_results.txt archive."""
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    with open(RESULTS_PATH, "a") as f:
        f.write(f"[{ts}] ZAPPER       {line}\n")

def ensure_dirs():
    os.makedirs(SOVRAN_DATA, exist_ok=True)

# ─── The Zap ─────────────────────────────────────────────────────────────────

def zap_file(filename):
    """
    Perform the ✨⚡• Spark_Bolt_Bit transformation.
    """
    file_path = os.path.join(AQUIFER_COLD, filename)
    
    if not os.path.exists(file_path):
        print(f"❌ Error: {filename} not found in the Aquifer.")
        return False

    print(f"✨ Spark: Acknowledging origin essence: {filename}")
    
    # Gather metadata
    stats = os.stat(file_path)
    size_bytes = stats.st_size
    mtime = int(stats.st_mtime)
    
    # Create the Bit (FileRecord)
    bit = FileRecord(
        filename=filename,
        size_bytes=size_bytes,
        ul_date=int(time.time()),
        file_date=mtime,
        uploader="Gemini",
        status=FileStatus.AVAILABLE | FileStatus.VALIDATED
    )

    print(f"⚡ Bolt:  Applying transformative energy to {filename}...")
    
    # Store the Bit in the Sovran database
    ensure_dirs()
    
    db = []
    if os.path.exists(FILE_AREA_DB):
        with open(FILE_AREA_DB, "r") as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []

    # Update if exists, else append
    updated = False
    for i, entry in enumerate(db):
        if entry["filename"] == filename:
            db[i] = vars(bit)
            updated = True
            break
    
    if not updated:
        db.append(vars(bit))
        
    with open(FILE_AREA_DB, "w") as f:
        json.dump(db, f, indent=4)

    print(f"• Bit:   Fundamental unit preserved in main_area.json")
    
    # Log the successful zap
    write_results(f"ZAP_COMPLETE {filename} size:{size_bytes} SHA256:N/A")
    print(f"\n∰ SUCCESS: {filename} has been zapped into the Sovran system. ∰")
    return True

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 sovran_zapper.py <filename_in_aquifer>")
        print("\nAvailable in Aquifer:")
        if os.path.exists(AQUIFER_COLD):
            for f in os.listdir(AQUIFER_COLD):
                if f.endswith(".zip"):
                    print(f"  - {f}")
        return

    target = sys.argv[1]
    zap_file(target)

if __name__ == "__main__":
    main()
