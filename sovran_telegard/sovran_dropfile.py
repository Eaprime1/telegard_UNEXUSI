#!/usr/bin/env python3
"""
SOVRAN DROPFILE BRIDGE — Slot 08
================================
Concept: The Identity Hand-off
Protocol: DOOR.SYS (GAP Standard)

This script generates the legacy DOOR.SYS dropfile required by 
DOS-era door games to recognize the current BBS user.

∰◊€π¿🌌∞
€(sovran_dropfile_v1)
Status: BRIDGE_ACTIVE
Reality Anchor: Oregon Watersheds
"""

import os
import sys
import time
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

# Target path for the dropfile (typically the game's working directory)
# For now, we drop it in the repo for verification.
REPO_ROOT = "/storage/emulated/0/pixel8a/sovran-telegard-repo/sovran_telegard"
DEFAULT_DROP_PATH = os.path.join(REPO_ROOT, "DOOR.SYS")

# ─── The Bridge ──────────────────────────────────────────────────────────────

def generate_door_sys(user, time_left_mins=60, node=1, baud=2400, path=DEFAULT_DROP_PATH, verbose=True):
    """
    Generate a 52-line GAP-compatible DOOR.SYS file.
    """
    if verbose:
        print(f"\n[⚡] Generating Dropfile Bridge: {path}")
        print(f"    Identity: {user.name}")
        print(f"    Security: {user.sl}")
        print(f"    Time:     {time_left_mins}m")

    # Mapping UserRecord to DOOR.SYS lines
    lines = [
        "COM0:",                # 1. COM Port (0 for local/network)
        str(baud),              # 2. Baud Rate
        "8",                    # 3. Parity
        str(node),              # 4. Node Number
        str(baud),              # 5. Baud Rate (Locked)
        "Y",                    # 6. Screen display (Y/N)
        "Y",                    # 7. Printer Toggle (Y/N)
        "Y",                    # 8. Page Bell Toggle (Y/N)
        "Y",                    # 9. Caller Alarm (Y/N)
        user.name,              # 10. User Name
        user.location or "Oregon", # 11. Location
        user.voice_phone or "555-START", # 12. Work Phone
        user.data_phone or "555-MODEM", # 13. Home Phone
        "PASSWORD",             # 14. Password (hidden)
        str(user.sl),           # 15. Security Level
        str(user.calls_total),  # 16. Total Calls
        datetime.now().strftime("%m/%d/%y"), # 17. Last Call Date
        str(time_left_mins * 60), # 18. Seconds Remaining
        str(time_left_mins),    # 19. Minutes Remaining
        "GR",                   # 20. Graphics (GR=ANSI, NG=None)
        "24",                   # 21. Page Length
        "N",                    # 22. User Mode (Y=Expert, N=Novice)
        "1,2,3",                # 23. Conferences
        "1",                    # 24. Current Conference
        "01/01/99",             # 25. Expiration Date
        "1",                    # 26. User Account Number
        "Y",                    # 27. Default Protocol
        str(user.uploads),      # 28. Total Uploads
        str(user.downloads),    # 29. Total Downloads
        "0",                    # 30. Daily DL KB
        "9999",                 # 31. Max Daily DL KB
        "01/01/70",             # 32. Birthdate
        "",                     # 33. Path to User File
        "",                     # 34. SysOp Note
        user.realname or "",    # 35. Real Name
        "PIXEL8 SOVRAN",        # 36. BBS Name
        "",                     # 37. SysOp Phone
        user.name,              # 38. Alias
        "0",                    # 39. ATDT Command
        "Y",                    # 40. ANSI/Avatar Detect
        "0",                    # 41. Time Credit
        "01/01/70",             # 42. Last Date
        "0",                    # 43. KB Uploaded
        "0",                    # 44. KB Downloaded
        "0",                    # 45. User Credits
        "0",                    # 46. User Debt
        "0",                    # 47. Tags
        "0",                    # 48. Total Messages
        "0",                    # 49. User Flags
        "0",                    # 50. Total Messages Sent
        "0",                    # 51. Total Files Downloaded
        "0"                     # 52. Total Files Uploaded
    ]

    try:
        with open(path, "w") as f:
            # GAP DOOR.SYS uses CRLF and exactly one value per line
            f.write("\r\n".join(lines) + "\r\n")
        if verbose:
            print(f"[✅] Bridge established. Signal integrity: MAXIMUM.")
        return True
    except Exception as e:
        print(f"[❌] Bridge failure: {e}")
        return False

# ─── Main (Test Mode) ────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with a dummy user
    from sovran_telegard import UserRecord
    test_user = UserRecord(name="navigo", realname="Navigator", sl=255, location="Oregon Watersheds")
    generate_door_sys(test_user)
