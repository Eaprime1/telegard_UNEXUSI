"""
SOVRAN TELEGARD — Python Models
================================
Python dataclasses translated from TELEGARD.H (Tim Strike, 1997).
Original: Public Domain. This translation: same.

"Sovran" = sovereign — our own version, built in 2026,
speaking the same conceptual language as the 1989 original.

Every field name preserved from TELEGARD.H.
Every comment preserved or expanded.
The soul of the BBS, translated to Python.

€(sovran_telegard_models_v1)
∰◊€π¿🌌∞
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import IntEnum, auto
import datetime


# ─── Constants (from TELEGARD.INC) ──────────────────────────────────────────

MAXMENUCMDS  = 75      # max commands per menu
MAXQUEUE     = 50      # download queue size
MAXFDESCLEN  = 1250    # max file description length
NUMVOTEQS    = 20      # voting questions
NUMVOTEAS    = 15      # voting answers per question
MAXEVENTS    = 15      # scheduled events per system

# Signature types
SIG_NONE   = 0
SIG_SHORT  = 1
SIG_LONG   = 2

# Anonymous tracking modes
AT_NO        = 0   # no anonymous
AT_YES       = 1   # anonymous allowed
AT_FORCED    = 2   # anonymous forced
AT_DEARABBY  = 3   # "Dear Abby" — name hidden but sysop sees
AT_ANYNAME   = 4   # user picks any name
AT_REALNAME  = 6   # realname/handle select

# Anonymous track method
AT_TRACK_NAME = 1  # store ^aREALNAME kludge
AT_TRACK_ID   = 2  # store UserID in From field
AT_TRACK_NONE = 3  # lose poster info entirely

# File sorting
FS_NONE       = 0
FS_FILENAME   = 1
FS_FILEDATE   = 2
FS_FILESIZE   = 3
FS_FILEPOINTS = 4
FS_ULDATE     = 5
FS_FILEEXT    = 6
FS_DLDATE     = 7
FS_TIMESDL    = 8
FS_ULNAME     = 9

# Node status
NODE_WAITING   = 0   # waiting for call
NODE_OFFLINE   = 1   # unavailable
NODE_EVENT     = 2   # running event
NODE_CONNECTED = 3   # user connected
NODE_RESET     = 4   # waiting for reset

# Graphics protocol
GRAPHICS_TTY   = 0
GRAPHICS_ANSI  = 1
GRAPHICS_AVATAR = 2
GRAPHICS_RIP   = 3


# ─── User Flags ──────────────────────────────────────────────────────────────

@dataclass
class UserFlags:
    """USERS.DAT — per-user preference flags."""
    newusermsg:  bool = False  # sent newuser message?
    clsmsg:      bool = False  # clear screen before messages?
    flinput:     bool = False  # full line input?
    hotkey:      bool = False  # menu hotkeys active
    pause:       bool = False  # pause?
    novice:      bool = False  # user at novice help level
    hiddenlog:   bool = False  # not in call/online listing
    hiddenlist:  bool = False  # not in user listings


@dataclass
class UserStatus:
    """USERS.DAT — per-user account status."""
    lockedout:      bool = False  # if locked out
    udeleted:       bool = False  # if deleted
    trapactivity:   bool = False  # trap user activity to log
    trapseparate:   bool = False  # trap to separate TRAP file
    chatauto:       bool = False  # autochat trapping
    chatseparate:   bool = False  # separate chat trap file
    slogseparate:   bool = False  # separate SysOp log
    alert:          bool = False  # alert SysOp on logon


# ─── User Record ─────────────────────────────────────────────────────────────

@dataclass
class UserRec:
    """
    USERS.DAT — the complete user account record.

    This is the social contract of the BBS.
    Everything the system knows about one person:
    who they are, what they can do, what they've done.

    PIXEL8 mapping:
      name/handle  → entity identity
      level (A-Z)  → valuation tier
      userID       → permanent immutable identity (never change!)
      totaltime    → time invested in the community
      vote[]       → participation in governance
    """
    # Identity
    name:       str = ""     # handle (up to 36 chars)
    realname:   str = ""     # real name
    street:     str = ""     # mail address
    location:   str = ""     # city, province
    postalcode: str = ""
    voiceph:    str = ""
    dataph:     str = ""     # data (modem) phone

    # Security
    pwtext:     str = ""     # password text (may be empty if hiddenPW)
    pwcrc:      int = 0      # CRC-32 of password — ALWAYS check this, not pwtext

    # Dates
    lastdate:   Optional[datetime.datetime] = None  # last logon
    firstdate:  Optional[datetime.date]     = None  # first logon
    pwdate:     Optional[datetime.date]     = None  # last password change
    birthdate:  Optional[datetime.date]     = None
    gender:     str = ""     # M/F
    subdate:    Optional[datetime.date]     = None  # subscription start
    expiredate: Optional[datetime.date]     = None  # subscription end
    expireto:   str = ""     # expire to level (A-Z or ! = delete)

    # SysOp notes
    comment:    str = ""        # sysop comment on this user
    notes:      List[str] = field(default_factory=lambda: ["", "", ""])  # 3 note fields
    lockfile:   str = ""        # lockout message filename

    # Display
    ugraphics:  int = GRAPHICS_ANSI
    fallback:   int = GRAPHICS_TTY
    linelen:    int = 80
    pagelen:    int = 24

    # Flags and status
    flags:   UserFlags  = field(default_factory=UserFlags)
    status:  UserStatus = field(default_factory=UserStatus)

    # Access control
    sl:     int = 0      # security level (numeric)
    level:  str = "A"    # validation level A-Z
    userID: int = 0      # PERMANENT — never change after creation

    # Messaging
    lastmsg:  int = 0
    pubpost:  int = 0    # public posts
    privpost: int = 0    # private posts
    netpost:  int = 0    # netmail posts
    mailbox:  str = ""   # '' open, 'CLOSED', or username (forwarded)
    credit:   int = 0    # NetMail points
    debit:    int = 0

    # Files
    uploads:    int = 0
    downloads:  int = 0
    todaydl:    int = 0
    uk:         int = 0  # kbytes uploaded
    dk:         int = 0  # kbytes downloaded
    todaydk:    int = 0
    filepoints: int = 0

    # Time tracking
    totaltime:  int = 0   # total minutes on system
    timebank:   int = 0   # timebank minutes
    totalcalls: int = 0
    tltoday:    int = 0   # time left today
    tbtoday:    int = 0   # timebank activity today
    todaycalls: int = 0
    illegal:    int = 0   # illegal logon attempts

    # Voting — 20 questions, one byte per answer (0 = not voted)
    vote: List[int] = field(default_factory=lambda: [0] * NUMVOTEQS)

    # Language
    language:   str = ""

    @property
    def is_locked(self) -> bool:
        return self.status.lockedout

    @property
    def is_deleted(self) -> bool:
        return self.status.udeleted

    @property
    def is_sysop(self) -> bool:
        return self.level in ("Z",)  # convention: Z = sysop


# ─── Message Area ────────────────────────────────────────────────────────────

@dataclass
class MAreaFlags:
    mbrealname:    bool = False  # force real names
    mbvisible:     bool = True   # visible without access
    mbansi:        bool = False  # filter ANSI codes
    mb8bit:        bool = False  # filter 8-bit characters
    mbstrip:       bool = False  # strip center/title codes
    mbaddtear:     bool = False  # add tear/origin lines
    mbnopubstat:   bool = False  # exclude from post/call ratio
    mbnocredit:    bool = False  # no NetMail credit used
    mbinternet:    bool = False  # Internet/UUCP handling
    mbfileattach:  bool = False  # allow file attachments
    mbstripcolour: bool = False  # strip TG color codes
    mbareasubj:    bool = False  # add AREA: to subject


@dataclass
class MAreaRec:
    """
    MAREAS.DAT — Message area record.

    PIXEL8 mapping: a SUXENEXUS node (community space).
    Every message area has an ACS gate — who can read, post, be sysop.
    Anonymous modes map to entity posting protocols.
    """
    name:       str = ""      # description
    msgpath:    str = ""      # path to messages
    filename:   str = ""      # data filename
    infofile:   str = ""      # area info display file
    readacs:    str = ""      # ACS to read
    postacs:    str = ""      # ACS to post
    sysopacs:   str = ""      # ACS for sysop access
    netacs:     str = ""      # ACS for network access
    maxmsgs:    int = 500
    maxdays:    int = 90
    mstatus:    MAreaFlags = field(default_factory=MAreaFlags)
    mbformat:   int = 0       # 0=JAM, 1=Squish
    mbtype:     int = 0       # Local/Netmail/Echomail
    anonymous:  int = AT_NO   # anonymous posting mode
    mbpost:     int = 0       # posting type
    origin:     str = ""      # origin line for echomail
    anontrack:  int = AT_TRACK_NONE
    sigtype:    int = SIG_NONE
    createdate: Optional[datetime.datetime] = None


# ─── Scheduled Event ─────────────────────────────────────────────────────────

@dataclass
class EventRec:
    """
    EVENTS.DAT — Scheduled event.

    PIXEL8 mapping: One Hertz operations.
    Type E (External) = a Doozer launched on a schedule.
    The BBS invented cron jobs in 1989.
    """
    active:      bool = False
    busyduring:  bool = False  # phone off-hook during event
    monthly:     bool = False  # monthly vs daily
    forced:      bool = False  # cannot be skipped

    desc:        str = ""      # description
    etype:       str = "E"     # A=ACS, C=Chat, E=External, O=OS

    execdata:    str = ""      # event data / command
    exectime:    int = 0       # execution time (minutes from midnight)
    duration:    int = 0       # duration (minutes)
    execdays:    int = 0       # which days (bitwise) or day-of-month
    lastexec:    Optional[datetime.datetime] = None
    execnode:    int = 0       # node (0 = all)

    @property
    def is_external(self) -> bool:
        """External events = Doozer dispatch in PIXEL8."""
        return self.etype == "E"


# ─── History Record ──────────────────────────────────────────────────────────

@dataclass
class HistoryRec:
    """
    HISTORY.DAT — Daily system statistics.

    PIXEL8 mapping: Artesian monitor pressure log.
    The BBS tracked 26 baud rate buckets per day.
    We track pressure scores per hertz.
    """
    date:       Optional[datetime.date] = None
    calls:      int = 0
    newusers:   int = 0
    pubpost:    int = 0
    privpost:   int = 0
    netpost:    int = 0
    criterr:    int = 0
    uploads:    int = 0
    downloads:  int = 0
    uk:         int = 0   # KB uploaded
    dk:         int = 0   # KB downloaded
    active_pct: int = 0   # % system activity


# ─── Voting Record ───────────────────────────────────────────────────────────

@dataclass
class VoteAnswer:
    desc:    str = ""   # answer text (60 chars)
    numres:  int = 0    # votes for this answer


@dataclass
class VoteRec:
    """
    VOTING.DAT — One voting question.

    20 questions, 15 answers each.
    PIXEL8 mapping: entity congress / governance voting.
    """
    active:   bool = False
    question: str  = ""
    voteacs:  str  = ""   # ACS to vote
    addacs:   str  = ""   # ACS to add answers
    numusers: int  = 0    # users who have answered
    numans:   int  = 0    # active answers
    answer:   List[VoteAnswer] = field(
        default_factory=lambda: [VoteAnswer() for _ in range(NUMVOTEAS)]
    )


# ─── Drop File (Door Interface) ──────────────────────────────────────────────

@dataclass
class DropFile:
    """
    The drop file — what Telegard writes before launching a door program.

    This IS the Henry Report.
    Every field Tim Strike put here, we put in HenryReport.
    The pattern is 37 years old.

    When Telegard launches a door:
      1. Write this to DOOR.SYS or CHAIN.TXT
      2. Shell out to the door program
      3. Door reads this file, runs, exits
      4. Control returns to Telegard

    PIXEL8:
      1. Henry writes HenryReport (this)
      2. Fraggle dispatches Doozer
      3. Doozer reads report, runs, returns
      4. Control returns to liminal state

    Format: based on GAP/RBBS-PC/PCBoard DOOR.SYS standard.
    Not invented by Telegard — predates it.
    """
    # Connection
    comport:     int = 0       # COM port (0 = local)
    baud:        int = 0       # connection speed
    node:        int = 1       # node number

    # User identity
    realname:    str = ""      # user's real name
    handle:      str = ""      # user's handle/alias
    location:    str = ""      # city, state

    # Access
    sl:          int = 0       # security level
    level:       str = "A"     # validation level
    userID:      int = 0       # unique user ID

    # Time
    time_limit:  int = 60      # minutes allowed this call
    time_used:   int = 0       # minutes used so far

    # Display
    graphics:    int = GRAPHICS_ANSI
    linelen:     int = 80
    pagelen:     int = 24

    # Session
    logon_time:  Optional[datetime.datetime] = None
    sysop_next:  bool = False   # sysop coming online after door?
    door_name:   str = ""       # name of this door

    def to_dict(self) -> dict:
        return {
            "comport":    self.comport,
            "baud":       self.baud,
            "node":       self.node,
            "realname":   self.realname,
            "handle":     self.handle,
            "location":   self.location,
            "sl":         self.sl,
            "level":      self.level,
            "userID":     self.userID,
            "time_limit": self.time_limit,
            "time_used":  self.time_used,
            "graphics":   self.graphics,
            "linelen":    self.linelen,
            "pagelen":    self.pagelen,
            "door_name":  self.door_name,
        }


# ─── Mission Taxonomy ────────────────────────────────────────────────────────

class MissionType(IntEnum):
    """
    Mission types as door program categories.
    Telegard had: door games, utilities, chat, file requests.
    PIXEL8 has: missions, commissions, bounty, scavenger, adventure.

    The DropFile is the handoff for all of them.
    Fraggle dispatches the right Doozer based on mission type.
    """
    MISSION      = 1   # general mission — a task with clear completion
    COMMISSION   = 2   # commissioned work — someone asked for this
    BOUNTY       = 3   # reward-based — find/fix something, claim reward
    SCAVENGER    = 4   # find-based — gather components or artifacts
    ADVENTURE    = 5   # exploration — outcome unknown at start
    ARTISAN      = 6   # craft-based — create an artifact
    EXPEDITION   = 7   # multi-stage journey with checkpoints


MISSION_VALUATION = {
    # (mission_type, completion_quality) → tier
    # Same ℞/§/$/ €/∞ system as entity certification
    # Quality: 0=abandoned 1=minimal 2=standard 3=quality 4=artifact+lineage
    (MissionType.MISSION,   0): ("℞", "NEEDS_WORK"),
    (MissionType.MISSION,   1): ("§",  "BASIC"),
    (MissionType.MISSION,   2): ("$",  "STANDARD"),
    (MissionType.MISSION,   3): ("€",  "ADVANCED"),
    (MissionType.MISSION,   4): ("∞",  "PINNACLE"),
    # PINNACLE requires: completion + artifact created + lineage documented
}


# ─── Smoke Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("SOVRAN TELEGARD — Models Smoke Test")
    print("=" * 40)

    # Create a user
    u = UserRec(
        name="FRAGGLE",
        realname="Fraggle Rock",
        userID=1001,
        level="Z",
        totalcalls=42,
        pubpost=17,
    )
    print(f"\nUser: {u.name} (ID:{u.userID}) Level:{u.level} Sysop:{u.is_sysop}")

    # Create a drop file — the Henry Report ancestor
    drop = DropFile(
        handle=u.name,
        realname=u.realname,
        userID=u.userID,
        level=u.level,
        time_limit=60,
        door_name="TRADE_WARS_2002",
    )
    print(f"\nDrop File: {drop.door_name} → user {drop.handle} ({drop.time_limit}min)")
    print(f"  as dict: {drop.to_dict()}")

    # Event (One Hertz ancestor)
    evt = EventRec(
        active=True,
        etype="E",
        desc="Nightly Henry scan",
        execdata="python3 henry.py --scan /repo",
        exectime=180,   # 3:00 AM
    )
    print(f"\nEvent: '{evt.desc}' — External: {evt.is_external}")

    # Vote
    v = VoteRec(
        active=True,
        question="Which entity should be certified next?",
        numusers=7,
        numans=3,
    )
    v.answer[0] = VoteAnswer(desc="ZipMancer",  numres=4)
    v.answer[1] = VoteAnswer(desc="ZapMancer",  numres=2)
    v.answer[2] = VoteAnswer(desc="MollyBolt",  numres=1)
    print(f"\nVote: '{v.question}'")
    for a in v.answer[:v.numans]:
        print(f"  {a.numres:2d} votes — {a.desc}")

    print("\n∰◊€π¿🌌∞")
    print("Sovran Telegard models: READY")
