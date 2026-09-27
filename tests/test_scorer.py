"""
Unit tests for HabitScorer.
"""

import unittest
from hook_engine.core.models import (
    HookGraph,
    HookTrigger,
    HookAction,
    HookReward,
    HookInvestment,
    TriggerType,
    RewardType,
    StoredValueType,
    FoggLever,
    FindingVerdict,
    ManipulationQuadrant,
)
from hook_engine.core.scorer import HabitScorer


class TestHabitScorer(unittest.TestCase):

    def test_ideal_habit_forming_product(self):
        graph = HookGraph(project_name="HabitHero")
        graph.triggers.append(HookTrigger(
            id="t1", name="Push Trigger", trigger_type=TriggerType.OWNED,
            description="Push prompt", is_recurring=True
        ))
        graph.actions.append(HookAction(
            id="a1", name="Quick Log", description="1-tap log",
            input_fields_count=2, steps_count=1
        ))
        graph.rewards.append(HookReward(
            id="r1", name="Social Tribe", reward_type=RewardType.TRIBE,
            is_infinite_variability=True
        ))
        graph.investments.append(HookInvestment(
            id="i1", name="User Content", stored_value_type=StoredValueType.CONTENT,
            description="Stored post", loads_next_trigger=True
        ))

        scorer = HabitScorer(graph)
        bundle = scorer.score()

        self.assertGreaterEqual(bundle.overall_habit_health_score, 75)
        self.assertTrue(bundle.habit_zone.in_habit_zone)
        self.assertEqual(bundle.manipulation_matrix_quadrant, ManipulationQuadrant.FACILITATOR)

        # Assert EAST, TTV, and RAT additions
        self.assertIsNotNone(bundle.east_score)
        self.assertIsNotNone(bundle.ttv_metrics)
        self.assertIsNotNone(bundle.rat_assumption)
        self.assertIn("Habit Devotees", bundle.rat_assumption.hypothesis)

    def test_high_friction_product_penalties(self):
        graph = HookGraph(project_name="FrictionHeavy")
        # 10 input fields and mandatory paywall
        graph.actions.append(HookAction(
            id="a1", name="Heavy Form", description="10 fields",
            input_fields_count=10, requires_payment=True, requires_auth_wall=True,
            fogg_friction_levers=[FoggLever.PHYSICAL_EFFORT, FoggLever.TIME, FoggLever.MONEY]
        ))
        # Zero triggers, zero rewards, zero investments

        scorer = HabitScorer(graph)
        bundle = scorer.score()

        self.assertLess(bundle.overall_habit_health_score, 50)
        self.assertFalse(bundle.habit_zone.in_habit_zone)

        # Check that critical findings were emitted
        fail_findings = [f for f in bundle.findings if f.verdict == FindingVerdict.FAIL]
        self.assertGreaterEqual(len(fail_findings), 2)


if __name__ == "__main__":
    unittest.main()
