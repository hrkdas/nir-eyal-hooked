"""
Unit tests for CodebaseScanner.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from hook_engine.core.scanner import CodebaseScanner
from hook_engine.core.models import TriggerType, RewardType, StoredValueType


class TestCodebaseScanner(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.dir_path = Path(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_detect_push_notification_and_email(self):
        # Create a mock notification worker file
        worker_file = self.dir_path / "notificationWorker.ts"
        worker_file.write_text("""
        import admin from 'firebase-admin';
        import { sendgrid } from '@sendgrid/mail';

        export async function sendPushAlert(token: string, message: string) {
            await admin.messaging().send({ token, notification: { body: message } });
        }

        export async function sendEmailDigest(userEmail: string) {
            await sendgrid.send({ to: userEmail, from: 'team@app.com', subject: 'Your weekly update' });
        }
        """)

        scanner = CodebaseScanner(str(self.dir_path))
        graph = scanner.scan()

        self.assertTrue(len(graph.triggers) >= 2)
        trigger_types = [t.trigger_type for t in graph.triggers]
        self.assertIn(TriggerType.OWNED, trigger_types)

    def test_detect_form_action_friction(self):
        form_file = self.dir_path / "SignupForm.tsx"
        form_file.write_text("""
        export function SignupForm() {
            return (
                <form>
                    <input name="email" type="email" />
                    <input name="password" type="password" />
                    <input name="confirmPassword" type="password" />
                    <input name="firstName" />
                    <input name="lastName" />
                    <input name="company" />
                    <input name="role" />
                    <button type="submit">Sign Up</button>
                </form>
            );
        }
        """)

        scanner = CodebaseScanner(str(self.dir_path))
        graph = scanner.scan()

        self.assertEqual(len(graph.actions), 1)
        action = graph.actions[0]
        self.assertEqual(action.input_fields_count, 7)
        self.assertTrue(len(action.fogg_friction_levers) >= 2)

    def test_detect_variable_rewards_and_stored_value(self):
        feed_file = self.dir_path / "FeedAndLibrary.tsx"
        feed_file.write_text("""
        export function CommunityFeed() {
            return (
                <div>
                    <button className="like_button">Like</button>
                    <div className="infinitescroll">Feed Items</div>
                </div>
            );
        }

        export function UserLibrary() {
            return (
                <div>
                    <button onClick={create_document}>New Document</button>
                    <button onClick={add_to_bookmark}>Bookmark</button>
                </div>
            );
        }
        """)

        scanner = CodebaseScanner(str(self.dir_path))
        graph = scanner.scan()

        # Variable rewards: Tribe (like_button) and Hunt (infinitescroll)
        reward_types = [r.reward_type for r in graph.rewards]
        self.assertIn(RewardType.TRIBE, reward_types)
        self.assertIn(RewardType.HUNT, reward_types)

        # Stored value: Content (create_document) and Data (bookmark)
        stored_types = [i.stored_value_type for i in graph.investments]
        self.assertIn(StoredValueType.CONTENT, stored_types)
        self.assertIn(StoredValueType.DATA, stored_types)


if __name__ == "__main__":
    unittest.main()
