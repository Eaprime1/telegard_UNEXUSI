#!/usr/bin/env python3
"""
SOVRAN TELEGARD — Python Data Structures
========================================
Origin Reference: Telegard 3.09 Gamma-1 (1997-11-05)
Project: runexusiam play universe

These structures are Python-native translations of the legacy 
Turbo Pascal / C data models found in the Telegard 3.09 Dev Kit.
They serve as the 'Domos' (Origin templates) for our Python BBS.

∰◊€π¿🌌∞
€(sovran_telegard_v1)
Status: DOMOS_INITIALIZED
Reality Anchor: Oregon Watersheds
"""

from dataclasses import dataclass, field
from enum import IntFlag, auto
from typing import List, Optional
import time
import zlib  # For CRC32 password verification

# ─── 1. CORE TYPES ──────────────────────────────────────────────────────────

# Telegard 'unixtime' is a longint (seconds since 01/01/70)
# Telegard 'datestring' is string[9] (MM/YY/YY)

# ─── 2. USER STATUS & FLAGS ──────────────────────────────────────────────────

class UserStatus(IntFlag):
    """Legacy USERS.DAT status (userstatus set)"""
    LOCKED_OUT    = auto()  # if locked out
    DELETED       = auto()  # if deleted
    TRAP_ACTIVITY = auto()  # if trapping user activity
    TRAP_SEPARATE = auto()  # if trap to separate TRAP file
    CHAT_AUTO     = auto()  # if auto chat trapping
    CHAT_SEPARATE = auto()  # if separate chat file
    SLOG_SEPARATE = auto()  # if separate SysOp log
    ALERT         = auto()  # alert SysOp when user logs on

class UserFlags(IntFlag):
    """Legacy USERS.DAT user flags (userflag set)"""
    NEW_USER_MSG  = auto()  # sent newuser message
    CLS_MSG       = auto()  # clear screen before messages
    FULL_INPUT    = auto()  # full line input
    HOTKEY        = auto()  # menu hotkeys active
    PAUSE         = auto()  # pause lists
    NOVICE        = auto()  # user is at novice help level
    HIDDEN_LOG    = auto()  # not in call/online listings
    HIDDEN_LIST   = auto()  # not in user listings

class UserACFlags(IntFlag):
    """Legacy user AC flags (bitmapped restriction set)"""
    R_LOGON       = auto()  # L - One call per day
    R_CHAT        = auto()  # C - Can't page SysOp
    R_NETMAIL_DEL = auto()  # F - Force Netmail deletion
    R_AMSG        = auto()  # A - Can't post AutoMessage
    R_POST_AN     = auto()  # * - Can't post anonymously
    R_POST_PVT    = auto()  # E - Can't post private
    R_POST_NET    = auto()  # N - Can't post NetMail
    R_POST        = auto()  # P - Can't post at all
    R_VOTING      = auto()  # K - Can't vote
    R_MSG         = auto()  # M - Forced email deletion
    R_POST_ECHO   = auto()  # G - Can't post EchoMail
    F_NO_DL_RATIO = auto()  # 1 - No UL/DL ratio

# ─── 3. USER RECORD (userrec) ────────────────────────────────────────────────

@dataclass
class UserRecord:
    """Translation of Telegard's USERS.DAT record (userrec)"""
    name: str = ""              # User name
    realname: str = ""          # Real name
    street: str = ""            # Mailing address
    location: str = ""          # City, Province
    postal_code: str = ""       # Postal code
    voice_phone: str = ""       # Voice phone number
    data_phone: str = ""        # Data phone number (modem)

    # Password fields
    pw_text: str = ""           # User password (may be empty if hidden)
    pw_crc: int = 0             # CRC-32 of user password

    # Identity/Profile
    last_date: int = 0          # Last logon unixtime
    first_date: str = ""        # Firston datestring
    pw_date: str = ""           # Last date of password change
    birth_date: str = ""        # Birth date
    gender: str = "M"           # M/F
    subscription_date: str = "" # Subscription start
    expire_date: str = ""       # Subscription expires
    expire_to: str = "A"        # Level to expire to (A..Z)
    comment: str = ""           # SysOp comment
    notes: List[str] = field(default_factory=lambda: ["", "", ""])
    lock_file: str = ""         # Lockout message filename

    # Technical Specs
    graphics_protocol: int = 1  # 0:TTY, 1:ANSI, 2:Avatar, 3:RIP
    fallback_protocol: int = 0  
    line_length: int = 80       # Columns
    page_length: int = 24       # Rows

    # Security & Flags
    sl: int = 10                # Security Level (10 = New User)
    status: UserStatus = UserStatus(0)
    flags: UserFlags = UserFlags(0)
    ac: UserACFlags = UserACFlags(0)

    # Stats
    uploads: int = 0            # Total files uploaded
    uk_total: int = 0           # Total KB uploaded
    downloads: int = 0          # Total files downloaded
    dk_total: int = 0           # Total KB downloaded
    time_total: int = 0         # Total time online (minutes)
    calls_total: int = 0        # Total calls
    posts_total: int = 0        # Total messages posted
    email_total: int = 0        # Total email sent

    def verify_password(self, input_text: str) -> bool:
        """Verify password using CRC-32 (legacy HiddenPW logic)"""
        # Telegard passwords were always forced to uppercase
        input_upper = input_text.upper().encode('ascii')
        # CRC32 in Pascal/C was often signed or unsigned 32-bit
        input_crc = zlib.crc32(input_upper) & 0xFFFFFFFF
        return input_crc == (self.pw_crc & 0xFFFFFFFF)

    def set_password(self, new_password: str, hide_text: bool = True):
        """Set password and update CRC"""
        p_upper = new_password.upper()
        self.pw_crc = zlib.crc32(p_upper.encode('ascii')) & 0xFFFFFFFF
        if hide_text:
            self.pw_text = ""
        else:
            self.pw_text = p_upper

# ─── 4. FILE & MESSAGE STRUCTURES ────────────────────────────────────────────

class FileAreaFlags(IntFlag):
    """Legacy FAREAS.DAT status flags (fareaflags set)"""
    CD_ROM       = auto()  # area is on CD-ROM
    NOT_ACTIVE   = auto()  # area is not active
    MANDATORY    = auto()  # mandatory for all users
    UPLOAD_ONLY  = auto()  # upload only area
    PRIVATE      = auto()  # private files only

class FileStatus(IntFlag):
    """Legacy *.FA file status flags (fbstat set)"""
    FREE_DL      = auto()  # if file is free download
    NO_TIME      = auto()  # if file is time check free
    VALIDATED    = auto()  # if file is validated
    AVAILABLE    = auto()  # if file is available
    OFFLINE      = auto()  # if file is offline
    HATCH        = auto()  # if file hatched via SDS

@dataclass
class FileAreaRecord:
    """Translation of Telegard's FAREAS.DAT (farearec)"""
    description: str = ""       # area description
    filename: str = ""          # database filename (e.g. "MAIN")
    info_file: str = ""         # info filename
    path: str = ""              # physical path
    arc_type: str = ""          # archive extension (ZIP, etc)
    status: FileAreaFlags = FileAreaFlags(0)
    sysop_acs: str = "s255"     # SysOp access
    list_acs: str = ""          # list/view access
    ul_acs: str = ""            # upload access
    dl_acs: str = ""            # download access
    create_date: int = 0        # area creation date (unixtime)

@dataclass
class FileRecord:
    """Translation of Telegard's *.FA record (fbrec)"""
    filename: str = ""          # actual filename on disk
    description_offset: int = 0 # offset in description file
    description_len: int = 0    # length of description
    size_bytes: int = 0         # file size
    ul_date: int = 0            # upload date
    file_date: int = 0          # date on file
    dl_date: int = 0            # last download date
    status: FileStatus = FileStatus.AVAILABLE | FileStatus.VALIDATED
    downloads: int = 0          # download count
    uploader: str = ""          # uploader name
    password_crc: int = 0       # CRC of download password

@dataclass
class MessageAreaRecord:
    """Translation of Telegard's MAREAS.DAT (marearec)"""
    name: str = ""              # area description
    msg_path: str = ""          # messages pathname
    filename: str = ""          # base filename for data
    read_acs: str = ""          # read access
    post_acs: str = ""          # post access
    sysop_acs: str = "s255"     # SysOp access
    max_msgs: int = 500         # max messages to keep
    max_days: int = 30          # max days to keep
    origin_line: str = ""       # origin line (FidoNet style)
    create_date: int = 0        # area creation date

# ─── 5. MENU STRUCTURES ──────────────────────────────────────────────────────

@dataclass
class MenuRecord:
    """Translation of Telegard's *.MNU header (menurec)"""
    titles: List[str] = field(default_factory=lambda: ["", "", ""])
    prompt: str = ""            # menu prompt
    fallback: str = ""          # fallback menu if something fails
    help_file: str = ""         # help file to display
    columns: int = 1            # generic menu column count

@dataclass
class MessageRecord:
    """Translation of Telegard's *.SQD record (sqxmsgrec)"""
    msg_from: str = ""          # Message from
    msg_to: str = ""            # Message to
    subject: str = ""           # Message subject
    msg_date: int = 0           # Original date (unixtime)
    msg_id: int = 0             # Message ID
    body: str = ""              # Message body (stored in data file)

# ─── 6. CONFIGURATION RECORD (configrec) ─────────────────────────────────────

@dataclass
class ConfigRecord:
    """Translation of Telegard's CONFIG.TG (configrec)"""
    version_id: int = 0x0309    # 0x0309 = v3.09
    
    # Pathing
    data_path: str = "./data/"
    text_path: str = "./text/"
    lang_path: str = "./lang/"
    menu_path: str = "./menus/"
    logs_path: str = "./logs/"
    msgs_path: str = "./msgs/"
    file_path: str = "./files/"
    
    # System Identity
    bbs_name: str = "PIXEL8 SOVRAN"
    bbs_phone: str = "555-MODEM"
    bbs_location: str = "Oregon Watersheds"
    sysop_name: str = "Eric Pace"
    
    # Operation
    multinode: bool = False
    hidden_pw: bool = True      # If True, pw_text in UserRecord is cleared
    timeout_minutes: int = 15
    sysop_pw: str = "SECRET"    # For remote sysop access

# ─── 5. DEMO / TEST ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("∰◊€π¿🌌∞ - SOVRAN TELEGARD DOMOS TEST")
    
    # Create a new user record
    eric = UserRecord(
        name="NAVIGO SUXENEXUS",
        realname="Eric Pace",
        location="Oregon",
        sl=255,  # SysOp Level
        status=UserStatus.CHAT_AUTO | UserStatus.ALERT,
        flags=UserFlags.HOTKEY | UserFlags.PAUSE | UserFlags.FULL_INPUT
    )
    
    # Set and verify password
    password = "GEMINI_NEXUS"
    eric.set_password(password, hide_text=True)
    
    print(f"\nUser: {eric.name}")
    print(f"Location: {eric.location}")
    print(f"SL: {eric.sl}")
    print(f"Status: {eric.status!r}")
    print(f"Flags: {eric.flags!r}")
    print(f"Password CRC: {hex(eric.pw_crc)}")
    print(f"Password Text: '{eric.pw_text}' (hidden as requested)")
    
    # Verification check
    test_pw = "GEMINI_NEXUS"
    is_correct = eric.verify_password(test_pw)
    print(f"Verifying '{test_pw}': {'✅ SUCCESS' if is_correct else '❌ FAILED'}")
    
    # System config
    config = ConfigRecord()
    print(f"\nSystem: {config.bbs_name}")
    print(f"SysOp: {config.sysop_name}")
    print(f"Root Location: {config.bbs_location}")
    
    print("\n∰◊€π¿🌌∞ - Journey continues...")
