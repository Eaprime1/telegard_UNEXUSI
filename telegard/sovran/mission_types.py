"""
MISSION TYPES — Pinnacle Taxonomy
===================================
The pinnacle system for mission classification.

Telegard had door programs: Trade Wars, LORD, chat utilities, file tools.
Each door = a different kind of thing you could do.

PIXEL8 has mission types.
Each mission type = a different kind of dispatch.
Fraggle routes to the right Doozer based on mission_type.

VALUATION (same system as entity certification):
  ℞  NEEDS_WORK  → incomplete / abandoned mid-run
  §  BASIC       → completed, minimum viable
  $  STANDARD    → completed with quality
  €  ADVANCED    → completed + secondary objectives unlocked
  ∞  PINNACLE    → completed + artifact created + lineage documented

A mission that generates a certified entity at the end = ∞ PINNACLE.
The system pressures toward quality naturally — not a rule, just what the tiers reward.

€(mission_types_v1)
∰◊€π¿🌌∞
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from enum import Enum
import datetime


# ─── Mission Types ────────────────────────────────────────────────────────────

class MissionType(str, Enum):
    """
    The seven mission types.

    Each maps to a Telegard door program category:
      MISSION    → utility door (specific task, clear output)
      COMMISSION → requested custom work (someone placed an order)
      BOUNTY     → reward door (find/fix, claim points)
      SCAVENGER  → file request door (gather components)
      ADVENTURE  → game door (Trade Wars, LORD — outcome unknown)
      ARTISAN    → creation door (write something, build something)
      EXPEDITION → multi-node tour (checkpoints, stages)

    "Head pressure" flows through these:
      simple missions = low pressure (utility doors)
      expeditions = high pressure (multi-stage, multi-node)
    """
    MISSION    = "mission"     # task with clear completion criteria
    COMMISSION = "commission"  # someone asked for this specifically
    BOUNTY     = "bounty"      # find/fix something, claim reward
    SCAVENGER  = "scavenger"   # gather artifacts or components
    ADVENTURE  = "adventure"   # exploration, outcome unknown at start
    ARTISAN    = "artisan"     # create a certified artifact
    EXPEDITION = "expedition"  # multi-stage journey with checkpoints


# ─── Completion Quality ───────────────────────────────────────────────────────

class CompletionQuality(int, Enum):
    """
    How well was the mission completed?
    This maps to valuation tier.
    """
    ABANDONED  = 0  # ℞ abandoned mid-run
    MINIMAL    = 1  # § minimum viable completion
    STANDARD   = 2  # $ completed with quality
    QUALITY    = 3  # € secondary objectives unlocked
    PINNACLE   = 4  # ∞ artifact created + lineage documented


# ─── Valuation ────────────────────────────────────────────────────────────────

VALUATION_MAP: Dict[CompletionQuality, tuple] = {
    CompletionQuality.ABANDONED: ("℞", "NEEDS_WORK",  0),
    CompletionQuality.MINIMAL:   ("§",  "BASIC",      25),
    CompletionQuality.STANDARD:  ("$",  "STANDARD",   50),
    CompletionQuality.QUALITY:   ("€",  "ADVANCED",   75),
    CompletionQuality.PINNACLE:  ("∞",  "PINNACLE",  100),
}

def get_mission_valuation(quality: CompletionQuality) -> tuple:
    """Return (symbol, tier_name, score) for a completion quality."""
    return VALUATION_MAP[quality]


# ─── Pinnacle Requirements ────────────────────────────────────────────────────

PINNACLE_REQUIREMENTS: Dict[MissionType, List[str]] = {
    MissionType.MISSION: [
        "Mission objective met",
        "Output artifact created (file, entity, document)",
        "Lineage documented (what was learned, what was built)",
    ],
    MissionType.COMMISSION: [
        "Commissioned output delivered",
        "Client satisfied (or self-certified if solo)",
        "Artifact certified (€ ADVANCED or ∞ PINNACLE)",
        "Commission record written",
    ],
    MissionType.BOUNTY: [
        "Target found/fixed",
        "Bounty claim documented (what was the target, what was done)",
        "Reward assigned to entity (filepoints / credit)",
        "Verification by Henry scan (zero remaining issues)",
    ],
    MissionType.SCAVENGER: [
        "All components gathered",
        "Manifest written (what was found, where, when)",
        "Components organized into a structure (not just a pile)",
        "ZipMancer or TrackmancerBitplane records custody",
    ],
    MissionType.ADVENTURE: [
        "Journey completed (reached the end, whatever it was)",
        "Adventure log written (what was encountered, what changed)",
        "At least one certified artifact born from the journey",
        "The unexpected thing: document the surprise",
    ],
    MissionType.ARTISAN: [
        "Artifact created (entity, document, system, poem, tool)",
        "Artifact certified (passes certification process)",
        "Craft notes written (why this approach, what was hard)",
        "Artifact enters the lineage (linked from its ancestry)",
    ],
    MissionType.EXPEDITION: [
        "All checkpoints reached",
        "Stage reports written (one per checkpoint)",
        "Overall expedition report written",
        "At least one artifact per stage",
        "The system is better for the expedition having happened",
    ],
}


# ─── Mission Record ───────────────────────────────────────────────────────────

@dataclass
class MissionRecord:
    """
    A mission record — the living document of one mission.

    Analogous to a Telegard door session:
      - starts when Fraggle writes the drop file
      - runs while the Doozer executes
      - closes when control returns to liminal

    But a mission may span multiple sessions.
    An expedition may span weeks.
    """
    mission_id:   str = ""
    mission_type: MissionType = MissionType.MISSION
    title:        str = ""
    description:  str = ""
    issuer:       str = ""   # who commissioned/launched this (entity name or "Eric")
    executor:     str = ""   # which Doozer/entity is doing this

    # Lifecycle
    started:   Optional[datetime.datetime] = None
    completed: Optional[datetime.datetime] = None
    quality:   Optional[CompletionQuality] = None

    # Artifacts
    artifacts:      List[str] = field(default_factory=list)   # paths to outputs
    lineage_doc:    str = ""   # path to lineage/notes document
    certification:  str = ""   # cert timestamp if artifact was certified

    # Checkpoints (for expeditions)
    checkpoints: List[dict] = field(default_factory=list)

    # Chain of custody
    coc_entries: List[dict] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return self.completed is not None

    @property
    def valuation(self) -> Optional[tuple]:
        if self.quality is None:
            return None
        return get_mission_valuation(self.quality)

    @property
    def is_pinnacle(self) -> bool:
        return self.quality == CompletionQuality.PINNACLE

    def add_coc(self, action: str, actor: str, note: str = ""):
        self.coc_entries.append({
            "ts":     datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
            "action": action,
            "actor":  actor,
            "note":   note,
        })

    def complete(self, quality: CompletionQuality, artifact_paths: List[str] = None):
        self.completed = datetime.datetime.now()
        self.quality   = quality
        if artifact_paths:
            self.artifacts.extend(artifact_paths)
        sym, tier, score = get_mission_valuation(quality)
        self.add_coc("COMPLETED", self.executor, f"{sym} {tier} ({score}/100)")

    def pinnacle_checklist(self) -> dict:
        """Return the pinnacle requirements for this mission type."""
        reqs = PINNACLE_REQUIREMENTS.get(self.mission_type, [])
        return {
            "mission_type": self.mission_type.value,
            "requirements": reqs,
            "count": len(reqs),
        }


# ─── Head Pressure ────────────────────────────────────────────────────────────

@dataclass
class SystemPressure:
    """
    System head pressure — the artesian concept.

    An artesian well: water under pressure from depth + geology.
    It flows without pumping. But if you bore too many wells
    in one aquifer, the pressure drops and the flow stops.

    This system:
      active_missions = wells bored
      system_load     = aquifer pressure
      head_pressure   = combined demand

    The one_hertz_collective monitors this.
    The artesian_monitor.py reads it.
    """
    active_missions: int = 0
    parallel_ops:    int = 0
    system_load_pct: float = 0.0   # from artesian_monitor
    memory_pct:      float = 0.0

    @property
    def head_pressure(self) -> float:
        """
        Combined head pressure score 0-100.
        Weighted: system_load 40%, missions 30%, parallel_ops 20%, memory 10%.
        """
        mission_score = min(self.active_missions * 15, 100)
        ops_score     = min(self.parallel_ops * 20, 100)
        return round(
            self.system_load_pct * 0.40 +
            mission_score        * 0.30 +
            ops_score            * 0.20 +
            self.memory_pct      * 0.10,
            1
        )

    @property
    def label(self) -> str:
        p = self.head_pressure
        if p >= 95: return "OVERFLOW — yield something"
        if p >= 80: return "HIGH — reduce parallel ops"
        if p >= 60: return "CAUTION — watch carefully"
        return "BREATHING — all good"


# ─── Smoke Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("MISSION TYPES — Pinnacle Taxonomy")
    print("=" * 50)

    # Show all types and their pinnacle requirements
    for mt in MissionType:
        reqs = PINNACLE_REQUIREMENTS[mt]
        print(f"\n∞ {mt.value.upper()} PINNACLE requires:")
        for r in reqs:
            print(f"  ✓ {r}")

    print("\n" + "─" * 50)

    # Create a sample mission
    m = MissionRecord(
        mission_id="202603260001",
        mission_type=MissionType.ADVENTURE,
        title="Explore the Telegard Archive",
        description="Rediscover the ancestor architecture. Document lineage.",
        issuer="Eric Pace",
        executor="Claude",
    )
    m.started = datetime.datetime(2026, 3, 25, 19, 20)
    m.add_coc("STARTED", "Eric Pace", "Timestamp 202603251920")
    m.add_coc("DISCOVERY", "Claude", "Door interface = Doozer dispatch. Convergent engineering.")
    m.complete(
        CompletionQuality.PINNACLE,
        artifact_paths=["LINEAGE.md", "TELEGARD_SEED.md", "sovran/models.py"]
    )

    sym, tier, score = m.valuation
    print(f"\nMission: {m.title}")
    print(f"Type:     {m.mission_type.value}")
    print(f"Executor: {m.executor}")
    print(f"Result:   {sym} {tier} ({score}/100)")
    print(f"Pinnacle: {m.is_pinnacle}")
    print(f"Artifacts: {m.artifacts}")
    print(f"\nCoC:")
    for e in m.coc_entries:
        print(f"  [{e['ts']}] {e['actor']}: {e['action']} — {e['note']}")

    print("\n─" * 50)
    sp = SystemPressure(
        active_missions=3,
        parallel_ops=4,
        system_load_pct=55,
        memory_pct=42,
    )
    print(f"\nSystem Pressure: {sp.head_pressure} — {sp.label}")

    print("\n∰◊€π¿🌌∞")
    print("Mission taxonomy: READY")
