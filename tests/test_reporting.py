"""
Unit tests for Reporting, HTML Generation, and Patch Generation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from hook_engine.core.models import (
    HookGraph,
    HookTrigger,
    HookAction,
    HookReward,
    HookInvestment,
    TriggerType,
    RewardType,
    StoredValueType,
    FindingVerdict,
    FindingSeverity,
    Finding,
)
from hook_engine.reporting.builder import AuditReportBuilder
from hook_engine.reporting.html_generator import HTMLReportGenerator
from hook_engine.reporting.patch_generator import PatchGenerator


class TestReportingEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.graph = HookGraph(project_name="ReportTestApp")
        self.graph.triggers.append(HookTrigger(
            id="t1", name="Push Hook", trigger_type=TriggerType.OWNED, is_recurring=True, description="Push"
        ))
        self.graph.actions.append(HookAction(
            id="a1", name="Form Action", description="Form", input_fields_count=8
        ))
        self.graph.rewards.append(HookReward(
            id="r1", name="Feed", reward_type=RewardType.HUNT, is_infinite_variability=True
        ))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_audit_report_builder_and_json(self):
        builder = AuditReportBuilder(self.graph)
        bundle = builder.build(run_simulation=True, run_interviews=True)

        self.assertIsNotNone(bundle.timestamp)
        self.assertIn("cohort_summaries", bundle.simulation_results)
        self.assertIn("churn_interviews", bundle.simulation_results)

        json_path = Path(self.test_dir) / "bundle.json"
        saved_file = builder.export_json(bundle, str(json_path))
        self.assertTrue(Path(saved_file).exists())
        self.assertGreater(Path(saved_file).stat().st_size, 100)

    def test_html_generator_renders_clean_page(self):
        builder = AuditReportBuilder(self.graph)
        bundle = builder.build(run_simulation=True, run_interviews=True)

        generator = HTMLReportGenerator(bundle)
        html_out = Path(self.test_dir) / "report.html"
        generated_path = generator.generate(str(html_out))

        self.assertTrue(Path(generated_path).exists())
        content = Path(generated_path).read_text(encoding="utf-8")
        self.assertIn("Hook Model Behavioral Audit", content)
        self.assertIn("ReportTestApp", content)
        self.assertIn("THE HABIT ZONE", content)
        self.assertIn("Synthetic \"5 Whys\" Churn Interrogations", content)

    def test_patch_generator_creates_diffs(self):
        builder = AuditReportBuilder(self.graph)
        bundle = builder.build(run_simulation=False)

        patch_gen = PatchGenerator(bundle)
        patches = patch_gen.generate_patches()

        self.assertGreaterEqual(len(patches), 1)
        # Should create a form simplification diff for 8 input fields
        form_patch = next((p for p in patches if p.phase == "action"), None)
        self.assertIsNotNone(form_patch)
        self.assertIn("--- a/", form_patch.diff_content)
        self.assertIn("+++ b/", form_patch.diff_content)

    def test_html_generator_renders_east_ttv_and_rat(self):
        builder = AuditReportBuilder(self.graph)
        empirical_telemetry = {"Day 0": 100.0, "Day 1": 35.0, "Day 3": 18.0, "Day 7": 10.0, "Day 30": 5.0}
        bundle = builder.build(run_simulation=True, run_interviews=True, empirical_telemetry=empirical_telemetry)

        generator = HTMLReportGenerator(bundle)
        html_out = Path(self.test_dir) / "enriched_report.html"
        generated_path = generator.generate(str(html_out))

        self.assertTrue(Path(generated_path).exists())
        content = Path(generated_path).read_text(encoding="utf-8")
        self.assertIn("EAST Behavioral Framework Diagnostic", content)
        self.assertIn("Time-to-Value (TTV) Stopwatch", content)
        self.assertIn("Riskiest Habit Assumption Tests (RAT Matrix)", content)
        self.assertIn("Empirical Telemetry Calibration", content)

    def test_patch_generator_endowed_progress_and_mastery(self):
        finding_ttv = Finding(
            control_id="HOOK-ACT-04",
            phase="action",
            title="Time-to-Value Lag",
            verdict=FindingVerdict.FAIL,
            severity=FindingSeverity.HIGH,
            observation="TTV exceeds 45s",
            evidence="TTV stopwatch measured 65s",
            recommendation="Pre-fill defaults",
            code_patch_target="src/components/QuickStartWizard.tsx",
        )
        finding_gamification = Finding(
            control_id="HOOK-REW-03",
            phase="reward",
            title="Overjustification Risk",
            verdict=FindingVerdict.WARN,
            severity=FindingSeverity.MEDIUM,
            observation="Points only",
            evidence="Streak points without social loop",
            recommendation="Upgrade to intrinsic mastery",
            code_patch_target="src/rewards/achievementHandler.ts",
        )
        builder = AuditReportBuilder(self.graph)
        bundle = builder.build(run_simulation=False)
        bundle.findings.extend([finding_ttv, finding_gamification])

        patch_gen = PatchGenerator(bundle)
        patches = patch_gen.generate_patches()

        wizard_patch = next((p for p in patches if "Endowed Progress Wizard" in p.title), None)
        self.assertIsNotNone(wizard_patch)
        self.assertIn("QuickStartWizard", wizard_patch.diff_content)

        mastery_patch = next((p for p in patches if "Intrinsic Mastery Upgrade" in p.title), None)
        self.assertIsNotNone(mastery_patch)
        self.assertIn("masteryTier", mastery_patch.diff_content)


if __name__ == "__main__":
    unittest.main()

