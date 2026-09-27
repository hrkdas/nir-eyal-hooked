"""
Generates a standalone, dependency-free interactive HTML dashboard
for displaying Nir Eyal Hook Model audit results.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from ..core.models import AuditBundle, FindingVerdict, FindingSeverity


class HTMLReportGenerator:
    """
    Renders an AuditBundle into a responsive, clean, self-contained HTML report.
    """

    def __init__(self, bundle: AuditBundle):
        self.bundle = bundle

    def generate(self, output_path: str) -> str:
        """Renders HTML dashboard to the specified destination path."""
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        html_content = self.render_html()
        out.write_text(html_content, encoding="utf-8")
        return str(out)

    def render_html(self) -> str:
        score = self.bundle.overall_habit_health_score
        score_color = "#10b981" if score >= 75 else ("#f59e0b" if score >= 50 else "#ef4444")
        zone = self.bundle.habit_zone
        ethics = self.bundle.manipulation_matrix_quadrant.value.capitalize()

        # Generate findings HTML
        findings_rows = []
        for f in self.bundle.findings:
            sev_color = {
                "critical": "#ef4444",
                "high": "#f97316",
                "medium": "#f59e0b",
                "low": "#3b82f6",
                "info": "#6b7280"
            }.get(f.severity.value, "#6b7280")

            verdict_badge = {
                "pass": '<span class="badge pass">PASS</span>',
                "fail": '<span class="badge fail">FAIL</span>',
                "warn": '<span class="badge warn">WARN</span>',
                "not_applicable": '<span class="badge na">N/A</span>',
            }.get(f.verdict.value, f.verdict.value)

            findings_rows.append(f"""
            <tr>
                <td><code>{f.control_id}</code></td>
                <td><span class="phase-tag">{f.phase.upper()}</span></td>
                <td><strong>{f.title}</strong><br/><small>{f.observation}</small></td>
                <td>{verdict_badge}</td>
                <td><span class="sev-tag" style="background-color: {sev_color}20; color: {sev_color}; border: 1px solid {sev_color}40;">{f.severity.value.upper()}</span></td>
                <td><div class="rec-text">{f.recommendation}</div></td>
            </tr>
            """)
        findings_html = "\n".join(findings_rows) if findings_rows else "<tr><td colspan='6'>No findings recorded.</td></tr>"

        # Cohort simulation summary table
        sim = self.bundle.simulation_results
        cohort_rows = []
        if sim and "cohort_summaries" in sim:
            for k, c in sim["cohort_summaries"].items():
                rate = c.get("day30_retention_rate", 0.0) * 100
                bar_color = "#10b981" if rate >= 40 else ("#f59e0b" if rate >= 20 else "#ef4444")
                cohort_rows.append(f"""
                <tr>
                    <td><strong>{c.get('display_name', k)}</strong></td>
                    <td>{c.get('initial', 100)}</td>
                    <td>{c.get('retained_day30', 0)}</td>
                    <td>
                        <div class="progress-wrap">
                            <div class="progress-bar" style="width: {min(100, max(5, rate))}%; background: {bar_color};"></div>
                            <span>{rate:.1f}%</span>
                        </div>
                    </td>
                </tr>
                """)
        cohort_html = "\n".join(cohort_rows) if cohort_rows else "<tr><td colspan='4'>Simulation data not available.</td></tr>"

        # Qualitative 5 Whys interview accordions
        interviews_html = []
        if sim and "churn_interviews" in sim:
            for interview in sim["churn_interviews"]:
                steps_html = []
                for s in interview.get("steps", []):
                    steps_html.append(f"""
                    <div class="interview-step">
                        <div class="why-badge">Why {s['why_level']}</div>
                        <div class="interview-dialogue">
                            <p class="q"><strong>Q:</strong> {s['interviewer_question']}</p>
                            <p class="a"><strong>A:</strong> "{s['persona_response']}"</p>
                            <p class="diag"><em>Diagnosis: {s['behavioral_diagnosis']}</em></p>
                        </div>
                    </div>
                    """)
                interviews_html.append(f"""
                <details class="interview-accordion">
                    <summary><strong>{interview['persona_name']}</strong> — Dropped out at {interview['dropoff_round']} (Root Itch: {interview['root_internal_itch']})</summary>
                    <div class="accordion-body">
                        {"".join(steps_html)}
                        <div class="interview-remedy">
                            <strong>Recommended Fix:</strong> {interview.get('actionable_remediation', '')}
                        </div>
                    </div>
                </details>
                """)
        interviews_rendered = "\n".join(interviews_html) if interviews_html else "<p>No interview records.</p>"

        # SVG Habit Zone Coordinate Calculation
        # Map (Utility: 0-10 -> X: 40 to 360, Freq: 0-10 -> Y: 360 to 40)
        px_x = 40 + (zone.perceived_utility_score / 10.0) * 320
        px_y = 360 - (zone.frequency_score / 10.0) * 320

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hook Model Audit: {self.bundle.project_name}</title>
<style>
:root {{
    --bg: #0f172a;
    --card: #1e293b;
    --border: #334155;
    --text: #f8fafc;
    --muted: #94a3b8;
    --accent: #3b82f6;
    --success: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
body {{ background-color: var(--bg); color: var(--text); padding: 2rem; line-height: 1.5; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
.title-wrap h1 {{ font-size: 1.8rem; font-weight: 700; }}
.title-wrap p {{ color: var(--muted); font-size: 0.95rem; }}
.score-badge {{ display: flex; align-items: center; gap: 1rem; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 0.75rem 1.5rem; }}
.score-circle {{ font-size: 2.2rem; font-weight: 800; color: {score_color}; }}
.score-label {{ font-size: 0.85rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}

.grid-4 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
.card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }}
.card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }}
.card-title {{ font-size: 1rem; font-weight: 600; color: var(--text); }}
.card-metric {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem; }}
.card-desc {{ font-size: 0.85rem; color: var(--muted); }}

.section {{ margin-bottom: 2.5rem; }}
.section-title {{ font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }}

.split-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
@media (max-width: 850px) {{ .split-2 {{ grid-template-columns: 1fr; }} }}

.zone-svg {{ width: 100%; height: auto; max-height: 380px; background: #131d31; border-radius: 8px; border: 1px solid var(--border); }}
table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; }}
th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border); }}
th {{ background: #131d31; color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}

.badge {{ padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 700; font-size: 0.75rem; }}
.badge.pass {{ background: #064e3b; color: #34d399; }}
.badge.warn {{ background: #78350f; color: #fbbf24; }}
.badge.fail {{ background: #7f1d1d; color: #f87171; }}
.badge.na {{ background: #374151; color: #9ca3af; }}
.phase-tag {{ font-size: 0.75rem; font-weight: 700; color: var(--accent); }}
.sev-tag {{ padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }}
.rec-text {{ font-size: 0.85rem; color: #cbd5e1; }}

.progress-wrap {{ display: flex; align-items: center; gap: 0.75rem; }}
.progress-bar {{ height: 8px; border-radius: 4px; transition: width 0.3s ease; }}

.interview-accordion {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.75rem; overflow: hidden; }}
.interview-accordion summary {{ padding: 1rem; cursor: pointer; background: #1a2436; font-size: 0.95rem; }}
.accordion-body {{ padding: 1.25rem; }}
.interview-step {{ display: flex; gap: 1rem; margin-bottom: 1rem; border-left: 2px solid var(--border); padding-left: 1rem; }}
.why-badge {{ background: var(--accent); color: #fff; font-size: 0.75rem; font-weight: 700; border-radius: 4px; padding: 0.2rem 0.4rem; height: fit-content; }}
.interview-dialogue p {{ margin-bottom: 0.35rem; font-size: 0.9rem; }}
.interview-dialogue .q {{ color: #cbd5e1; }}
.interview-dialogue .a {{ color: #38bdf8; }}
.interview-dialogue .diag {{ color: #f59e0b; font-size: 0.8rem; }}
.interview-remedy {{ margin-top: 1rem; padding: 0.75rem; background: #0f172a; border-left: 3px solid var(--success); border-radius: 4px; font-size: 0.9rem; }}
</style>
</head>
<body>
<div class="container">
    <header>
        <div class="title-wrap">
            <h1>Hook Model Behavioral Audit</h1>
            <p>Project: <strong>{self.bundle.project_name}</strong> &bull; Generated: {self.bundle.timestamp}</p>
        </div>
        <div class="score-badge">
            <div class="score-circle">{score}</div>
            <div>
                <div class="score-label">Habit Health Index</div>
                <div style="font-size: 0.85rem; color: var(--muted);">{self.bundle.summary_verdict}</div>
            </div>
        </div>
    </header>

    <!-- 4 Phases Grid -->
    <div class="grid-4">
        <div class="card">
            <div class="card-header">
                <span class="card-title">1. Triggers</span>
                <span>{len(self.bundle.hook_graph.triggers)} detected</span>
            </div>
            <div class="card-metric" style="color: {'#10b981' if self.bundle.hook_graph.triggers else '#ef4444'};">
                {'OWNED' if any(t.trigger_type.value == 'owned' for t in self.bundle.hook_graph.triggers) else 'WEAK'}
            </div>
            <div class="card-desc">External prompt scaffolding & internal emotional itch alignment</div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">2. Action (Fogg Sieve)</span>
                <span>B = MAT</span>
            </div>
            <div class="card-metric" style="color: {'#10b981' if self.bundle.fogg_simplicity_score >= 70 else '#f59e0b'};">
                {self.bundle.fogg_simplicity_score}<small style="font-size: 1rem; color: var(--muted);">/100</small>
            </div>
            <div class="card-desc">Simplicity across time, money, and mental/physical effort</div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">3. Variable Reward</span>
                <span>Nucleus Accumbens</span>
            </div>
            <div class="card-metric" style="color: {'#10b981' if self.bundle.reward_entropy_score >= 70 else '#f59e0b'};">
                {self.bundle.reward_entropy_score}<small style="font-size: 1rem; color: var(--muted);">/100</small>
            </div>
            <div class="card-desc">Dopamine variability (Tribe, Hunt, Self) vs satiation decay</div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">4. Investment</span>
                <span>IKEA Effect</span>
            </div>
            <div class="card-metric" style="color: {'#10b981' if self.bundle.stored_value_score >= 70 else '#f59e0b'};">
                {self.bundle.stored_value_score}<small style="font-size: 1rem; color: var(--muted);">/100</small>
            </div>
            <div class="card-desc">Compounding stored value (Content, Data, Reputation, Skill)</div>
        </div>
    </div>

    <!-- Habit Zone & Cohorts Section -->
    <div class="section split-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">The Habit Zone Coordinate</span>
                <span class="badge {'pass' if zone.in_habit_zone else 'fail'}">{'IN HABIT ZONE' if zone.in_habit_zone else 'OUTSIDE HABIT ZONE'}</span>
            </div>
            <svg class="zone-svg" viewBox="0 0 400 400">
                <!-- Axes -->
                <line x1="40" y1="360" x2="380" y2="360" stroke="#334155" stroke-width="2"/>
                <line x1="40" y1="360" x2="40" y2="20" stroke="#334155" stroke-width="2"/>
                <!-- Axis Labels -->
                <text x="210" y="390" fill="#94a3b8" font-size="12" text-anchor="middle">Perceived Utility (Painkiller Factor) &rarr;</text>
                <text x="-190" y="20" fill="#94a3b8" font-size="12" text-anchor="middle" transform="rotate(-90)">Frequency of Behavior &rarr;</text>
                <!-- Threshold Curve -->
                <path d="M 40 120 Q 180 200 360 330" fill="none" stroke="#f59e0b" stroke-dasharray="4 4" stroke-width="2"/>
                <text x="300" y="270" fill="#f59e0b" font-size="10">Habit Threshold Curve</text>
                <!-- Habit Zone fill -->
                <path d="M 40 120 Q 180 200 360 330 L 380 330 L 380 20 L 40 20 Z" fill="#10b981" fill-opacity="0.08"/>
                <text x="260" y="80" fill="#34d399" font-size="14" font-weight="bold">THE HABIT ZONE</text>
                <!-- Plotted Project Point -->
                <circle cx="{px_x}" cy="{px_y}" r="8" fill="{score_color}" stroke="#ffffff" stroke-width="2"/>
                <text x="{min(340, px_x + 12)}" y="{max(35, px_y + 4)}" fill="#ffffff" font-size="12" font-weight="bold">{self.bundle.project_name}</text>
            </svg>
            <p style="font-size: 0.85rem; color: var(--muted); margin-top: 0.5rem;">
                Classification: <strong>{zone.classification}</strong> (Freq: {zone.frequency_score}/10, Utility: {zone.perceived_utility_score}/10).
            </p>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">User Cohort 30-Day Retention Simulation</span>
                <span>{sim.get('overall_retention_rate', 0.0)*100:.1f}% Overall</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Cohort Archetype</th>
                        <th>Day 0</th>
                        <th>Day 30</th>
                        <th>Retention Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {cohort_html}
                </tbody>
            </table>
            <div style="margin-top: 1rem; font-size: 0.85rem; color: var(--muted);">
                Ethics Classification: <strong>{ethics}</strong> &bull; Manipulation Matrix: 
                <span style="color: {'#34d399' if ethics == 'Facilitator' else '#f87171'};">
                    {'High integrity (Maker uses it & creates material utility)' if ethics == 'Facilitator' else 'Review alignment'}
                </span>
            </div>
        </div>
    </div>

    <!-- Qualitative Churn Interviews -->
    <div class="section">
        <h2 class="section-title">Synthetic "5 Whys" Churn Interrogations</h2>
        <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem;">
            Qualitative interviews simulating dropped-out cohort personas to extract root-cause emotional friction.
        </p>
        {interviews_rendered}
    </div>

    <!-- Findings Table -->
    <div class="section">
        <h2 class="section-title">Audited Controls & Behavioral Findings ({len(self.bundle.findings)})</h2>
        <div class="card" style="overflow-x: auto; padding: 0;">
            <table>
                <thead>
                    <tr>
                        <th>Control ID</th>
                        <th>Phase</th>
                        <th>Finding & Observation</th>
                        <th>Verdict</th>
                        <th>Severity</th>
                        <th>Actionable Remediation</th>
                    </tr>
                </thead>
                <tbody>
                    {findings_html}
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>
"""
