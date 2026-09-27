# HookEngine Examples & Live Demo

This folder contains a sample SaaS application onboarding flow, live pre-generated audit reports, and empirical Mixpanel retention telemetry.

---

## 📂 Contents

1. **`sample-product/`**: A sample TypeScript/React SaaS application demonstrating:
   - `OnboardingWizard.tsx`: Fogg simplicity flow with Endowed Progress and fast-path setup.
   - `NotificationWorker.ts`: Owned external triggers (context-aware push notification and weekly digests).
   - `DiscoveryFeed.tsx`: Variable rewards of the Tribe, Hunt, and Self.
   - `Workspace.ts`: Compounding stored value (Content, Personal Data, Collaboration Network).

2. **`sample_telemetry.json`**: An empirical 30-day retention curve export from analytics (Mixpanel / PostHog) to calibrate simulated cohort retention.

3. **`sample_report.html`**: A live, standalone, interactive HTML dashboard generated directly from auditing `sample-product/`. Open it in any browser to explore the Habit Zone graph, EAST score card, and 5 Whys interview accordions.

4. **`sample_bundle.json`**: The complete machine-readable JSON audit bundle.

---

## 🚀 Try It Yourself

Run the audit command on the sample product:

```bash
# Run full behavioral audit with telemetry calibration and HTML report output
./bin/hook-engine audit ./examples/sample-product \
  --html ./examples/sample_report.html \
  --json ./examples/sample_bundle.json \
  --telemetry ./examples/sample_telemetry.json \
  --diff
```
