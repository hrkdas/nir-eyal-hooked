"""
Command Line Interface (CLI) for HookEngine.
Usage:
    python -m hook_engine audit <target_path> [--html report.html] [--json bundle.json] [--diff]
    python -m hook_engine scan <target_path>
    python -m hook_engine simulate <target_path> [--users 100]
    python -m hook_engine diff <target_path>
"""

import sys
import argparse
from pathlib import Path

from .core.scanner import CodebaseScanner
from .core.scorer import HabitScorer
from .simulation.lifecycle import LifecycleSimulator
from .simulation.cohorts import get_default_cohorts
from .reporting.builder import AuditReportBuilder
from .reporting.html_generator import HTMLReportGenerator
from .reporting.patch_generator import PatchGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hook_engine",
        description="Nir Eyal Hook Model Behavioral Audit & Simulation Engine."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Run end-to-end Hook Model audit")
    audit_parser.add_argument("target", help="Path to project directory, PRD file, or code file")
    audit_parser.add_argument("--html", help="Path to write interactive HTML dashboard", default=None)
    audit_parser.add_argument("--json", help="Path to write JSON audit bundle", default=None)
    audit_parser.add_argument("--diff", action="store_true", help="Print remediation code/copy diffs")
    audit_parser.add_argument("--no-sim", action="store_true", help="Skip 30-day cohort simulation")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", help="Scan codebase and extract Hook Graph")
    scan_parser.add_argument("target", help="Path to project directory or file")

    # Command: simulate
    sim_parser = subparsers.add_parser("simulate", help="Run 30-day multi-cohort retention simulation")
    sim_parser.add_argument("target", help="Path to project directory or file")
    sim_parser.add_argument("--users", type=int, default=100, help="Initial population per cohort")

    # Command: diff
    diff_parser = subparsers.add_parser("diff", help="Generate code & copy remediation diffs")
    diff_parser.add_argument("target", help="Path to project directory or file")

    return parser


def cmd_audit(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    print(f"\n[HookEngine] Running behavioral audit on: {target.name} ({target})")

    # 1. Scan
    scanner = CodebaseScanner(str(target))
    graph = scanner.scan()
    print(f"  > Scanned Hook Graph: {len(graph.triggers)} triggers, {len(graph.actions)} actions, "
          f"{len(graph.rewards)} rewards, {len(graph.investments)} investments.")

    # 2. Build Report Bundle
    builder = AuditReportBuilder(graph)
    bundle = builder.build(run_simulation=not args.no_sim, run_interviews=not args.no_sim)

    # 3. Print Executive Summary
    print("\n" + "=" * 60)
    print(f"  EXECUTIVE HABIT HEALTH SCORE: {bundle.overall_habit_health_score} / 100")
    print(f"  HABIT ZONE COORDINATE: Freq={bundle.habit_zone.frequency_score}/10, Utility={bundle.habit_zone.perceived_utility_score}/10")
    print(f"  HABIT CLASSIFICATION: {bundle.habit_zone.classification}")
    print(f"  MANIPULATION MATRIX:  {bundle.manipulation_matrix_quadrant.value.upper()}")
    print(f"  FOGG SIMPLICITY:      {bundle.fogg_simplicity_score} / 100")
    print(f"  REWARD ENTROPY:       {bundle.reward_entropy_score} / 100")
    print(f"  STORED VALUE:         {bundle.stored_value_score} / 100")
    print("=" * 60)

    print(f"\nSummary Verdict: {bundle.summary_verdict}")

    # Print Findings Overview
    print(f"\nAudit Findings ({len(bundle.findings)}):")
    for f in bundle.findings:
        icon = "[PASS]" if f.verdict.value == "pass" else ("[WARN]" if f.verdict.value == "warn" else "[FAIL]")
        print(f"  {icon:<6} {f.control_id:<14} [{f.phase.upper():<10}] {f.title}")

    # Cohort Retention Summary
    sim = bundle.simulation_results
    if sim and "cohort_summaries" in sim:
        print("\n30-Day Cohort Retention Simulation:")
        for k, c in sim["cohort_summaries"].items():
            rate = c.get("day30_retention_rate", 0.0) * 100
            print(f"  * {c.get('display_name', k):<24} : {rate:>5.1f}% retained (Started {c.get('initial')})")

    # Export JSON
    if args.json:
        out_json = builder.export_json(bundle, args.json)
        print(f"\n[+] Saved JSON audit bundle: {out_json}")

    # Export HTML
    if args.html:
        generator = HTMLReportGenerator(bundle)
        out_html = generator.generate(args.html)
        print(f"[+] Saved interactive HTML dashboard: {out_html}")

    # Print Diffs
    if args.diff:
        patch_gen = PatchGenerator(bundle)
        patches = patch_gen.generate_patches()
        if patches:
            print(f"\nActionable Remediation Diffs ({len(patches)}):")
            for p in patches:
                print(f"\n--- {p.title} ({p.target_file}) ---")
                print(p.diff_content)
        else:
            print("\nNo code diffs required; product passes core simplicity controls.")

    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    scanner = CodebaseScanner(str(target))
    graph = scanner.scan()

    print(f"\n[HookEngine] Hook Graph for: {graph.project_name}")
    print(f"Loop Connected: {graph.loop_connected}")

    print("\n1. Triggers:")
    for t in graph.triggers:
        print(f"  * [{t.trigger_type.value.upper()}] {t.name} ({t.channel}) - {t.source_reference}")

    print("\n2. Actions:")
    for a in graph.actions:
        print(f"  * {a.name} ({a.input_fields_count} inputs, {a.steps_count} steps) - AuthWall={a.requires_auth_wall}")

    print("\n3. Variable Rewards:")
    for r in graph.rewards:
        print(f"  * [{r.reward_type.value.upper()}] {r.name} (Infinite={r.is_infinite_variability})")

    print("\n4. Investments (Stored Value):")
    for i in graph.investments:
        print(f"  * [{i.stored_value_type.value.upper()}] {i.name} (PrimesNext={i.loads_next_trigger})")

    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    scanner = CodebaseScanner(str(target))
    graph = scanner.scan()

    cohorts = get_default_cohorts(population_per_cohort=args.users)
    sim = LifecycleSimulator(graph, cohorts=cohorts)
    res = sim.run()

    print(f"\n[HookEngine] 30-Day Cohort Simulation for {graph.project_name}")
    print(f"Total Users: {res.total_initial_users} | Retained Day 30: {res.total_day30_retained} ({res.overall_retention_rate*100:.1f}%)")

    for k, c in res.cohort_summaries.items():
        hist = c.get("history", {})
        curve_str = " -> ".join(f"{round_id}:{count}" for round_id, count in hist.items())
        print(f"\nCohort: {c.get('display_name')}")
        print(f"  Trajectory: {curve_str}")

    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    target = Path(args.target).resolve()
    scanner = CodebaseScanner(str(target))
    graph = scanner.scan()

    scorer = HabitScorer(graph)
    bundle = scorer.score()

    patch_gen = PatchGenerator(bundle)
    patches = patch_gen.generate_patches()

    print(f"\n[HookEngine] Recommended Remediation Diffs for: {graph.project_name} ({len(patches)} patches)")
    for p in patches:
        print(f"\n# {p.title}")
        print(f"# Target: {p.target_file} | Rationale: {p.rationale}")
        print(p.diff_content)

    return 0


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "audit":
        return cmd_audit(args)
    elif args.command == "scan":
        return cmd_scan(args)
    elif args.command == "simulate":
        return cmd_simulate(args)
    elif args.command == "diff":
        return cmd_diff(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
