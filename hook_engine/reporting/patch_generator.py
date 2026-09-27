"""
Automated Code & Copy Remediation Patch Generator.
Produces actionable git-style unified diffs to fix identified Hook Model weaknesses:
UI form simplification, trigger copy rewrites, and stored value hook insertion.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from ..core.models import AuditBundle, Finding, FindingVerdict


@dataclass
class RemediationPatch:
    title: str
    target_file: str
    phase: str
    rationale: str
    diff_content: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "target_file": self.target_file,
            "phase": self.phase,
            "rationale": self.rationale,
            "diff_content": self.diff_content,
        }


class PatchGenerator:
    """
    Analyzes an AuditBundle's findings and generates concrete, ready-to-apply diffs.
    """

    def __init__(self, bundle: AuditBundle):
        self.bundle = bundle

    def generate_patches(self) -> List[RemediationPatch]:
        patches: List[RemediationPatch] = []

        for finding in self.bundle.findings:
            if finding.verdict in (FindingVerdict.FAIL, FindingVerdict.WARN):
                patch = self._create_patch_for_finding(finding)
                if patch:
                    patches.append(patch)

        return patches

    def _create_patch_for_finding(self, finding: Finding) -> Optional[RemediationPatch]:
        # Case 1: Form Friction (HOOK-ACT-01)
        if finding.control_id == "HOOK-ACT-01":
            target = finding.code_patch_target or "src/components/OnboardingForm.tsx"
            return RemediationPatch(
                title="Progressive Disclosure: Defer non-critical fields until post-activation",
                target_file=target,
                phase="action",
                rationale="Cuts input fields from 7+ down to 2 essential fields, elevating Fogg Ability above the activation threshold.",
                diff_content=f"""--- a/{target}
+++ b/{target}
@@ -10,12 +10,6 @@ export function OnboardingForm() {{
   return (
     <form onSubmit={{handleSubmit}}>
       <input name="email" type="email" placeholder="Work Email" required />
       <input name="password" type="password" placeholder="Password" required />
-      <input name="company" placeholder="Company Name" />
-      <input name="role" placeholder="Your Title" />
-      <input name="teamSize" type="number" placeholder="Team Size" />
-      <input name="phoneNumber" type="tel" placeholder="Phone Number" />
-      <input name="referralCode" placeholder="Referral Code" />
+      {{/* Deferred to Settings after initial Aha! moment */}}
       <button type="submit">Get Started Free (No Card Required)</button>
     </form>
   );
"""
            )

        # Case 2: Missing Owned Trigger (HOOK-TRIG-01)
        if finding.control_id in ("HOOK-TRIG-01", "HOOK-TRIG-02"):
            target = finding.code_patch_target or "src/jobs/reengagement.ts"
            return RemediationPatch(
                title="Context-Aware Owned Trigger: Wire 24h re-engagement notification",
                target_file=target,
                phase="trigger",
                rationale="Prevents Day-1 churn by dispatching an owned notification tied to teammate activity.",
                diff_content=f"""--- a/{target}
+++ b/{target}
@@ -0,0 +1,15 @@
+import {{ sendNotification }} from '../services/notifications';
+
+/**
+ * Nir Eyal Hook Model: Owned External Trigger
+ * Connects external prompt to teammate action, soothing the user's FOMO/Anxiety.
+ */
+export async function queueDayOneHookTrigger(userId: string, teammateName: string) {{
+  await sendNotification({{
+    userId,
+    channel: 'push',
+    title: `${{teammateName}} reviewed your project`,
+    body: 'Tap to see their comments and keep momentum going.',
+    deliverAfterHours: 24,
+  }});
+}}
"""
            )

        # Case 3: Missing Stored Value (HOOK-INV-01)
        if finding.control_id == "HOOK-INV-01":
            target = finding.code_patch_target or "src/handlers/actionComplete.ts"
            return RemediationPatch(
                title="Stored Value Hook: Auto-bookmark & store user effort after reward",
                target_file=target,
                phase="investment",
                rationale="Leverages the IKEA effect by immediately storing user data, increasing switching costs and priming next trigger.",
                diff_content=f"""--- a/{target}
+++ b/{target}
@@ -18,6 +18,12 @@ export async function handleActionComplete(event: ActionEvent) {{
   // Step 3: Deliver Variable Reward
   await deliverVariableReward(event.userId, event.actionId);
   
+  // Step 4: Hook Model Stored Value Investment
+  // Auto-save user history and prime next trigger
+  await db.storedValue.create({{
+    data: {{ userId: event.userId, content: event.payload, primesNextTrigger: true }}
+  }});
+
   return {{ success: true }};
 }}
"""
            )

        # Case 4: Excessive Time-to-Value Friction (HOOK-ACT-04)
        if finding.control_id == "HOOK-ACT-04":
            target = finding.code_patch_target or "src/components/QuickStartWizard.tsx"
            return RemediationPatch(
                title="Endowed Progress Wizard: Pre-fill defaults & compress TTV under 15 seconds",
                target_file=target,
                phase="action",
                rationale="Leverages the Endowed Progress Effect (Nunes & Dreze) by giving users head-start progress (Step 2 of 3) and 1-click template selection to compress Time-to-Value.",
                diff_content=f"""--- a/{target}
+++ b/{target}
@@ -1,15 +1,24 @@
-export function SetupWizard() {{
-  // Slow multi-page questionnaire
-  return <ComplexSurvey onComplete={{save}} />;
+export function QuickStartWizard({{ onAhaMoment }}: {{ onAhaMoment: () => void }}) {{
+  // Endowed Progress: User starts at 66% completed with smart defaults pre-populated
+  return (
+    <div className="quickstart-container">
+      <div className="progress-banner" aria-label="Step 2 of 3 (66% completed)">
+        <span>Step 2 of 3: Fast-track template chosen</span>
+        <div className="progress-bar-fill" style={{{{ width: '66%' }}}} />
+      </div>
+      <h3>Explore with sample data ready</h3>
+      <button 
+        className="btn-primary-instant"
+        onClick={{() => onAhaMoment()}}
+      >
+        Launch Instant Sandbox (1-Click) &rarr;
+      </button>
+    </div>
+  );
 }}
"""
            )

        # Case 5: Overjustification Decay Risk (HOOK-REW-03)
        if finding.control_id == "HOOK-REW-03":
            target = finding.code_patch_target or "src/rewards/achievementHandler.ts"
            return RemediationPatch(
                title="Intrinsic Mastery Upgrade: Transform extrinsic points into milestone mastery",
                target_file=target,
                phase="reward",
                rationale="Protects against the Overjustification Effect by anchoring rewards to genuine competence feedback (Self) and peer appreciation (Tribe) rather than ephemeral point tickers.",
                diff_content=f"""--- a/{target}
+++ b/{target}
@@ -5,7 +5,13 @@ export function awardActivity(userId: string) {{
-  // Pure extrinsic point increment: high satiation & churn risk
-  pointsEngine.increment(userId, 10);
+  // Hook Model Mastery Loop: Pair achievement with intrinsic competence feedback
+  const masteryTier = calculateSkillMilestone(userId);
+  notifications.send({{
+    userId,
+    title: `Mastery Unlocked: Level ${{masteryTier.name}}`,
+    body: `You automated your first workflow. Your team has already saved 2.4 hours.`,
+    shareableArtifactUrl: `/certificates/${{masteryTier.id}}`
+  }});
 }}
"""
            )

        return None
