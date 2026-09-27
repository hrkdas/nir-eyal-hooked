# Show HN: HookEngine – An open-source Nir Eyal Hook Model auditor for codebases

**URL:** https://github.com/hrkdas/nir-eyal-hooked

---

## Submission Text

Hi HN!

Most product engineers and founders are familiar with Nir Eyal's *Hooked* framework (Trigger -> Action -> Variable Reward -> Investment), but evaluating whether a software codebase or onboarding flow actually forms sustainable habits usually ends up as subjective product debates.

We built **HookEngine** (https://github.com/hrkdas/nir-eyal-hooked), a zero-dependency CLI and AI Agent skill (for Claude Code, Cursor, Codex, and Antigravity) that statically audits codebases and user flows, scores behavioral habit math, and runs multi-agent cohort retention simulations.

### Key Capabilities:
1. **Deterministic AST Codebase Scanner**: Inspects form field friction, auth walls, and click-step friction.
2. **Behavioral Habit Math**: Computes the Habit Zone Coordinate ($x = \text{Utility}, y = \text{Frequency}$), BJ Fogg's Simplicity Sieve ($B=MAT$), and the UK Behavioural Insights Team EAST score (Easy, Attractive, Social, Timely).
3. **Time-to-Value (TTV) Stopwatch**: Estimates wall-clock friction to the first "Aha!" moment and detects dropped activation cliffs.
4. **30-Day Multi-Agent Cohort Simulator**: Simulates 5 distinct user psychographics (Casual Novice, Anxious Pro, Cynic, Power Devotee, Busy Multitasker) across 30 days of simulated drop-off.
5. **Synthetic "5 Whys" Churn Interrogations**: Autonomously interrogates churned personas to uncover root-cause friction.
6. **Empirical Telemetry Calibration**: Ingests Mixpanel or PostHog retention exports to align simulations against real data.
7. **Actionable Remediation Diffs**: Generates unified git-style code/copy patches (e.g. Endowed Progress wizards, progressive disclosure).

It runs 100% offline with zero third-party dependencies (pure Python 3.10+ standard library).

```bash
# Quick run
git clone https://github.com/hrkdas/nir-eyal-hooked.git
cd nir-eyal-hooked
./bin/hook-engine audit ./my-app --html report.html --diff
```

We also included an interactive demo report in `examples/sample_report.html` and chapter-by-chapter distillations in `chapters/` and `ideology/`.

Would love feedback from engineers, designers, and growth builders on the behavioral heuristics and simulation curves!
