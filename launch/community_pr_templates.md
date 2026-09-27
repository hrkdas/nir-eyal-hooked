# Community PR & Directory Submission Templates

Use these templates to submit HookEngine to open-source skill collections, awesome-lists, and agent registries.

---

## 1. Submission to `agentskills.io` / `anthropics/skills`
**PR Title:** `feat(skills): add nir-eyal-hooked behavioral audit skill`

**PR Description:**
```markdown
### Summary
Adds the `hooked` skill, an autonomous behavioral audit, cohort simulation, and UX remediation engine based on Nir Eyal's Hook Model (*Hooked: How to Build Habit-Forming Products*).

- **Skill Entrypoint:** `skills/hooked/SKILL.md`
- **Zero Dependencies:** Pure Python 3.10+ standard library.
- **Capabilities:** AST friction scanner, Habit Zone coordinate ($Utility \times Frequency$), Fogg Simplicity Index ($B=MAT$), UK BIT EAST scoring, 30-day cohort simulation with synthetic "5 Whys" churn interviews, and unified remediation diffs.
- **Repository:** https://github.com/hrkdas/nir-eyal-hooked
- **License:** MIT
```

---

## 2. Submission to `awesome-claude-skills` / `awesome-cursorrules`
**Entry Markdown:**
```markdown
- [HookEngine](https://github.com/hrkdas/nir-eyal-hooked) - Autonomous behavioral audit, habit simulation, and UX remediation engine based on Nir Eyal's Hook Model (Trigger, Action, Variable Reward, Investment) with 30-day cohort churn simulation.
```

---

## 3. Product Hunt Launch Kit (`launch/product_hunt.md`)
- **Product Name:** HookEngine
- **Tagline:** Nir Eyal Hook Model behavioral audit & retention simulator
- **Pricing:** Free / Open Source (MIT)
- **Topics:** Developer Tools, Artificial Intelligence, Product Management, Growth Hacking, User Experience
- **Maker Comment:**
> "Hey Product Hunt! We turned Nir Eyal's *Hooked* framework into an open-source behavioral engine and AI agent skill. It scans your app or PRD, models the Habit Zone ($Utility \times Frequency$), simulates 30-day cohort churn, and generates git diffs to fix onboarding drop-off. 100% zero-dependency Python stdlib. Check it out and let us know what you think!"
