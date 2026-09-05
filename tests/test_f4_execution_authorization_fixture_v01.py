import unittest

from logosweaver import (
    ExecutionContract,
    FigureState,
    JudgeKind,
    JudgeVerdict,
    LogosWeaverRuntime,
    SemanticFigure,
    Verdict,
)


class FixedJudge:

    def __init__(self, kind, verdict):
        self.kind = kind
        self.verdict = verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, self.verdict, rationale="explicit test verdict")


class F4ExecutionAuthorizationFixtureTests(unittest.TestCase):

    def test_executable_figure_reaches_execution_authorization(self):
        figure = SemanticFigure(
            "f3-birth-001",
            "f3-fixture-workspace",
            distinctions=("A", "B"),
            constraints=("A에 대해서만 실행을 허용한다",),
            state=FigureState.CANDIDATE,
        )

        runtime = LogosWeaverRuntime()
        runtime.register(figure)
        runtime.transition(figure.figure_id, FigureState.BOUNDARY_REVIEW)
        runtime.transition(figure.figure_id, FigureState.RESONANCE_CANDIDATE)
        runtime.transition(figure.figure_id, FigureState.EXECUTABLE)

        contract = ExecutionContract.create(
            required_state=FigureState.EXECUTABLE,
        )
        runtime.attach_contract(figure.figure_id, contract)

        runtime.evaluate_contract(
            figure.figure_id,
            [FixedJudge(kind, Verdict.PASS) for kind in JudgeKind],
        )

        self.assertEqual(figure.state, FigureState.EXECUTABLE)

        trace = runtime.trace(figure.figure_id)
        event_types = [event.event_type for event in trace]
        self.assertIn("EXECUTION_CONTRACT_ATTACHED", event_types)
        self.assertEqual(event_types[-1], "EXECUTION_AUTHORIZED")

        judge_events = [event for event in trace if event.event_type == "JUDGE_EVALUATED"]
        self.assertEqual(len(judge_events), len(JudgeKind))
        self.assertEqual(
            {event.payload["judge"] for event in judge_events},
            {kind.value for kind in JudgeKind},
        )


if __name__ == "__main__":
    unittest.main()