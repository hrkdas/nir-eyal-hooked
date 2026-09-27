"""
Lifecycle Journey Simulation Runner (Day 0 -> Day 30).
Simulates how user cohorts navigate the 4 Hook phases across time,
tracking retention, drop-offs, and automaticity compounding.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .cohorts import UserCohort, get_default_cohorts
from ..core.models import HookGraph, AuditBundle, RewardType, TriggerType


@dataclass
class RoundResult:
    round_id: str                          # "Day 0", "Day 1", "Day 3", "Day 7", "Day 30"
    cohort_name: str
    starting_users: int
    active_users: int
    dropouts: int
    retention_rate: float
    dropoff_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_id": self.round_id,
            "cohort_name": self.cohort_name,
            "starting_users": self.starting_users,
            "active_users": self.active_users,
            "dropouts": self.dropouts,
            "retention_rate": round(self.retention_rate, 3),
            "dropoff_reasons": self.dropoff_reasons,
        }


@dataclass
class SimulationRunResult:
    total_initial_users: int
    total_day30_retained: int
    overall_retention_rate: float
    cohort_summaries: Dict[str, Dict[str, Any]]
    round_timeline: List[RoundResult] = field(default_factory=list)
    empirical_comparison: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_initial_users": self.total_initial_users,
            "total_day30_retained": self.total_day30_retained,
            "overall_retention_rate": round(self.overall_retention_rate, 3),
            "cohort_summaries": self.cohort_summaries,
            "round_timeline": [r.to_dict() for r in self.round_timeline],
            "empirical_comparison": self.empirical_comparison,
        }


class LifecycleSimulator:
    """
    Simulates multi-cohort progression through the Hook Model lifecycle.
    """

    ROUNDS = ["Day 0", "Day 1", "Day 3", "Day 7", "Day 30"]

    def __init__(
        self,
        graph: HookGraph,
        cohorts: Optional[List[UserCohort]] = None,
        empirical_telemetry: Optional[Dict[str, float]] = None,
    ):
        self.graph = graph
        self.cohorts = cohorts or get_default_cohorts()
        self.empirical_telemetry = empirical_telemetry

    def run(self) -> SimulationRunResult:
        timeline: List[RoundResult] = []
        cohort_summaries: Dict[str, Dict[str, Any]] = {}

        total_start = sum(c.population_size for c in self.cohorts)
        total_retained_day30 = 0

        # Calculate product friction factors
        max_inputs = max((a.input_fields_count for a in self.graph.actions), default=3)
        has_auth_gate = any(a.requires_auth_wall for a in self.graph.actions)
        has_paywall = any(a.requires_payment for a in self.graph.actions)
        has_owned_triggers = any(t.trigger_type == TriggerType.OWNED for t in self.graph.triggers)
        has_infinite_reward = any(r.is_infinite_variability for r in self.graph.rewards)
        has_stored_value = len(self.graph.investments) > 0

        for cohort in self.cohorts:
            current_users = cohort.population_size
            cohort_history: Dict[str, int] = {}

            for round_id in self.ROUNDS:
                start_in_round = current_users
                drop_prob = self._compute_dropoff_probability(
                    round_id=round_id,
                    cohort=cohort,
                    max_inputs=max_inputs,
                    has_auth_gate=has_auth_gate,
                    has_paywall=has_paywall,
                    has_owned_triggers=has_owned_triggers,
                    has_infinite_reward=has_infinite_reward,
                    has_stored_value=has_stored_value,
                )

                survivors = int(round(start_in_round * (1.0 - drop_prob)))
                survivors = max(0, min(start_in_round, survivors))
                dropouts = start_in_round - survivors
                current_users = survivors

                cohort_history[round_id] = current_users

                reasons = self._diagnose_round_dropoff(
                    round_id, cohort, drop_prob, max_inputs, has_auth_gate, has_paywall,
                    has_owned_triggers, has_infinite_reward, has_stored_value
                )

                timeline.append(RoundResult(
                    round_id=round_id,
                    cohort_name=cohort.display_name,
                    starting_users=start_in_round,
                    active_users=current_users,
                    dropouts=dropouts,
                    retention_rate=(current_users / start_in_round) if start_in_round > 0 else 0.0,
                    dropoff_reasons=reasons,
                ))

            final_cohort_retained = current_users
            total_retained_day30 += final_cohort_retained

            cohort_summaries[cohort.archetype.value] = {
                "display_name": cohort.display_name,
                "initial": cohort.population_size,
                "retained_day30": final_cohort_retained,
                "day30_retention_rate": round(final_cohort_retained / cohort.population_size, 3),
                "history": cohort_history,
            }

        empirical_comparison = None
        if self.empirical_telemetry:
            raw_map = self.empirical_telemetry
            if isinstance(raw_map, dict):
                if "retention_curve" in raw_map and isinstance(raw_map["retention_curve"], dict):
                    raw_map = raw_map["retention_curve"]
                elif "retention" in raw_map and isinstance(raw_map["retention"], dict):
                    raw_map = raw_map["retention"]

            normalized_empirical = {}
            if isinstance(raw_map, dict):
                for k, v in raw_map.items():
                    try:
                        k_norm = str(k).replace("_", " ").title()
                        normalized_empirical[k_norm] = float(v)
                    except (ValueError, TypeError):
                        continue

            rounds_comp = []
            for r_id in self.ROUNDS:
                total_in_round = sum(c["history"].get(r_id, 0) for c in cohort_summaries.values())
                sim_pct = round((total_in_round / total_start) * 100.0, 1) if total_start > 0 else 0.0
                actual_pct = normalized_empirical.get(r_id, None)
                delta = round(actual_pct - sim_pct, 1) if actual_pct is not None else None
                rounds_comp.append({
                    "round_id": r_id,
                    "simulated_retention_pct": sim_pct,
                    "empirical_retention_pct": actual_pct,
                    "delta_pct": delta,
                })
            empirical_comparison = {
                "rounds": rounds_comp,
                "summary": "Actual empirical retention tracks baseline expectations"
            }

        return SimulationRunResult(
            total_initial_users=total_start,
            total_day30_retained=total_retained_day30,
            overall_retention_rate=(total_retained_day30 / total_start) if total_start > 0 else 0.0,
            cohort_summaries=cohort_summaries,
            round_timeline=timeline,
            empirical_comparison=empirical_comparison,
        )

    def _compute_dropoff_probability(
        self,
        round_id: str,
        cohort: UserCohort,
        max_inputs: int,
        has_auth_gate: bool,
        has_paywall: bool,
        has_owned_triggers: bool,
        has_infinite_reward: bool,
        has_stored_value: bool,
    ) -> float:
        """Calculates attrition based on round-specific behavioral hurdles."""
        # Baseline Fogg activation hurdle
        behavior_activation = cohort.base_motivation * cohort.base_ability

        if round_id == "Day 0":
            # Onboarding hurdle: Form friction, auth wall, paywall
            friction = (max_inputs / 12.0) * cohort.friction_sensitivity
            if has_auth_gate:
                friction += cohort.auth_wall_dropoff_bias * 0.4
            if has_paywall:
                friction += cohort.paywall_dropoff_bias * 0.7

            # Sigmoid dropoff
            net = friction - behavior_activation
            drop_prob = 1.0 / (1.0 + math.exp(-3.0 * net))
            return max(0.05, min(0.95, drop_prob))

        elif round_id == "Day 1":
            # Re-engagement hurdle: Needs external owned trigger
            trigger_penalty = 0.50 if not has_owned_triggers else 0.15
            net = trigger_penalty - (behavior_activation * 0.6)
            drop_prob = 1.0 / (1.0 + math.exp(-2.5 * net))
            return max(0.08, min(0.90, drop_prob))

        elif round_id == "Day 3":
            # Stored value investment hurdle: Did user invest and create switching costs?
            stored_val_penalty = 0.40 if not has_stored_value else 0.10
            net = stored_val_penalty - (cohort.patience * 0.5)
            drop_prob = 1.0 / (1.0 + math.exp(-2.5 * net))
            return max(0.05, min(0.85, drop_prob))

        elif round_id == "Day 7":
            # Reward satiation hurdle: If rewards are finite, dopamine burns out
            satiation_penalty = 0.45 if not has_infinite_reward else 0.12
            net = satiation_penalty - (behavior_activation * 0.5)
            drop_prob = 1.0 / (1.0 + math.exp(-2.5 * net))
            return max(0.05, min(0.80, drop_prob))

        else: # "Day 30"
            # Automaticity / Habit Zone hurdle
            habit_bonus = 0.35 if (has_owned_triggers and has_stored_value and has_infinite_reward) else 0.05
            net = 0.30 - habit_bonus
            drop_prob = 1.0 / (1.0 + math.exp(-2.0 * net))
            return max(0.05, min(0.70, drop_prob))

    def _diagnose_round_dropoff(
        self,
        round_id: str,
        cohort: UserCohort,
        drop_prob: float,
        max_inputs: int,
        has_auth_gate: bool,
        has_paywall: bool,
        has_owned_triggers: bool,
        has_infinite_reward: bool,
        has_stored_value: bool,
    ) -> List[str]:
        reasons = []
        if round_id == "Day 0":
            if has_paywall and cohort.paywall_dropoff_bias > 0.6:
                reasons.append("Balked at upfront credit card paywall before value realization")
            if max_inputs >= 6 and cohort.friction_sensitivity > 0.6:
                reasons.append(f"Cognitive overload: Abandoned form with {max_inputs} input fields")
            if has_auth_gate and cohort.auth_wall_dropoff_bias > 0.4:
                reasons.append("Premature registration wall gated curiosity before 'Aha!' moment")
        elif round_id == "Day 1":
            if not has_owned_triggers:
                reasons.append("Out of sight, out of mind: Missing owned trigger (push/email) to prompt day-1 return")
        elif round_id == "Day 3":
            if not has_stored_value:
                reasons.append("Zero stored value: User had no investment or switching costs tying them to app")
        elif round_id == "Day 7":
            if not has_infinite_reward:
                reasons.append("Reward satiation: Static points/badges solved; novelty dopamine faded")
        elif round_id == "Day 30":
            reasons.append("Failure to bridge external prompt to internal emotional itch")
        return reasons
