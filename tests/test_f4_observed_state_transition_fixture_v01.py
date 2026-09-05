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


class F4ObservedStateTransitionFixtureTests(unittest.TestCase):

    def test_executed_figure_reaches_observed_state_transition(self):
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

        runtime.transition(figure.figure_id, FigureState.EXECUTED)
        runtime.transition(figure.figure_id, FigureState.OBSERVED)

        self.assertEqual(figure.state, FigureState.OBSERVED)

        trace = runtime.trace(figure.figure_id)
        event_types = [event.event_type for event in trace]
        self.assertEqual(
            event_types,
            [
                "FIGURE_REGISTERED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
                "EXECUTION_CONTRACT_ATTACHED",
                "JUDGE_EVALUATED",
                "JUDGE_EVALUATED",
                "JUDGE_EVALUATED",
                "JUDGE_EVALUATED",
                "EXECUTION_AUTHORIZED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
            ],
        )

        transitioned_events = [
            event for event in trace if event.event_type == "STATE_TRANSITIONED"
        ]
        self.assertEqual(
            transitioned_events[-2].payload,
            {"previous": FigureState.EXECUTABLE.value, "target": FigureState.EXECUTED.value},
        )
        self.assertEqual(
            transitioned_events[-1].payload,
            {"previous": FigureState.EXECUTED.value, "target": FigureState.OBSERVED.value},
        )


if __name__ == "__main__":
    unittest.main()
