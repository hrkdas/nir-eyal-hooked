"""
Psychographic User Archetypes and Cohort Definitions for Behavioral Simulation.
Based on Fogg's Behavior Model (B=MAT) and Nir Eyal's user habit segments.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any
from ..core.models import InternalItch


class UserArchetype(str, Enum):
    NOVICE = "casual_novice"              # Low motivation, low patience, easily distracted
    ANXIOUS_PRO = "anxious_professional"  # High pain/itch, high motivation, zero time
    CYNIC_SKEPTIC = "cynical_skeptic"     # High skill, highly sensitive to auth/dark patterns
    POWER_DEVOTEE = "power_devotee"       # Early adopter, high willingness to invest
    BUSY_MULTITASKER = "busy_multitasker" # Fragmented attention, mobile-only, drop-off prone


@dataclass
class UserCohort:
    archetype: UserArchetype
    display_name: str
    description: str
    population_size: int = 100
    base_motivation: float = 0.50          # 0.0 (apathetic) to 1.0 (obsessed)
    base_ability: float = 0.50             # 0.0 (low tech literacy) to 1.0 (power user)
    patience: float = 0.50                 # Tolerance for multi-step flows
    primary_internal_itch: InternalItch = InternalItch.BOREDOM
    friction_sensitivity: float = 0.50     # Sensitivity to form fields / delays
    auth_wall_dropoff_bias: float = 0.30   # Extra penalty if gated by login upfront
    paywall_dropoff_bias: float = 0.70    # Extra penalty if credit card required upfront

    def to_dict(self) -> Dict[str, Any]:
        return {
            "archetype": self.archetype.value,
            "display_name": self.display_name,
            "description": self.description,
            "population_size": self.population_size,
            "base_motivation": self.base_motivation,
            "base_ability": self.base_ability,
            "patience": self.patience,
            "primary_internal_itch": self.primary_internal_itch.value,
            "friction_sensitivity": self.friction_sensitivity,
        }


def get_default_cohorts(population_per_cohort: int = 100) -> List[UserCohort]:
    """Generates standard five behavioral cohorts for simulation."""
    return [
        UserCohort(
            archetype=UserArchetype.NOVICE,
            display_name="The Casual Novice",
            description="Browsing out of mild curiosity or boredom. Will abandon if forced to think.",
            population_size=population_per_cohort,
            base_motivation=0.35,
            base_ability=0.30,
            patience=0.25,
            primary_internal_itch=InternalItch.BOREDOM,
            friction_sensitivity=0.85,
            auth_wall_dropoff_bias=0.45,
            paywall_dropoff_bias=0.90,
        ),
        UserCohort(
            archetype=UserArchetype.ANXIOUS_PRO,
            display_name="The Anxious Professional",
            description="Seeking immediate relief from workplace anxiety or inefficiency. Has zero time.",
            population_size=population_per_cohort,
            base_motivation=0.85,
            base_ability=0.75,
            patience=0.40,
            primary_internal_itch=InternalItch.ANXIETY,
            friction_sensitivity=0.60,
            auth_wall_dropoff_bias=0.20,
            paywall_dropoff_bias=0.40,
        ),
        UserCohort(
            archetype=UserArchetype.CYNIC_SKEPTIC,
            display_name="The Cynical Skeptic",
            description="Tech-savvy and hyper-vigilant against dark patterns, forced signups, and spam.",
            population_size=population_per_cohort,
            base_motivation=0.45,
            base_ability=0.90,
            patience=0.30,
            primary_internal_itch=InternalItch.UNCERTAINTY,
            friction_sensitivity=0.75,
            auth_wall_dropoff_bias=0.65,
            paywall_dropoff_bias=0.95,
        ),
        UserCohort(
            archetype=UserArchetype.POWER_DEVOTEE,
            display_name="The Power Devotee",
            description="Enthusiastic early adopter willing to climb learning curves if stored value is obvious.",
            population_size=population_per_cohort,
            base_motivation=0.90,
            base_ability=0.85,
            patience=0.80,
            primary_internal_itch=InternalItch.FOMO,
            friction_sensitivity=0.25,
            auth_wall_dropoff_bias=0.10,
            paywall_dropoff_bias=0.30,
        ),
        UserCohort(
            archetype=UserArchetype.BUSY_MULTITASKER,
            display_name="The Busy Multitasker",
            description="Using mobile device between errands. Frequent interruptions cause involuntary abandonment.",
            population_size=population_per_cohort,
            base_motivation=0.50,
            base_ability=0.50,
            patience=0.30,
            primary_internal_itch=InternalItch.FATIGUE,
            friction_sensitivity=0.70,
            auth_wall_dropoff_bias=0.40,
            paywall_dropoff_bias=0.80,
        ),
    ]
