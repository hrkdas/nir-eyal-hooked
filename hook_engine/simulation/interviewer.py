"""
Synthetic Churn Interviewer: Automated '5 Whys' Root-Cause Interrogation.
Simulates in-depth qualitative user interviews with dropped-out cohort personas
to uncover why the Hook loop broke down.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from .cohorts import UserCohort, UserArchetype
from ..core.models import HookGraph, InternalItch


@dataclass
class InterviewStep:
    why_level: int
    interviewer_question: str
    persona_response: str
    behavioral_diagnosis: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "why_level": self.why_level,
            "interviewer_question": self.interviewer_question,
            "persona_response": self.persona_response,
            "behavioral_diagnosis": self.behavioral_diagnosis,
        }


@dataclass
class ChurnInterviewTranscript:
    persona_name: str
    archetype: str
    dropoff_round: str
    root_internal_itch: str
    steps: List[InterviewStep] = field(default_factory=list)
    actionable_remediation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "persona_name": self.persona_name,
            "archetype": self.archetype,
            "dropoff_round": self.dropoff_round,
            "root_internal_itch": self.root_internal_itch,
            "steps": [s.to_dict() for s in self.steps],
            "actionable_remediation": self.actionable_remediation,
        }


class SyntheticInterviewer:
    """
    Conducts qualitative '5 Whys' root-cause interviews with simulated user personas.
    """

    def __init__(self, graph: HookGraph):
        self.graph = graph

    def interview_cohort(
        self, cohort: UserCohort, dropoff_round: str = "Day 0"
    ) -> ChurnInterviewTranscript:
        max_inputs = max((a.input_fields_count for a in self.graph.actions), default=0)
        worst_ttv = max((a.ttv_metrics.estimated_ttv_seconds for a in self.graph.actions if a.ttv_metrics), default=20)
        has_auth = any(a.requires_auth_wall for a in self.graph.actions)
        has_paywall = any(a.requires_payment for a in self.graph.actions)
        has_owned_trig = len(self.graph.triggers) > 0

        steps: List[InterviewStep] = []

        if dropoff_round == "Day 0":
            # Round 0: Onboarding friction
            steps.append(InterviewStep(
                why_level=1,
                interviewer_question=f"Hello {cohort.display_name}. Our telemetry shows you abandoned the application during initial onboarding. Why did you leave?",
                persona_response=f"I clicked the link expecting a quick solution, but was immediately confronted with a heavy setup flow.",
                behavioral_diagnosis="Initial Action Barrier (Fogg Ability Threshold Exceeded)"
            ))

            ttv_clause = f" (taking over ~{worst_ttv}s to reach value)" if worst_ttv > 45 else ""
            steps.append(InterviewStep(
                why_level=2,
                interviewer_question="Why did the setup flow feel so heavy?",
                persona_response=f"It demanded {max_inputs} input fields{ttv_clause} and forced account creation before I even saw what the tool actually did for me.",
                behavioral_diagnosis="Violation of Simplicity Sieve (Mental & Physical Effort Friction / TTV Delay)"
            ))

            steps.append(InterviewStep(
                why_level=3,
                interviewer_question="Why didn't the potential benefit justify taking 2 minutes to fill out those fields?",
                persona_response="Because I didn't have proof of value yet. Every modern app promises the world, but asking for my credentials upfront felt like homework.",
                behavioral_diagnosis="Asymmetric Investment Demand (Demanding Investment before Variable Reward)"
            ))

            steps.append(InterviewStep(
                why_level=4,
                interviewer_question="Why were you looking for an application like this in that exact moment?",
                persona_response="I was feeling overwhelmed and rushed. I needed an instant answer, not a new software project to manage.",
                behavioral_diagnosis="Misalignment with User Context & Cognitive Bandwidth"
            ))

            steps.append(InterviewStep(
                why_level=5,
                interviewer_question="What was the core underlying emotional itch you were trying to solve?",
                persona_response=f"Deep down, I felt acute {cohort.primary_internal_itch.value}. When your product added friction instead of soothing that discomfort, my subconscious reacted by closing the tab.",
                behavioral_diagnosis=f"ROOT CAUSE: Failure to relieve the internal trigger ({cohort.primary_internal_itch.value}) within 3 seconds."
            ))

            remediation = "Implement progressive disclosure: Remove registration gate, provide an instant sandbox/preview, and defer account creation until user attempts to save their work (Stored Value)."

        elif dropoff_round == "Day 1":
            # Round 1: Trigger failure
            steps.append(InterviewStep(
                why_level=1,
                interviewer_question="You had a promising initial session yesterday, but you never returned today. Why didn't you open the app?",
                persona_response="To be completely honest, I completely forgot it existed.",
                behavioral_diagnosis="Absence of Owned Trigger Cue"
            ))
            steps.append(InterviewStep(
                why_level=2,
                interviewer_question="Why did you forget so quickly after a successful first session?",
                persona_response="Nothing in my daily environment prompted me. I didn't get any notification or email reminding me of what I started.",
                behavioral_diagnosis="Broken External Trigger Scaffolding"
            ))
            steps.append(InterviewStep(
                why_level=3,
                interviewer_question="Why didn't an internal urge prompt you to return without a notification?",
                persona_response="A single session isn't enough to build a neural habit. My brain hasn't associated your app with my daily routine yet.",
                behavioral_diagnosis="Habit Formation Latency (Requires repeated external scaffolding)"
            ))
            steps.append(InterviewStep(
                why_level=4,
                interviewer_question="What would have brought you back into the product?",
                persona_response="If a teammate had commented on my item, or if I received a timely summary prompt when my problem flared up.",
                behavioral_diagnosis="Lack of Relationship or Context-Aware Owned Trigger"
            ))
            steps.append(InterviewStep(
                why_level=5,
                interviewer_question="What root emotional discomfort remained unaddressed?",
                persona_response=f"My recurring {cohort.primary_internal_itch.value}. Because your product wasn't top-of-mind, I defaulted to my old routine instead.",
                behavioral_diagnosis=f"ROOT CAUSE: Competitor / Status Quo mind monopoly won due to missing owned re-engagement trigger."
            ))
            remediation = "Establish timely owned triggers: Trigger an automated, value-packed digest email or contextual push notification within 24 hours of onboarding."

        else:
            # Default Day 3 / Day 7 satiation
            steps.append(InterviewStep(
                why_level=1,
                interviewer_question=f"You used the service for several days, but recently churned. Why did you stop?",
                persona_response="The initial novelty wore off. Checking the app started feeling like a chore rather than a delight.",
                behavioral_diagnosis="Dopamine Satiation & Finite Reward Decay"
            ))
            steps.append(InterviewStep(
                why_level=2,
                interviewer_question="Why did the experience feel like a chore?",
                persona_response="Every time I opened it, I saw the exact same static stats and predictable points. The mystery was gone.",
                behavioral_diagnosis="Lack of Infinite Variable Rewards (Tribe/Hunt)"
            ))
            steps.append(InterviewStep(
                why_level=3,
                interviewer_question="Why didn't your accumulated data or past work keep you invested?",
                persona_response="I didn't have much stored value in the app. Leaving didn't cost me anything.",
                behavioral_diagnosis="Low Switching Costs (Zero Stored Value Compounding)"
            ))
            steps.append(InterviewStep(
                why_level=4,
                interviewer_question="What would have kept you engaged over the long term?",
                persona_response="Seeing unexpected feedback from peers, or having my accumulated history unlock personalized superpowers.",
                behavioral_diagnosis="Absence of Social Proof (Tribe) and Stored Skill"
            ))
            steps.append(InterviewStep(
                why_level=5,
                interviewer_question="What is the root reason your habit failed to solidify?",
                persona_response="Without unpredictable variable rewards and compounding stored value, the loop died.",
                behavioral_diagnosis="ROOT CAUSE: Finite reward loop failed to transition into self-sustaining habit."
            ))
            remediation = "Introduce infinite variability (social reactions or algorithmic discovery) and show compounding stored value dashboards."

        return ChurnInterviewTranscript(
            persona_name=cohort.display_name,
            archetype=cohort.archetype.value,
            dropoff_round=dropoff_round,
            root_internal_itch=cohort.primary_internal_itch.value,
            steps=steps,
            actionable_remediation=remediation,
        )
