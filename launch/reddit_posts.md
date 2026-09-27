# Reddit Launch Posts

---

## 1. r/ProductManagement
**Title:** I built an open-source tool that statically audits codebases against Nir Eyal's Hook Model (and simulates 30-day cohort churn)

**Post:**
Hey r/ProductManagement,

One common challenge when shipping new onboarding flows is that product managers, designers, and engineers end up in subjective arguments about "user friction" or whether an onboarding flow has "too many steps."

To bring empirical behavioral science into our development cycle, I built an open-source tool called **HookEngine** (https://github.com/hrkdas/nir-eyal-hooked).

It's based on Nir Eyal's *Hooked* (Trigger -> Action -> Variable Reward -> Investment):
1. **Fogg Simplicity Sieve ($B=MAT$)**: Automatically inspects form field counts, auth walls, and step friction.
2. **Habit Zone Coordinate**: Maps your product on $Utility \times Frequency$ (Painkiller vs. Vitamin).
3. **EAST Framework**: Scores Easy, Attractive, Social, and Timely drivers.
4. **30-Day Cohort Simulation**: Models 5 user archetypes over 30 days and runs automated "5 Whys" exit interviews with churned users.
5. **Real Telemetry Calibration**: Ingests Mixpanel/PostHog retention exports to compare simulated curves against real-world retention.

It's zero-dependency (standard library only) and works both as a standalone CLI and an AI agent skill for Claude Code and Cursor.

All source code and reference guides are open under MIT:
https://github.com/hrkdas/nir-eyal-hooked

Would love to hear how you currently audit user habit formation in your teams!

---

## 2. r/SaaS & r/IndieHackers
**Title:** Stop losing users on Day 3: Open-source Hook Model auditor for your SaaS onboarding

**Post:**
If your SaaS has decent top-of-funnel traffic but users vanish after their first session, you likely have an incomplete Hook Loop or a high Time-to-Value (TTV) cliff.

I turned Nir Eyal's *Hooked* framework into an open-source CLI that scans your app, scores your habit mechanics, and generates git diffs (e.g. Endowed Progress wizards and 1-click fast paths) to fix drop-offs:

👉 https://github.com/hrkdas/nir-eyal-hooked

Key features:
- Statically scans React/TypeScript/Python forms and click-paths
- Generates an interactive self-contained HTML dashboard
- Runs synthetic 5 Whys interviews with churned user personas
- Zero dependencies — runs anywhere with Python 3.10+

Check it out and let me know if it surfaces interesting insights about your onboarding flow!
