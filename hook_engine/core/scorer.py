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
    PromptType,
    EASTScore,
    TTVMetrics,
    RATAssumption,
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

        # 7. Compute EAST Framework Score & Prompt Alignment
        east_score = self._compute_east_score()

        # 8. Compute Overall Time-to-Value (TTV) Stopwatch Metric
        ttv_metrics = self._compute_overall_ttv()

        # 9. Formulate Riskiest Habit Assumption Test (RAT)
        rat_assumption = self._formulate_rat_assumption(fogg_score, entropy_score, investment_score)

        # 10. Aggregate Overall Habit Health Score (0 - 100)
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
            east_score=east_score,
            ttv_metrics=ttv_metrics,
            rat_assumption=rat_assumption,
            hook_graph=self.graph,
            findings=findings,
            summary_verdict=summary,
        )

    def _compute_east_score(self) -> EASTScore:
        triggers_with_east = [t.east_score for t in self.graph.triggers if t.east_score]
        if not triggers_with_east:
            return EASTScore(easy=0.20, attractive=0.20, social=0.10, timely=0.20, overall=0.18)
        avg_easy = sum(s.easy for s in triggers_with_east) / len(triggers_with_east)
        avg_attractive = sum(s.attractive for s in triggers_with_east) / len(triggers_with_east)
        avg_social = sum(s.social for s in triggers_with_east) / len(triggers_with_east)
        avg_timely = sum(s.timely for s in triggers_with_east) / len(triggers_with_east)
        avg_overall = (avg_easy + avg_attractive + avg_social + avg_timely) / 4.0
        return EASTScore(easy=avg_easy, attractive=avg_attractive, social=avg_social, timely=avg_timely, overall=avg_overall)

    def _compute_overall_ttv(self) -> TTVMetrics:
        actions_with_ttv = [a.ttv_metrics for a in self.graph.actions if a.ttv_metrics]
        if not actions_with_ttv:
            return TTVMetrics(estimated_ttv_seconds=20, rating="Instant (<25s)", friction_bottleneck="None")
        worst = max(actions_with_ttv, key=lambda m: m.estimated_ttv_seconds)
        return worst

    def _formulate_rat_assumption(self, fogg_score: int, entropy_score: int, investment_score: int) -> RATAssumption:
        if not self.graph.triggers:
            return RATAssumption(
                hypothesis="Users will reflexively remember to return to the product without external trigger scaffolding.",
                risk_level="Critical",
                test_method="Survey churned users on Day 2 to measure brand recall latency.",
                success_metric=">= 25% unprompted return rate without push/email cues."
            )
        if fogg_score < 40:
            return RATAssumption(
                hypothesis="Users possess sufficient initial motivation to complete a high-friction onboarding setup before experiencing value.",
                risk_level="Critical",
                test_method="A/B test a 1-step progressive onboarding against the existing setup flow.",
                success_metric=">= 50% increase in Day-0 activation rate."
            )
        if entropy_score < 50:
            return RATAssumption(
                hypothesis="Finite rewards (static badges/points) will maintain dopamine engagement past Day 14.",
                risk_level="High",
                test_method="Cohort retention comparison at Day 7 vs Day 30.",
                success_metric="D30 retention decay rate <= 40% of D7 cohort baseline."
            )
        if investment_score < 40:
            return RATAssumption(
                hypothesis="Users will form an enduring habit despite zero accumulated switching costs or stored data.",
                risk_level="High",
                test_method="Introduce post-reward auto-bookmarking and measure 30-day retention delta.",
                success_metric=">= 15% increase in Day-30 retention for users who store value."
            )
        return RATAssumption(
            hypothesis="Habit Devotees will reach the daily engagement threshold and form a self-sustaining basal ganglia routine.",
            risk_level="Medium",
            test_method="Cohort Habit Testing (Identify top 5% users and codify their habit path).",
            success_metric="Devotee cohort represents >= 5% of active user base."
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

        # Check Time-to-Value (TTV) Stopwatch metric
        worst_ttv = max((a.ttv_metrics.estimated_ttv_seconds for a in self.graph.actions if a.ttv_metrics), default=20)
        if worst_ttv > 90:
            findings.append(Finding(
                control_id="HOOK-ACT-04",
                phase="action",
                title="Time-to-Value (TTV) Friction Alert",
                verdict=FindingVerdict.FAIL,
                severity=FindingSeverity.HIGH,
                observation=f"Estimated Time-to-Value is ~{worst_ttv}s (Cognitive Exhaustion threshold exceeded).",
                evidence="Setup friction exceeds 90-second activation budget (Corey Haines Stopwatch model).",
                recommendation="Convert into an Endowed Progress progressive wizard: pre-fill defaults and show instant value.",
            ))

        # System 1 vs System 2 Cognitive Load Classifier (rastian/behavioral-design-skills)
        if max_inputs > 5 or has_auth_gate:
            findings.append(Finding(
                control_id="HOOK-ACT-05",
                phase="action",
                title="System 2 Deliberative Cognitive Overload",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.MEDIUM,
                observation="Action path forces slow, deliberative System 2 decision-making during initial onboarding.",
                evidence="High input complexity or upfront account creation interrupts subconscious, intuitive System 1 momentum.",
                recommendation="Shift to System 1 default architecture: provide 1-click presets and smart pre-filled configurations (Kahneman Nudge framework).",
            ))
        else:
            findings.append(Finding(
                control_id="HOOK-ACT-05",
                phase="action",
                title="System 1 Intuitive Flow Activated",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Action leverages System 1 fast heuristics without forcing painful deliberative pauses.",
                evidence=f"Concise input path ({max_inputs} fields) enables seamless subconscious execution.",
                recommendation="Preserve low-cognitive-load defaults as product surface area expands.",
            ))

        # Hesitation Sitter Audit (ai-marketing-claude / zubair-trabzada)
        if has_paywall or has_auth_gate:
            findings.append(Finding(
                control_id="HOOK-ACT-06",
                phase="action",
                title="Hesitation Barrier at High-Friction Gate",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.LOW,
                observation="Friction gate (auth or payment) requires reassurance to overcome user hesitation.",
                evidence="Authentication or checkout barrier detected in primary onboarding loop.",
                recommendation="Place social proof ('Joined by 10,000+ teams') and security reassurance directly adjacent to CTA button.",
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
        has_extrinsic_only = any(r.is_extrinsic_only for r in self.graph.rewards)

        entropy_score = 40
        if has_tribe:
            entropy_score += 25
        if has_hunt:
            entropy_score += 25
        if has_self:
            entropy_score += 15
        if has_infinite:
            entropy_score += 15
        if has_extrinsic_only:
            entropy_score -= 10

        entropy_score = max(10, min(100, entropy_score))

        if has_extrinsic_only:
            findings.append(Finding(
                control_id="HOOK-REW-03",
                phase="reward",
                title="Overjustification Effect Risk (Superficial Gamification)",
                verdict=FindingVerdict.WARN,
                severity=FindingSeverity.MEDIUM,
                observation="Extrinsic points/tokens detected without intrinsic mastery or social validation.",
                evidence="Points-only reward structure risks crowding out user's authentic internal emotional itch.",
                recommendation="Shift gamification from extrinsic points to intrinsic competence (Wondelai Mastery model).",
            ))

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

        # Octalysis White Hat vs Black Hat Reward Balance (alexander-kastil/skills-collection)
        if has_self or has_tribe:
            findings.append(Finding(
                control_id="HOOK-REW-05",
                phase="reward",
                title="White Hat Empowerment Reward Dynamics",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Rewards promote positive user agency, competence (Self), and community belonging (Tribe).",
                evidence="Empowerment and social validation mechanisms detected rather than predatory loss addiction.",
                recommendation="Maintain focus on user flourishing; avoid dark scarcity or anxiety-driven countdown timers.",
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
                recommendation="Connect stored value to future triggers (e.g. teammate comments on saved doc -> push notification).",
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

        # Commitment & Loss-Aversion Device Check (HKTITAN/duolingo)
        has_commitment = any(inv.stored_value_type in (StoredValueType.DATA, StoredValueType.REPUTATION) for inv in self.graph.investments)
        if has_commitment:
            findings.append(Finding(
                control_id="HOOK-INV-03",
                phase="investment",
                title="Commitment & Loss-Aversion Anchoring",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Stored value establishes psychological switching costs and loss aversion (Duolingo commitment model).",
                evidence="User investment creates personal equity that users are reluctant to forfeit.",
                recommendation="Provide streak freezes, milestone recaps, or progress wagers to reinforce user commitment.",
            ))

        # Autonomy & Emergency Exit Check (mastepanoski/claude-skills / NN/g #3)
        findings.append(Finding(
            control_id="HOOK-INV-04",
            phase="investment",
            title="User Autonomy & Data Portability",
            verdict=FindingVerdict.PASS,
            severity=FindingSeverity.INFO,
            observation="Invested assets remain under user ownership (Nielsen Norman Group Heuristic #3: User Control & Freedom).",
            evidence="No proprietary data-hostage sludge detected in investment mechanics.",
            recommendation="Guarantee 1-click JSON/CSV export and reversible configurations to maximize user trust.",
        ))

        # Macro-Loop Bridging (aakashg/pm-claude-skills)
        if primes_next or any(inv.stored_value_type == StoredValueType.CONTENT for inv in self.graph.investments):
            findings.append(Finding(
                control_id="HOOK-MACRO-01",
                phase="investment",
                title="Macro Product-Led Growth (PLG) Loop Bridged",
                verdict=FindingVerdict.PASS,
                severity=FindingSeverity.INFO,
                observation="Micro-Hook habit loop bridges to macro viral distribution (Aakash Growth Loop model).",
                evidence="Stored user content or collaboration triggers invite loops with potential K-factor > 0.",
                recommendation="Amplify public share links, shared workspaces, and team invitation mechanics.",
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
