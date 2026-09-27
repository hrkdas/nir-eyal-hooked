# Reference 08: EAST Behavioral Framework, TTV Stopwatch & Overjustification Defense

This document details the behavioral science foundations and scoring heuristics implemented in HookEngine for EAST, Time-to-Value (TTV) velocity, the Overjustification Effect, and Riskiest Habit Assumption Testing (RAT).

---

## 1. The EAST Framework (UK Behavioural Insights Team)

Developed by the Behavioural Insights Team (BIT), the EAST framework posits that to encourage any behavior, you must make it:
1. **Easy** (Reduce cognitive and physical friction, harness defaults, streamline choice architecture).
2. **Attractive** (Attract attention, personalize cues, frame immediate rewards).
3. **Social** (Show that most people perform the desired behavior, encourage peer commitments, network effects).
4. **Timely** (Prompt users when they are most receptive, immediate vs delayed costs/benefits, trigger priming).

### Mapping to Nir Eyal's Hook Model

| EAST Dimension | Hook Model Phase | Heuristic & Metric in HookEngine | Target Threshold |
| :--- | :--- | :--- | :--- |
| **Easy** | **Action** | Input fields $\le 3$, zero mandatory upfront auth-walls, 1-click execution. | $\ge 75/100$ |
| **Attractive** | **Variable Reward** | High reward entropy across Tribe, Hunt, and Self. Visual salience of cues. | $\ge 70/100$ |
| **Social** | **Trigger & Reward** | Tribe rewards (likes, comments, badges, collaboration) + peer external prompts. | $\ge 60/100$ |
| **Timely** | **Trigger & Investment**| Stored value immediately priming the next context-aware prompt; re-engagement window. | $\ge 70/100$ |

---

## 2. Time-to-Value (TTV) Stopwatch & The Endowed Progress Effect

### The TTV Stopwatch Metric
Time-to-Value measures the simulated wall-clock latency (in seconds) between the user's initial interaction (landing or prompt click) and their first **Aha! moment** (delivery of variable reward or tangible progress).

- **Instant ($\le 20\text{s}$):** Highest habit formation potential. Friction is minimal, Fogg Ability is maximal.
- **Moderate ($21 - 45\text{s}$):** Tolerable for B2B or productivity tools with high motivation ($M$).
- **Excessive ($> 45\text{s}$):** Critical drop-off cliff. Without an early perceived win, users abandon the flow.

### Nunes & Dreze (2006) Endowed Progress Effect
When people believe they have already made progress toward completing a goal, they are significantly more committed to completing it.

**Remediation Pattern (`HOOK-ACT-04`):**
Instead of showing an empty 3-step wizard (0% progress), frame the initial screen as **Step 2 of 3 (66% completed)** with smart defaults already configured. This leverages artificial progress to slash psychological friction and accelerate TTV.

---

## 3. The Overjustification Effect (Deci, 1971; Lepper et al., 1973)

### The Psychological Risk
When an intrinsically motivating activity is artificially rewarded with extrinsic incentives (points, tokens, superficial badges), the user's intrinsic motivation is crowded out. Once the extrinsic novelty wears off (point fatigue), engagement drops below the baseline.

### HookEngine Heuristics (`HOOK-REW-03`)
- **Warning Flag:** Detected point/streak/coin systems operating *without* social validation (Tribe) or competence feedback (Self).
- **Remediation Pattern:**
  - Shift reward framing from "You earned 10 points" to "Mastery Unlocked: You automated your first workflow and saved your team 2.4 hours."
  - Couple extrinsic milestones with shareable artifacts (social proof) or increased capability (unlocking advanced features).

---

## 4. Riskiest Habit Assumption Testing (RAT)

Before pouring paid acquisition spend into top-of-funnel loops, product teams must validate their riskiest habit assumptions. HookEngine automatically synthesizes falsifiable RAT hypotheses:

1. **Trigger Phase:** Users experience an authentic emotional itch within 24 hours of onboarding.
   - *Failure Hypothesis:* External prompts are treated as spam because users lack recurring internal anxiety or curiosity.
   - *Validation Telemetry:* Open rate on 24h re-engagement trigger $> 25\%$.
2. **Action Phase:** First-time users reach the Aha! moment in under 30 seconds.
   - *Failure Hypothesis:* Onboarding form friction triggers immediate tab-closing drop-off.
   - *Validation Telemetry:* Day-0 activation completion rate $> 60\%$.
3. **Reward Phase:** Core variable reward delivers unpredictable dopamine and perceived utility.
   - *Failure Hypothesis:* Reward format is static and deterministic; satiation sets in by Day 3.
   - *Validation Telemetry:* Day-3 to Day-7 retention drop-off $< 50\%$.
4. **Investment Phase:** Users willingly store personal data or custom settings to reduce future effort.
   - *Failure Hypothesis:* Zero stored value; switching cost remains zero, making user susceptible to competitors.
   - *Validation Telemetry:* Stored value creation rate per active user $> 40\%$.
