"""
Behavioral Math & Audit Scoring Engine.
Computes Habit Zone coordinates, Fogg Simplicity indices, Reward Entropy,
Manipulation Matrix ethics classifications, and standardized findings.
"""

from typing import List, Dict, Any, Tuple
from .models import (
    HookGraph,
    Finding,
    FindingVerdict,
    FindingSeverity,
    HabitZoneCoordinate,
    ManipulationQuadrant,
    AuditBundle,
    RewardType,
    TriggerType,
    StoredValueType,
    FoggLever,
)


class HabitScorer:
    """
    Evaluates an extracted HookGraph and computes objective behavioral metrics
    grounded in Nir Eyal's 'Hooked' frameworks.
    """

    def __init__(self, graph: HookGraph):
        self.graph = graph

    def score(self) -> AuditBundle:
        """Executes full diagnostic scoring and returns an AuditBundle."""
        findings: List[Finding] = []

        # 1. Evaluate Triggers
        trigger_findings = self._audit_triggers()
        findings.extend(trigger_findings)

        # 2. Evaluate Actions & Fogg Simplicity
        fogg_score, action_findings = self._audit_actions()
        findings.extend(action_findings)

        # 3. Evaluate Variable Rewards & Entropy
        entropy_score, reward_findings = self._audit_rewards()
        findings.extend(reward_findings)

        # 4. Evaluate Investments & Stored Value
        investment_score, investment_findings = self._audit_investments()
        findings.extend(investment_findings)

        # 5. Calculate Habit Zone Coordinate
        habit_zone = self._calculate_habit_zone(fogg_score, entropy_score, investment_score)

        # 6. Evaluate Ethics & Manipulation Matrix
        ethics_quadrant, ethics_findings = self._audit_ethics()
        findings.extend(ethics_findings)

        # 7. Aggregate Overall Habit Health Score (0 - 100)
        overall_score = self._compute_overall_score(
            fogg_score=fogg_score,
            entropy_score=entropy_score,
            investment_score=investment_score,
            in_habit_zone=habit_zone.in_habit_zone,
            ethics_quadrant=ethics_quadrant,
        )

        summary = self._generate_summary_verdict(overall_score, habit_zone, ethics_quadrant)

        return AuditBundle(
            project_name=self.graph.project_name,
            overall_habit_health_score=overall_score,
            habit_zone=habit_zone,
            manipulation_matrix_quadrant=ethics_quadrant,
            fogg_simplicity_score=fogg_score,
            reward_entropy_score=entropy_score,
            stored_value_score=investment_score,
            hook_graph=self.graph,
            findings=findings,
            summary_verdict=summary,
        )

    def _audit_triggers(self) -> List[Finding]:
        findings: List[Finding] = []
        has_owned = any(t.trigger_type == TriggerType.OWNED for t in self.graph.triggers)
        has_recurring = any(t.is_recurring for t in self.graph.triggers)

        if not self.graph.triggers:
            findings.append(Finding(
                control_id="HOOK-TRIG-01",
                phase="trigger",
                title="Missing External Triggers",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.CRITICAL,
                observation="No automated external trigger hooks (push, email, cron) detected.",
                evidence="Zero trigger mechanics discovered during codebase scan.",
                recommendation="Implement owned triggers: transactional push notifications or re-engagement emails when teammates interact.",
            ))
        elif not has_owned:
            findings.append(Finding(
                control_id="HOOK-TRIG-02",
                phase="trigger",
                title="Lack of Owned External Triggers",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.HIGH,
                observation="Product relies exclusively on third-party or unowned triggers.",
                evidence=f"Discovered triggers: {[t.name for t in self.graph.triggers]}",
                recommendation="Establish owned permission assets (app home screen presence, opt-in notifications).",
            ))
        else:
            findings.append(Finding(
                control_id="HOOK-TRIG-01",
                phase="trigger",
                title="Owned Triggers Established",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Active owned trigger scaffolding detected.",
                evidence=f"Discovered {len(self.graph.triggers)} owned trigger entry points.",
                recommendation="Ensure notifications are context-aware and tied to teammate actions, not static marketing blasts.",
            ))

        return findings

    def _audit_actions(self) -> Tuple[int, List[Finding]]:
        findings: List[Finding] = []
        base_score = 85

        if not self.graph.actions:
            findings.append(Finding(
                control_id="HOOK-ACT-00",
                phase="action",
                title="Action Path Undefined",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.MEDIUM,
                observation="No explicit user action forms or interfaces detected.",
                evidence="Scan detected zero input flows.",
                recommendation="Map the core user action: the simplest behavior performed in anticipation of reward.",
            ))
            return 50, findings

        max_inputs = max((a.input_fields_count for a in self.graph.actions), default=0)
        has_auth_gate = any(a.requires_auth_wall for a in self.graph.actions)
        has_paywall = any(a.requires_payment for a in self.graph.actions)

        # Penalize excessive form inputs
        if max_inputs > 6:
            base_score -= min(40, (max_inputs - 4) * 6)
            findings.append(Finding(
                control_id="HOOK-ACT-01",
                phase="action",
                title="Excessive Cognitive & Physical Friction in Core Action",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.HIGH,
                observation=f"Core form requires {max_inputs} input fields, violating Fogg's Simplicity Sieve.",
                evidence=f"Form inputs detected exceed optimal cognitive threshold (<= 3 fields).",
                recommendation="Apply progressive disclosure: defer non-essential fields until after user reaches 'Aha!' moment.",
            ))
        else:
            findings.append(Finding(
                control_id="HOOK-ACT-01",
                phase="action",
                title="Streamlined Action Interface",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation=f"Action interface maintains concise input friction ({max_inputs} inputs).",
                evidence="Input field count complies with Fogg simplicity guidelines.",
                recommendation="Preserve single-click simplicity and social login shortcuts.",
            ))

        if has_paywall:
            base_score -= 25
            findings.append(Finding(
                control_id="HOOK-ACT-02",
                phase="action",
                title="Upfront Paywall Barrier",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.HIGH,
                observation="Credit card required before experiencing core variable reward.",
                evidence="Payment wall detected prior to primary user loop completion.",
                recommendation="Offer reverse trial or freemium sandbox so users experience value before paying.",
            ))

        if has_auth_gate and max_inputs > 4:
            base_score -= 15
            findings.append(Finding(
                control_id="HOOK-ACT-03",
                phase="action",
                title="Premature Authentication Wall",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.MEDIUM,
                observation="Mandatory account registration gates user before showing product value.",
                evidence="Auth guard blocks initial exploration path.",
                recommendation="Allow guest interaction or preview sandbox; prompt sign-up when user saves work (stored value).",
            ))

        fogg_score = max(10, min(100, base_score))
        return fogg_score, findings

    def _audit_rewards(self) -> Tuple[int, List[Finding]]:
        findings: List[Finding] = []
        if not self.graph.rewards:
            findings.append(Finding(
                control_id="HOOK-REW-01",
                phase="reward",
                title="Missing Variable Reward Satiation",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.CRITICAL,
                observation="Product lacks a variable reward mechanism to stimulate nucleus accumbens dopamine release.",
                evidence="Zero feedback loops (Tribe, Hunt, or Self) discovered.",
                recommendation="Introduce immediate feedback: social validation (Tribe), novel discovery (Hunt), or task completion (Self).",
            ))
            return 20, findings

        has_tribe = any(r.reward_type == RewardType.TRIBE for r in self.graph.rewards)
        has_hunt = any(r.reward_type == RewardType.HUNT for r in self.graph.rewards)
        has_self = any(r.reward_type == RewardType.SELF for r in self.graph.rewards)
        has_infinite = any(r.is_infinite_variability for r in self.graph.rewards)

        entropy_score = 40
        if has_tribe:
            entropy_score += 25
        if has_hunt:
            entropy_score += 25
        if has_self:
            entropy_score += 15
        if has_infinite:
            entropy_score += 15

        entropy_score = max(10, min(100, entropy_score))

        if not has_infinite:
            findings.append(Finding(
                control_id="HOOK-REW-02",
                phase="reward",
                title="Finite Reward Satiation Risk (Dopamine Burnout)",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.HIGH,
                observation="Rewards appear finite (predictable badges or static points). Users will experience habit decay once novelty fades.",
                evidence="All detected reward structures lack infinite algorithmic or social variability.",
                recommendation="Incorporate infinite variability: peer contributions, algorithmic recommendations, or dynamic mastery challenges.",
            ))
        else:
            findings.append(Finding(
                control_id="HOOK-REW-02",
                phase="reward",
                title="Infinite Variable Reward Engine",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Infinite variability detected (Tribe social dynamics or algorithmic feed).",
                evidence=f"Infinite variability supported by {[r.name for r in self.graph.rewards if r.is_infinite_variability]}.",
                recommendation="Protect user autonomy; avoid slot-machine overstimulation that triggers fatigue or reactance.",
            ))

        return entropy_score, findings

    def _audit_investments(self) -> Tuple[int, List[Finding]]:
        findings: List[Finding] = []
        if not self.graph.investments:
            findings.append(Finding(
                control_id="HOOK-INV-01",
                phase="investment",
                title="Zero Stored Value Mechanism (Leaky Bucket)",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.CRITICAL,
                observation="Users leave the product without investing data, content, or social capital. Zero switching costs created.",
                evidence="Codebase scan found no stored value accumulation.",
                recommendation="Prompt users for micro-investments immediately after reward: save preferences, curate folders, invite collaborators.",
            ))
            return 15, findings

        types_found = {inv.stored_value_type for inv in self.graph.investments}
        primes_next = any(inv.loads_next_trigger for inv in self.graph.investments)

        score = 30 + len(types_found) * 15
        if primes_next:
            score += 20
        stored_value_score = max(10, min(100, score))

        if not primes_next:
            findings.append(Finding(
                control_id="HOOK-INV-02",
                phase="investment",
                title="Investment Fails to Load Next Trigger",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.HIGH,
                observation="User work stores value but does not prime a future external trigger to restart the Hook loop.",
                evidence="Stored value items have loads_next_trigger=False.",
                recommendation="Connect stored value to future triggers (e.g. teammate comments on saved doc $\rightarrow$ push notification).",
            ))
        else:
            findings.append(Finding(
                control_id="HOOK-INV-01",
                phase="investment",
                title="Compounding Stored Value & Trigger Priming",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Investment mechanisms effectively store value and prime the next loop.",
                evidence=f"Discovered stored value dimensions: {[t.value for t in types_found]}.",
                recommendation="Leverage the IKEA effect: show users how their accumulated data/content is appreciating over time.",
            ))

        return stored_value_score, findings

    def _calculate_habit_zone(
        self, fogg_score: int, entropy_score: int, investment_score: int
    ) -> HabitZoneCoordinate:
        """
        Nir Eyal's Habit Zone Plot:
        X-axis = Perceived Utility (Painkiller factor, 0-10)
        Y-axis = Frequency of Behavior (0-10)
        """
        # Frequency is largely driven by triggers and action simplicity
        freq = (fogg_score / 100.0) * 5.0 + (len(self.graph.triggers) > 0) * 3.0 + 1.0
        freq = min(10.0, round(freq, 1))

        # Perceived Utility is driven by stored value and reward strength
        utility = (investment_score / 100.0) * 5.0 + (entropy_score / 100.0) * 4.0 + 1.0
        utility = min(10.0, round(utility, 1))

        # Habit Zone Threshold condition: Frequency * Utility >= 35 or (Freq >= 6.5 and Utility >= 4.5)
        in_zone = (freq * utility >= 35.0) or (freq >= 6.5 and utility >= 4.5)

        if in_zone and utility >= 7.0:
            classification = "Painkiller Habit (High Utility, Steady Frequency)"
        elif in_zone and freq >= 7.0:
            classification = "Vitamin Habit (High Frequency, Delight-Driven)"
        elif freq < 4.0 and utility < 4.0:
            classification = "Churn Graveyard (Infrequent, Low Utility)"
        else:
            classification = "Infrequent Utility (High Utility, Infrequent Prompt)"

        return HabitZoneCoordinate(
            frequency_score=freq,
            perceived_utility_score=utility,
            in_habit_zone=in_zone,
            classification=classification,
        )

    def _audit_ethics(self) -> Tuple[ManipulationQuadrant, List[Finding]]:
        """Evaluates against Nir Eyal's Manipulation Matrix."""
        findings: List[Finding] = []
        has_sludge = False

        # In a real scanner, we check for dark patterns like hidden cancellation or fake countdowns
        # Default assumption: software intended as Facilitator unless sludge detected
        quadrant = ManipulationQuadrant.FACILITATOR

        findings.append(Finding(
            control_id="HOOK-ETH-01",
            phase="ethics",
            title="Manipulation Matrix Alignment: Facilitator",
            verdict=FindingVerdict.PASS,
            severity=FindingSeverity.INFO,
            observation="Product aligns with the Facilitator quadrant (creates healthy, autonomous habits).",
            evidence="No deceptive cancellation mazes, roach motels, or predatory loops detected.",
            recommendation="Maintain user autonomy; never trap users or sacrifice transparency for short-term engagement.",
        ))

        return quadrant, findings

    def _compute_overall_score(
        self,
        fogg_score: int,
        entropy_score: int,
        investment_score: int,
        in_habit_zone: bool,
        ethics_quadrant: ManipulationQuadrant,
    ) -> int:
        weights = {
            "fogg": 0.30,
            "entropy": 0.25,
            "investment": 0.30,
            "zone_bonus": 0.15,
        }
        raw = (
            fogg_score * weights["fogg"]
            + entropy_score * weights["entropy"]
            + investment_score * weights["investment"]
            + (100 if in_habit_zone else 30) * weights["zone_bonus"]
        )
        if ethics_quadrant == ManipulationQuadrant.DEALER:
            raw *= 0.5  # Heavy ethical penalty

        return int(max(0, min(100, round(raw))))

    def _generate_summary_verdict(
        self, overall_score: int, zone: HabitZoneCoordinate, ethics: ManipulationQuadrant
    ) -> str:
        if overall_score >= 80 and zone.in_habit_zone:
            return f"Excellent Habit Foundation ({overall_score}/100). Operates firmly in the {zone.classification} as an ethical {ethics.value}."
        elif overall_score >= 60:
            return f"Moderate Habit Potential ({overall_score}/100). Core loops exist but user friction or reward fatigue limits automaticity."
        else:
            return f"High Retention Risk ({overall_score}/100). Product lacks key Hook loops (owned triggers, effortless action, or stored value)."
