"""F.5 evidence fixture for explicit Runtime lifecycle-to-lineage reconstruction.

This fixture intentionally uses test-controlled lifecycle transitions and explicit
lineage composition. It does not introduce or claim a mutation or identity engine.
"""

import unittest

from logosweaver import (
    ExecutionContract,
    FigureState,
    JudgeKind,
    JudgeVerdict,
    Lineage,
    LineageRelation,
    LogosWeaverRuntime,
    SemanticFigure,
    Verdict,
)


class FixedPassJudge:

    def __init__(self, kind):
        self.kind = kind

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, Verdict.PASS, rationale="explicit test-controlled PASS")


class F5RuntimeMvpLineageFixtureTests(unittest.TestCase):

    def test_runtime_mvp_lifecycle_to_lineage_evidence(self):
        workspace_id = "f5-fixture-workspace"
        figure_a = SemanticFigure("f5-figure-a", workspace_id)
        runtime = LogosWeaverRuntime()

        runtime.register(figure_a)
        for target in (
            FigureState.BOUNDARY_REVIEW,
            FigureState.RESONANCE_CANDIDATE,
            FigureState.EXECUTABLE,
        ):
            runtime.transition(figure_a.figure_id, target)

        runtime.attach_contract(
            figure_a.figure_id,
            ExecutionContract.create(required_state=FigureState.EXECUTABLE),
        )
        runtime.evaluate_contract(
            figure_a.figure_id,
            [FixedPassJudge(kind) for kind in JudgeKind],
        )

        runtime.transition(figure_a.figure_id, FigureState.EXECUTED)
        runtime.transition(figure_a.figure_id, FigureState.OBSERVED)
        runtime.transition(figure_a.figure_id, FigureState.IDENTITY_REVIEW)
        runtime.transition(figure_a.figure_id, FigureState.MUTATED)

        figure_b = SemanticFigure("f5-figure-b", workspace_id)
        runtime.register(figure_b)

        self.assertIn(figure_a.figure_id, runtime.figures)
        self.assertIn(figure_b.figure_id, runtime.figures)
        self.assertNotEqual(figure_a.figure_id, figure_b.figure_id)
        self.assertEqual(figure_b.workspace_id, figure_a.workspace_id)

        lineage = Lineage(
            source_figure_id=figure_a.figure_id,
            target_figure_id=figure_b.figure_id,
            relations=(LineageRelation.MUTATED_FROM,),
        )
        runtime.add_lineage(lineage)

        relevant_lineages = [
            item
            for item in runtime.lineages
            if item.source_figure_id == figure_a.figure_id
            and item.target_figure_id == figure_b.figure_id
        ]
        self.assertEqual(relevant_lineages, [lineage])
        self.assertEqual(relevant_lineages[0].source_figure_id, figure_a.figure_id)
        self.assertEqual(relevant_lineages[0].target_figure_id, figure_b.figure_id)
        self.assertIn(LineageRelation.MUTATED_FROM, relevant_lineages[0].relations)

        trace_a = runtime.trace(figure_a.figure_id)
        trace_b = runtime.trace(figure_b.figure_id)
        event_types_a = [event.event_type for event in trace_a]
        event_types_b = [event.event_type for event in trace_b]

        self.assertIn("FIGURE_REGISTERED", event_types_a)
        self.assertEqual(
            [
                (event.payload["previous"], event.payload["target"])
                for event in trace_a
                if event.event_type == "STATE_TRANSITIONED"
            ],
            [
                (FigureState.CANDIDATE.value, FigureState.BOUNDARY_REVIEW.value),
                (FigureState.BOUNDARY_REVIEW.value, FigureState.RESONANCE_CANDIDATE.value),
                (FigureState.RESONANCE_CANDIDATE.value, FigureState.EXECUTABLE.value),
                (FigureState.EXECUTABLE.value, FigureState.EXECUTED.value),
                (FigureState.EXECUTED.value, FigureState.OBSERVED.value),
                (FigureState.OBSERVED.value, FigureState.IDENTITY_REVIEW.value),
                (FigureState.IDENTITY_REVIEW.value, FigureState.MUTATED.value),
            ],
        )
        self.assertIn("JUDGE_EVALUATED", event_types_a)
        self.assertIn("EXECUTION_AUTHORIZED", event_types_a)
        self.assertEqual(figure_a.state, FigureState.MUTATED)

        mutated_transition = [
            event
            for event in trace_a
            if event.event_type == "STATE_TRANSITIONED"
            and event.payload["target"] == FigureState.MUTATED.value
        ]
        self.assertEqual(len(mutated_transition), 1)

        self.assertIn("FIGURE_REGISTERED", event_types_b)
        self.assertIn("LINEAGE_RECORDED", event_types_b)
        lineage_events = [
            event for event in trace_b if event.event_type == "LINEAGE_RECORDED"
        ]
        self.assertEqual(len(lineage_events), 1)
        self.assertEqual(
            lineage_events[0].payload["source_figure_id"],
            figure_a.figure_id,
        )

        self.assertTrue(all(event.figure_id == figure_a.figure_id for event in trace_a))
        self.assertTrue(all(event.figure_id == figure_b.figure_id for event in trace_b))
        self.assertNotIn("LINEAGE_RECORDED", event_types_a)
        self.assertNotIn("BOUNDARY_REVIEW", [event.payload.get("target") for event in trace_b])


if __name__ == "__main__":
    unittest.main()
