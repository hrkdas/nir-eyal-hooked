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

        # EAST Framework Card
        east = self.bundle.east_score
        east_html = ""
        if east:
            overall_pct = int(east.overall * 100)
            easy_pct = int(east.easy * 100)
            attractive_pct = int(east.attractive * 100)
            social_pct = int(east.social * 100)
            timely_pct = int(east.timely * 100)
            east_html = f"""
    <div class="card" style="margin-bottom: 2rem;">
        <div class="card-header">
            <span class="card-title">EAST Behavioral Framework Diagnostic</span>
            <span class="badge {'pass' if overall_pct >= 70 else 'warn'}">EAST Score: {overall_pct}/100</span>
        </div>
        <div class="east-grid">
            <div class="east-item">
                <div class="east-label"><span><strong>E</strong>asy</span> <span>{easy_pct}/100</span></div>
                <div class="progress-wrap"><div class="progress-bar" style="width: {easy_pct}%; background: #38bdf8;"></div></div>
                <small style="color: var(--muted); font-size: 0.75rem;">Frictionless default paths & progressive disclosure</small>
            </div>
            <div class="east-item">
                <div class="east-label"><span><strong>A</strong>ttractive</span> <span>{attractive_pct}/100</span></div>
                <div class="progress-wrap"><div class="progress-bar" style="width: {attractive_pct}%; background: #a855f7;"></div></div>
                <small style="color: var(--muted); font-size: 0.75rem;">Salient cues & immediate dopamine anticipation</small>
            </div>
            <div class="east-item">
                <div class="east-label"><span><strong>S</strong>ocial</span> <span>{social_pct}/100</span></div>
                <div class="progress-wrap"><div class="progress-bar" style="width: {social_pct}%; background: #ec4899;"></div></div>
                <small style="color: var(--muted); font-size: 0.75rem;">Tribe validation, social proof & peer loops</small>
            </div>
            <div class="east-item">
                <div class="east-label"><span><strong>T</strong>imely</span> <span>{timely_pct}/100</span></div>
                <div class="progress-wrap"><div class="progress-bar" style="width: {timely_pct}%; background: #10b981;"></div></div>
                <small style="color: var(--muted); font-size: 0.75rem;">Context-aware prompts & trigger priming</small>
            </div>
        </div>
    </div>
            """

        # TTV Stopwatch Card
        ttv_metrics = self.bundle.ttv_metrics
        ttv = ttv_metrics.estimated_ttv_seconds if ttv_metrics else 20
        ttv_rating = ttv_metrics.rating if ttv_metrics else "Optimal (<45s)"
        ttv_color = "#10b981" if ttv <= 25 else ("#f59e0b" if ttv <= 45 else "#ef4444")
        ttv_badge_html = f"""
        <div class="card">
            <div class="card-header">
                <span class="card-title">Time-to-Value (TTV) Stopwatch</span>
                <span class="badge" style="background: {ttv_color}20; color: {ttv_color}; border: 1px solid {ttv_color}40;">{ttv_rating}</span>
            </div>
            <div class="card-metric" style="color: {ttv_color};">~{ttv}s <small style="font-size: 0.9rem; color: var(--muted);">to first Aha! moment</small></div>
            <div class="card-desc">Simulated clock from initial landing / prompt arrival to first core value delivery.</div>
        </div>
        """

        # Riskiest Habit Assumptions (RAT)
        rat = self.bundle.rat_assumption
        rat_rows = []
        if rat:
            rat_rows.append(f"""
            <tr>
                <td><span class="phase-tag">CORE LOOP</span></td>
                <td><strong>{rat.hypothesis}</strong></td>
                <td><span class="badge warn">{rat.risk_level.upper()}</span></td>
                <td><code>{rat.test_method}</code></td>
                <td><span style="color: #38bdf8;">{rat.success_metric}</span></td>
            </tr>
            """)
        rat_table_html = "\n".join(rat_rows) if rat_rows else "<tr><td colspan='5'>No critical habit assumptions flagged.</td></tr>"

        # Empirical telemetry comparison table
        empirical_html = ""
        if sim and sim.get("empirical_comparison"):
            emp_comp = sim["empirical_comparison"]
            emp_rows = []
            for r in emp_comp.get("rounds", []):
                r_id = r.get("round_id")
                sim_pct = r.get("simulated_retention_pct", 0.0)
                emp_pct = r.get("empirical_retention_pct")
                delta = r.get("delta_pct")
                delta_str = "N/A"
                delta_color = "var(--muted)"
                if delta is not None:
                    delta_str = f"{delta:+.1f}%"
                    delta_color = "#10b981" if abs(delta) <= 5.0 else ("#f59e0b" if abs(delta) <= 15.0 else "#ef4444")
                emp_rows.append(f"""
                <tr>
                    <td><strong>{r_id}</strong></td>
                    <td>{sim_pct:.1f}%</td>
                    <td>{f"{emp_pct:.1f}%" if emp_pct is not None else "N/A"}</td>
                    <td><span style="color: {delta_color}; font-weight: bold;">{delta_str}</span></td>
                </tr>
                """)
            empirical_html = f"""
            <div style="margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <span style="font-weight: 600; font-size: 0.95rem;">Empirical Telemetry Calibration (Mixpanel / PostHog)</span>
                    <span class="badge pass">Calibrated</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Round</th>
                            <th>Simulated</th>
                            <th>Empirical Actual</th>
                            <th>Delta</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(emp_rows)}
                    </tbody>
                </table>
            </div>
            """

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
.east-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }}
.east-item {{ background: #131d31; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid var(--border); }}
.east-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem; }}
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

    <!-- EAST Behavioral Framework Card (if analyzed) -->
    {east_html}

    <!-- 4 Phases + TTV Stopwatch Grid -->
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

    <!-- TTV Stopwatch Highlight -->
    <div style="margin-bottom: 2rem;">
        {ttv_badge_html}
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
            {empirical_html}
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

    <!-- Riskiest Habit Assumption Tests (RAT) Section -->
    <div class="section">
        <h2 class="section-title">Riskiest Habit Assumption Tests (RAT Matrix)</h2>
        <p style="color: var(--muted); font-size: 0.9rem; margin-bottom: 1rem;">
            Empirical falsification hypotheses testing core habit assumptions before scaling spend.
        </p>
        <div class="card" style="overflow-x: auto; padding: 0;">
            <table>
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Core Habit Assumption</th>
                        <th>Vulnerability Hypothesis</th>
                        <th>Validation Telemetry Metric</th>
                        <th>Failure Threshold</th>
                    </tr>
                </thead>
                <tbody>
                    {rat_table_html}
                </tbody>
            </table>
        </div>
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
