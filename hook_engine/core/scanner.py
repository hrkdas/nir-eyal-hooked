"""
Deterministic Codebase, PRD, and User-Flow Scanner.
Analyzes files and project structures to identify Hook Model components:
Triggers, Actions, Rewards, Investments, and Behavioral Friction.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

from .models import (
    HookGraph,
    HookTrigger,
    HookAction,
    HookReward,
    HookInvestment,
    TriggerType,
    InternalItch,
    FoggLever,
    RewardType,
    StoredValueType,
    PromptType,
    EASTScore,
    TTVMetrics,
)


class CodebaseScanner:
    """
    Scans a filesystem directory, code repository, or documentation file
    to extract Hook Model entities and friction indicators.
    """

    # Common directories to skip
    EXCLUDE_DIRS = {
        ".git", "node_modules", "dist", "build", ".next", ".cache",
        "vendor", "env", "venv", ".venv", "__pycache__", ".pytest_cache"
    }

    # Code file extensions to inspect
    CODE_EXTS = {
        ".ts", ".tsx", ".js", ".jsx", ".py", ".html", ".vue", ".svelte",
        ".go", ".rb", ".php", ".swift", ".dart", ".kt", ".java", ".md", ".json"
    }

    def __init__(self, target_path: str):
        self.target_path = Path(target_path).resolve()
        self.project_name = self.target_path.name if self.target_path.is_dir() else self.target_path.stem

    def scan(self) -> HookGraph:
        """Runs full deterministic scan across the target directory or file."""
        if not self.target_path.exists():
            raise FileNotFoundError(f"Target path does not exist: {self.target_path}")

        graph = HookGraph(project_name=self.project_name)

        if self.target_path.is_file():
            self._scan_single_file(self.target_path, graph)
        else:
            self._scan_directory(self.target_path, graph)

        # Check if the loop is structurally connected
        graph.loop_connected = bool(
            graph.triggers and graph.actions and graph.rewards and graph.investments
        )

        return graph

    def _scan_directory(self, root_dir: Path, graph: HookGraph):
        """Recursively scans files in directory."""
        for root, dirs, files in os.walk(root_dir):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.CODE_EXTS:
                    self._scan_single_file(file_path, graph)

    def _scan_single_file(self, file_path: Path, graph: HookGraph):
        """Scans an individual file with regex patterns for Hook elements."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        rel_path = str(file_path.relative_to(self.target_path)) if self.target_path.is_dir() else file_path.name

        self._detect_triggers(content, rel_path, graph)
        self._detect_actions(content, rel_path, graph)
        self._detect_rewards(content, rel_path, graph)
        self._detect_investments(content, rel_path, graph)

    def _detect_triggers(self, content: str, rel_path: str, graph: HookGraph):
        """Identifies owned, relationship, or earned external triggers in code."""
        lower = content.lower()

        # Push notifications
        push_patterns = [
            r"fcm|firebase|onesignal|web-push|pushnotification|apns|sendnotification",
            r"sendpush|push_alert|pushalert|pushtoken|push_token|send_push"
        ]
        for pat in push_patterns:
            if re.search(pat, lower):
                graph.triggers.append(HookTrigger(
                    id=f"trig-push-{len(graph.triggers)+1}",
                    name=f"Push Notification Hook ({Path(rel_path).name})",
                    trigger_type=TriggerType.OWNED,
                    channel="push_notification",
                    description="Automated push notification detected in worker or client handler",
                    source_reference=rel_path,
                    is_recurring=True,
                    prompt_type=PromptType.SIGNAL,
                    east_score=EASTScore(easy=0.85, attractive=0.75, social=0.60, timely=0.80, overall=0.75),
                ))
                break

        # Transactional / Marketing Emails
        email_patterns = [
            r"sendgrid|resend|postmark|nodemailer|ses|mailgun|send_email|sendemail|deliver_later"
        ]
        for pat in email_patterns:
            if re.search(pat, lower):
                graph.triggers.append(HookTrigger(
                    id=f"trig-email-{len(graph.triggers)+1}",
                    name=f"Email Trigger ({Path(rel_path).name})",
                    trigger_type=TriggerType.OWNED,
                    channel="email",
                    description="Email dispatch routine identified",
                    source_reference=rel_path,
                    is_recurring=True,
                    prompt_type=PromptType.FACILITATOR,
                    east_score=EASTScore(easy=0.60, attractive=0.65, social=0.50, timely=0.60, overall=0.59),
                ))
                break

        # Cron & Scheduled Prompts
        cron_patterns = [
            r"cron\.schedule|schedulejob|apscheduler|celery\.task|bullmq|setInterval|node-cron"
        ]
        for pat in cron_patterns:
            if re.search(pat, lower):
                graph.triggers.append(HookTrigger(
                    id=f"trig-sched-{len(graph.triggers)+1}",
                    name=f"Scheduled Trigger Prompt ({Path(rel_path).name})",
                    trigger_type=TriggerType.OWNED,
                    channel="scheduler_cron",
                    description="Time-based background trigger scheduler detected",
                    source_reference=rel_path,
                    is_recurring=True,
                    prompt_type=PromptType.FACILITATOR,
                    east_score=EASTScore(easy=0.50, attractive=0.40, social=0.30, timely=0.45, overall=0.41),
                ))
                break

        # Social / Referral Invites (Relationship triggers)
        invite_patterns = [
            r"referral_code|invite_friend|share_link|invitedby|referral_bonus"
        ]
        for pat in invite_patterns:
            if re.search(pat, lower):
                graph.triggers.append(HookTrigger(
                    id=f"trig-rel-{len(graph.triggers)+1}",
                    name=f"Referral / Social Invite ({Path(rel_path).name})",
                    trigger_type=TriggerType.RELATIONSHIP,
                    channel="social_invite",
                    description="Relationship trigger mechanic detected",
                    source_reference=rel_path,
                    prompt_type=PromptType.SPARK,
                    east_score=EASTScore(easy=0.70, attractive=0.85, social=0.95, timely=0.70, overall=0.80),
                ))
                break

    def _detect_actions(self, content: str, rel_path: str, graph: HookGraph):
        """Measures UI action friction, form field density, and auth walls."""
        lower = content.lower()

        # Count input fields in UI forms
        input_matches = re.findall(r"<input|<textarea|<TextField|<Select|<Field", content, re.IGNORECASE)
        inputs_count = len(input_matches)

        # Check for authentication walls
        has_auth_gate = bool(re.search(r"requireauth|withauth|protectedroute|loginrequired|authguard", lower))

        # Check for credit card upfront
        has_payment_wall = bool(re.search(r"stripe|cardelement|checkoutform|subscription_required|billing_required", lower))

        if inputs_count > 0 or has_auth_gate or has_payment_wall:
            levers = []
            if inputs_count >= 5:
                levers.append(FoggLever.PHYSICAL_EFFORT)
                levers.append(FoggLever.TIME)
            if inputs_count >= 8:
                levers.append(FoggLever.MENTAL_EFFORT)
            if has_payment_wall:
                levers.append(FoggLever.MONEY)
            if has_auth_gate:
                levers.append(FoggLever.ROUTINE_DISRUPTION)

            # Calculate Time-to-Value (TTV) Stopwatch metrics
            ttv_secs = (inputs_count * 12) + (35 if has_auth_gate else 0) + (60 if has_payment_wall else 0) + 10
            if ttv_secs <= 25:
                ttv_rating = "Instant (<25s)"
            elif ttv_secs <= 45:
                ttv_rating = "Optimal (<45s)"
            elif ttv_secs <= 90:
                ttv_rating = "Friction Warning (45-90s)"
            else:
                ttv_rating = "Cognitive Exhaustion (>90s)"

            bottleneck = "Form Inputs" if inputs_count >= 5 else ("Payment Wall" if has_payment_wall else ("Auth Wall" if has_auth_gate else "None"))
            ttv_obj = TTVMetrics(estimated_ttv_seconds=ttv_secs, rating=ttv_rating, friction_bottleneck=bottleneck)

            action_name = f"User Action Flow in {Path(rel_path).name}"
            graph.actions.append(HookAction(
                id=f"act-{len(graph.actions)+1}",
                name=action_name,
                description=f"Action interface with {inputs_count} input fields detected (TTV: ~{ttv_secs}s)",
                input_fields_count=inputs_count,
                steps_count=max(1, inputs_count // 3),
                requires_auth_wall=has_auth_gate,
                requires_payment=has_payment_wall,
                fogg_friction_levers=levers,
                source_reference=rel_path,
                ttv_metrics=ttv_obj,
            ))

    def _detect_rewards(self, content: str, rel_path: str, graph: HookGraph):
        """Identifies rewards of Tribe, Hunt, or Self."""
        lower = content.lower()

        # Rewards of the Tribe (Social proof, likes, upvotes, comments, leaderboards)
        if re.search(r"like_button|upvote|thumbsup|comment_list|leaderboard|social_feed|reactions", lower):
            graph.rewards.append(HookReward(
                id=f"rew-tribe-{len(graph.rewards)+1}",
                name=f"Tribe Reward: Social Validation ({Path(rel_path).name})",
                reward_type=RewardType.TRIBE,
                is_variable=True,
                is_infinite_variability=True,
                description="Social validation, reactions, or community status mechanic",
                source_reference=rel_path,
            ))

        # Rewards of the Hunt (Infinite content scroll, search, discovery feed, deals)
        if re.search(r"infinitescroll|useinfinitequery|fetch_next_page|product_deals|discovery_feed|recommendations", lower):
            graph.rewards.append(HookReward(
                id=f"rew-hunt-{len(graph.rewards)+1}",
                name=f"Hunt Reward: Variable Discovery Feed ({Path(rel_path).name})",
                reward_type=RewardType.HUNT,
                is_variable=True,
                is_infinite_variability=True,
                description="Novel information / discovery feed with high variability",
                source_reference=rel_path,
            ))

        # Rewards of the Self (Streaks, badges, leveling up, task completion, inbox zero)
        if re.search(r"streak_count|badge_unlocked|level_up|task_completed|progress_bar|inbox_zero|achievement", lower):
            is_infinite = bool(re.search(r"procedural|dynamic_levels", lower))
            graph.rewards.append(HookReward(
                id=f"rew-self-{len(graph.rewards)+1}",
                name=f"Self Reward: Mastery / Progress ({Path(rel_path).name})",
                reward_type=RewardType.SELF,
                is_variable=True,
                is_infinite_variability=is_infinite,
                description="Progress, streak, or personal mastery feedback",
                source_reference=rel_path,
            ))

        # Extrinsic Only Rewards (Points, Coins, Loyalty Tokens - Overjustification Risk)
        if re.search(r"virtual_currency|loyalty_points|reward_coins|daily_tokens|gamification_points", lower):
            graph.rewards.append(HookReward(
                id=f"rew-ext-{len(graph.rewards)+1}",
                name=f"Extrinsic Points Reward ({Path(rel_path).name})",
                reward_type=RewardType.HUNT,
                is_variable=False,
                is_infinite_variability=False,
                is_extrinsic_only=True,
                overjustification_risk="high",
                description="Extrinsic points/tokens; risk of crowding out intrinsic motivation",
                source_reference=rel_path,
            ))

    def _detect_investments(self, content: str, rel_path: str, graph: HookGraph):
        """Identifies stored value mechanisms (Data, Content, Followers, Reputation, Skill)."""
        lower = content.lower()

        # Stored Value: Content (Playlists, articles, notes, projects)
        if re.search(r"playlist|create_document|new_post|saved_note|project_create|upload_media", lower):
            graph.investments.append(HookInvestment(
                id=f"inv-content-{len(graph.investments)+1}",
                name=f"Stored Value: User Content Creation ({Path(rel_path).name})",
                stored_value_type=StoredValueType.CONTENT,
                description="User creates content that increases switching costs (IKEA effect)",
                loads_next_trigger=True,
                effort_tier="medium",
                source_reference=rel_path,
            ))

        # Stored Value: Data (Preferences, history, bookmarks, tags)
        if re.search(r"bookmark|favorite|saved_item|user_preferences|watch_history|tag_list", lower):
            graph.investments.append(HookInvestment(
                id=f"inv-data-{len(graph.investments)+1}",
                name=f"Stored Value: Personal Data & Bookmarks ({Path(rel_path).name})",
                stored_value_type=StoredValueType.DATA,
                description="User stores personal data or favorites, tailoring the experience",
                loads_next_trigger=True,
                effort_tier="micro",
                source_reference=rel_path,
            ))

        # Stored Value: Followers (Social Graph)
        if re.search(r"follow_user|subscribe_channel|add_friend|sync_contacts|team_members", lower):
            graph.investments.append(HookInvestment(
                id=f"inv-follow-{len(graph.investments)+1}",
                name=f"Stored Value: Social Graph Curation ({Path(rel_path).name})",
                stored_value_type=StoredValueType.FOLLOWERS,
                description="Building follower graph; primes future relationship triggers",
                loads_next_trigger=True,
                effort_tier="micro",
                source_reference=rel_path,
            ))

        # Stored Value: Reputation
        if re.search(r"user_rating|karma_score|seller_score|reputation_points", lower):
            graph.investments.append(HookInvestment(
                id=f"inv-rep-{len(graph.investments)+1}",
                name=f"Stored Value: Reputation & Karma ({Path(rel_path).name})",
                stored_value_type=StoredValueType.REPUTATION,
                description="Reputational lock-in; user will not abandon accumulated standing",
                loads_next_trigger=False,
                effort_tier="medium",
                source_reference=rel_path,
            ))
