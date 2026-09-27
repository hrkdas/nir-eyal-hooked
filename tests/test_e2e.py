"""
End-to-End (E2E) Integration Tests for HookEngine.
Simulates a real codebase audit using the CLI runner.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from hook_engine.cli import main


class TestHookEngineE2E(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app_dir = Path(self.test_dir) / "MockSaaSApp"
        self.app_dir.mkdir()

        # 1. External Trigger (Push Worker)
        (self.app_dir / "worker.ts").write_text("""
        import admin from 'firebase-admin';
        export async function sendPushAlert(token: string) {
            await admin.messaging().send({ token, notification: { body: 'Teammate shared a file' } });
        }
        """)

        # 2. Action (Onboarding Form)
        (self.app_dir / "Onboarding.tsx").write_text("""
        export function Onboarding() {
            return (
                <form>
                    <input name="email" type="email" />
                    <input name="password" type="password" />
                    <input name="teamName" />
                    <button type="submit">Join</button>
                </form>
            );
        }
        """)

        # 3. Variable Reward (Tribe Social Feed)
        (self.app_dir / "Feed.tsx").write_text("""
        export function ActivityFeed() {
            return (
                <div>
                    <button className="like_button">Clap</button>
                    <div className="infinitescroll">Feed Items</div>
                </div>
            );
        }
        """)

        # 4. Investment (Stored Value Content & Data)
        (self.app_dir / "Workspace.ts").write_text("""
        export async function saveWorkspaceData(userId: string) {
            await db.document.create_document({ title: 'My Note' });
            await db.bookmark.add_to_bookmark({ docId: 123 });
        }
        """)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_full_cli_audit_flow(self):
        json_out = str(Path(self.test_dir) / "bundle.json")
        html_out = str(Path(self.test_dir) / "report.html")

        # Run CLI audit command
        exit_code = main(["audit", str(self.app_dir), "--json", json_out, "--html", html_out, "--diff"])
        self.assertEqual(exit_code, 0)

        # Verify JSON artifact
        json_path = Path(json_out)
        self.assertTrue(json_path.exists())
        data = json.loads(json_path.read_text(encoding="utf-8"))

        self.assertEqual(data["project_name"], "MockSaaSApp")
        self.assertGreaterEqual(data["overall_habit_health_score"], 60)
        self.assertTrue(data["habit_zone"]["in_habit_zone"])
        self.assertEqual(data["manipulation_matrix_quadrant"], "facilitator")

        # Verify HTML artifact
        html_path = Path(html_out)
        self.assertTrue(html_path.exists())
        html_content = html_path.read_text(encoding="utf-8")
        self.assertIn("MockSaaSApp", html_content)
        self.assertIn("THE HABIT ZONE", html_content)
        self.assertIn("30-Day Retention Simulation", html_content)

    def test_cli_subcommands(self):
        # Test scan subcommand
        exit_code_scan = main(["scan", str(self.app_dir)])
        self.assertEqual(exit_code_scan, 0)

        # Test simulate subcommand
        exit_code_sim = main(["simulate", str(self.app_dir), "--users", "50"])
        self.assertEqual(exit_code_sim, 0)

        # Test diff subcommand
        exit_code_diff = main(["diff", str(self.app_dir)])
        self.assertEqual(exit_code_diff, 0)

    def test_cli_audit_with_telemetry(self):
        tel_file = Path(self.test_dir) / "mixpanel_export.json"
        tel_file.write_text(json.dumps({
            "Day 0": 100.0,
            "Day 1": 45.0,
            "Day 3": 22.0,
            "Day 7": 14.0,
            "Day 30": 8.5
        }))

        json_out = str(Path(self.test_dir) / "bundle_with_telemetry.json")
        exit_code = main([
            "audit", str(self.app_dir),
            "--telemetry", str(tel_file),
            "--json", json_out
        ])
        self.assertEqual(exit_code, 0)

        data = json.loads(Path(json_out).read_text(encoding="utf-8"))
        self.assertIn("empirical_comparison", data["simulation_results"])
        rounds = data["simulation_results"]["empirical_comparison"]["rounds"]
        self.assertEqual(len(rounds), 5)
        d1 = next(r for r in rounds if r["round_id"] == "Day 1")
        self.assertEqual(d1["empirical_retention_pct"], 45.0)


if __name__ == "__main__":
    unittest.main()
