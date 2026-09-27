"""
Audit Report Builder: Combines scanning, scoring, simulation, and qualitative interviews
into a standardized, validated AuditBundle JSON artifact.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..core.models import AuditBundle, HookGraph
from ..core.scorer import HabitScorer
from ..simulation.lifecycle import LifecycleSimulator, SimulationRunResult
from ..simulation.interviewer import SyntheticInterviewer, ChurnInterviewTranscript
from ..simulation.cohorts import get_default_cohorts


class AuditReportBuilder:
    """
    Coordinates the full audit pipeline and compiles the master AuditBundle.
    """

    def __init__(self, graph: HookGraph):
        self.graph = graph

    def build(self, run_simulation: bool = True, run_interviews: bool = True) -> AuditBundle:
        """Executes scoring and optional lifecycle simulation to build complete bundle."""
        scorer = HabitScorer(self.graph)
        bundle = scorer.score()

        if run_simulation:
            cohorts = get_default_cohorts()
            sim = LifecycleSimulator(self.graph, cohorts=cohorts)
            sim_result = sim.run()
            bundle.simulation_results = sim_result.to_dict()

            if run_interviews:
                interviewer = SyntheticInterviewer(self.graph)
                transcripts: List[Dict[str, Any]] = []

                # Interview the two most vulnerable cohorts
                for cohort in cohorts[:2]:
                    transcript = interviewer.interview_cohort(cohort, dropoff_round="Day 0")
                    transcripts.append(transcript.to_dict())

                bundle.simulation_results["churn_interviews"] = transcripts

        return bundle

    @staticmethod
    def export_json(bundle: AuditBundle, output_path: str) -> str:
        """Exports the AuditBundle to a formatted JSON file."""
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        data = bundle.to_dict()
        out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(out)
