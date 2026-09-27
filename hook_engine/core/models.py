"""
Dataclasses and Enums representing the Hook Model entities, audit findings,
and scoring models based on Nir Eyal's 'Hooked'.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


class TriggerType(str, Enum):
    PAID = "paid"                 # Search ads, display ads, sponsored posts
    EARNED = "earned"             # PR, App Store features, viral mentions
    RELATIONSHIP = "relationship" # Word-of-mouth, invites, referral links
    OWNED = "owned"               # Push notifications, app icons, newsletters
    INTERNAL = "internal"         # Emotional itch (boredom, fear, loneliness, etc.)


class InternalItch(str, Enum):
    BOREDOM = "boredom"
    LONELINESS = "loneliness"
    UNCERTAINTY = "uncertainty"
    ANXIETY = "anxiety"
    FOMO = "fomo"
    INSECURITY = "insecurity"
    FATIGUE = "fatigue"
    CURIOSITY = "curiosity"
    OTHER = "other"


class FoggLever(str, Enum):
    """The 6 Elements of Simplicity from Dr. B.J. Fogg's Behavior Model (B=MAT)."""
    TIME = "time"                         # Seconds/minutes to finish action
    MONEY = "money"                       # Financial cost or upfront payment
    PHYSICAL_EFFORT = "physical_effort"   # Clicks, taps, typing, physical movement
    MENTAL_EFFORT = "mental_effort"       # Cognitive load, thinking, confusion
    SOCIAL_DEVIANCE = "social_deviance"   # Going against social norms
    ROUTINE_DISRUPTION = "routine_disruption" # Disrupting existing user routines


class RewardType(str, Enum):
    TRIBE = "tribe"   # Social validation, likes, belonging, peer competition
    HUNT = "hunt"     # Information, cash, deals, novel algorithmic content
    SELF = "self"     # Competence, mastery, completion, clearing inbox/levels


class StoredValueType(str, Enum):
    CONTENT = "content"       # Documents, photos, playlists, articles created
    DATA = "data"             # Usage history, logs, metrics, preferences
    FOLLOWERS = "followers"   # Social graph, audience, contacts synced
    REPUTATION = "reputation" # Ratings, badges, karma, public standing
    SKILL = "skill"           # Shortcuts mastered, muscle memory, workflows


class ManipulationQuadrant(str, Enum):
    FACILITATOR = "facilitator"   # Maker uses it + materially improves user life (Highest integrity)
    PEDDLER = "peddler"           # Maker does NOT use it + claims it improves user life
    ENTERTAINER = "entertainer"   # Maker uses it + ephemeral fun (no material improvement)
    DEALER = "dealer"             # Maker does NOT use it + causes compulsive harm (Addiction/Sludge)


class FindingSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class HookTrigger:
    id: str
    name: str
    trigger_type: TriggerType
    description: str
    channel: str = ""                       # e.g., "push_notification", "email", "app_icon"
    internal_itch: Optional[InternalItch] = None
    is_recurring: bool = False
    source_reference: str = ""              # e.g., "src/jobs/notification.ts"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "trigger_type": self.trigger_type.value,
            "description": self.description,
            "channel": self.channel,
            "internal_itch": self.internal_itch.value if self.internal_itch else None,
            "is_recurring": self.is_recurring,
            "source_reference": self.source_reference,
        }


@dataclass
class HookAction:
    id: str
    name: str
    description: str
    steps_count: int = 1                    # Clicks or steps required
    input_fields_count: int = 0             # Inputs user must fill
    requires_auth_wall: bool = False        # Does it gate user behind login/signup upfront?
    requires_payment: bool = False          # Requires credit card upfront?
    fogg_friction_levers: List[FoggLever] = field(default_factory=list)
    source_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps_count": self.steps_count,
            "input_fields_count": self.input_fields_count,
            "requires_auth_wall": self.requires_auth_wall,
            "requires_payment": self.requires_payment,
            "fogg_friction_levers": [lever.value for lever in self.fogg_friction_levers],
            "source_reference": self.source_reference,
        }


@dataclass
class HookReward:
    id: str
    name: str
    reward_type: RewardType
    is_variable: bool = True
    is_infinite_variability: bool = False   # True if reward constantly changes (e.g. social feed)
    dopamine_delivery_latency_seconds: float = 1.0 # How fast reward arrives after action
    description: str = ""
    source_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "reward_type": self.reward_type.value,
            "is_variable": self.is_variable,
            "is_infinite_variability": self.is_infinite_variability,
            "dopamine_delivery_latency_seconds": self.dopamine_delivery_latency_seconds,
            "description": self.description,
            "source_reference": self.source_reference,
        }


@dataclass
class HookInvestment:
    id: str
    name: str
    stored_value_type: StoredValueType
    description: str
    loads_next_trigger: bool = True         # Does this investment prime a future external trigger?
    effort_tier: str = "micro"              # "micro", "medium", "heavy"
    source_reference: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "stored_value_type": self.stored_value_type.value,
            "description": self.description,
            "loads_next_trigger": self.loads_next_trigger,
            "effort_tier": self.effort_tier,
            "source_reference": self.source_reference,
        }


@dataclass
class HookGraph:
    """Represents the complete extracted Hook loop pathways in a target project."""
    project_name: str
    triggers: List[HookTrigger] = field(default_factory=list)
    actions: List[HookAction] = field(default_factory=list)
    rewards: List[HookReward] = field(default_factory=list)
    investments: List[HookInvestment] = field(default_factory=list)
    loop_connected: bool = False            # True if trigger -> action -> reward -> investment is closed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "triggers": [t.to_dict() for t in self.triggers],
            "actions": [a.to_dict() for a in self.actions],
            "rewards": [r.to_dict() for r in self.rewards],
            "investments": [i.to_dict() for i in self.investments],
            "loop_connected": self.loop_connected,
        }


@dataclass
class Finding:
    control_id: str                         # e.g., "HOOK-TRIG-01", "HOOK-ACT-03"
    phase: str                              # "trigger", "action", "reward", "investment", "ethics"
    title: str
    verdict: FindingVerdict
    severity: FindingSeverity
    observation: str
    evidence: str
    recommendation: str
    code_patch_target: Optional[str] = None # Filepath to fix, if detectable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "control_id": self.control_id,
            "phase": self.phase,
            "title": self.title,
            "verdict": self.verdict.value,
            "severity": self.severity.value,
            "observation": self.observation,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "code_patch_target": self.code_patch_target,
        }


@dataclass
class HabitZoneCoordinate:
    frequency_score: float                  # 0 to 10 (Daily = 10, Weekly = 6, Monthly = 3, Rare = 1)
    perceived_utility_score: float          # 0 to 10 (Critical painkiller = 10, Nice-to-have vitamin = 2)
    in_habit_zone: bool                     # True if falls above habit threshold curve
    classification: str                     # "Painkiller Habit", "Vitamin Habit", "Churn Graveyard", "Rare Utility"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frequency_score": self.frequency_score,
            "perceived_utility_score": self.perceived_utility_score,
            "in_habit_zone": self.in_habit_zone,
            "classification": self.classification,
        }


@dataclass
class AuditBundle:
    """The complete versioned JSON artifact describing an end-to-end Hook Model audit."""
    project_name: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
    version: str = "1.0.0"
    overall_habit_health_score: int = 0     # 0 to 100
    habit_zone: HabitZoneCoordinate = field(
        default_factory=lambda: HabitZoneCoordinate(5.0, 5.0, False, "Uncalculated")
    )
    manipulation_matrix_quadrant: ManipulationQuadrant = ManipulationQuadrant.FACILITATOR
    fogg_simplicity_score: int = 50         # 0 (high friction) to 100 (frictionless)
    reward_entropy_score: int = 50          # 0 (completely finite) to 100 (infinite)
    stored_value_score: int = 50            # 0 (zero investment) to 100 (high compounding value)
    hook_graph: HookGraph = field(default_factory=lambda: HookGraph("Unknown"))
    findings: List[Finding] = field(default_factory=list)
    simulation_results: Dict[str, Any] = field(default_factory=dict)
    summary_verdict: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "timestamp": self.timestamp,
            "version": self.version,
            "overall_habit_health_score": self.overall_habit_health_score,
            "habit_zone": self.habit_zone.to_dict(),
            "manipulation_matrix_quadrant": self.manipulation_matrix_quadrant.value,
            "fogg_simplicity_score": self.fogg_simplicity_score,
            "reward_entropy_score": self.reward_entropy_score,
            "stored_value_score": self.stored_value_score,
            "hook_graph": self.hook_graph.to_dict(),
            "findings": [f.to_dict() for f in self.findings],
            "simulation_results": self.simulation_results,
            "summary_verdict": self.summary_verdict,
        }
