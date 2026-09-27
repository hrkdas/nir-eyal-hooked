"""
Unit tests for Cohort Simulation, Lifecycle Journeys, and Synthetic Churn Interviews.
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
)
from hook_engine.simulation.cohorts import get_default_cohorts, UserArchetype
from hook_engine.simulation.lifecycle import LifecycleSimulator
from hook_engine.simulation.interviewer import SyntheticInterviewer


class TestSimulationEngine(unittest.TestCase):

    def setUp(self):
        self.graph = HookGraph(project_name="TestApp")
        self.graph.triggers.append(HookTrigger(
            id="t1", name="Push", trigger_type=TriggerType.OWNED, is_recurring=True, description="Push"
        ))
        self.graph.actions.append(HookAction(
            id="a1", name="Action", description="Action", input_fields_count=2
        ))
        self.graph.rewards.append(HookReward(
            id="r1", name="Reward", reward_type=RewardType.TRIBE, is_infinite_variability=True
        ))
        self.graph.investments.append(HookInvestment(
            id="i1", name="Investment", stored_value_type=StoredValueType.DATA,
            loads_next_trigger=True, description="Saved Data"
        ))

    def test_default_cohorts_initialization(self):
        cohorts = get_default_cohorts(population_per_cohort=50)
        self.assertEqual(len(cohorts), 5)
        total_pop = sum(c.population_size for c in cohorts)
        self.assertEqual(total_pop, 250)

    def test_lifecycle_simulation_execution(self):
        cohorts = get_default_cohorts(population_per_cohort=20)
        sim = LifecycleSimulator(self.graph, cohorts=cohorts)
        res = sim.run()

        self.assertEqual(res.total_initial_users, 100)
        self.assertGreater(res.total_day30_retained, 0)
        self.assertLessEqual(res.total_day30_retained, res.total_initial_users)
        self.assertTrue(len(res.round_timeline) == 5 * len(cohorts))

    def test_synthetic_interviewer_5_whys(self):
        interviewer = SyntheticInterviewer(self.graph)
        cohorts = get_default_cohorts()
        novice = next(c for c in cohorts if c.archetype == UserArchetype.NOVICE)

        transcript = interviewer.interview_cohort(novice, dropoff_round="Day 0")
        self.assertEqual(len(transcript.steps), 5)
        self.assertEqual(transcript.steps[0].why_level, 1)
        self.assertEqual(transcript.steps[4].why_level, 5)
        self.assertIn("ROOT CAUSE", transcript.steps[4].behavioral_diagnosis)
        self.assertTrue(len(transcript.actionable_remediation) > 10)


if __name__ == "__main__":
    unittest.main()
