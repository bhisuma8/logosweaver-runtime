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


class F4ExecutedStateTransitionFixtureTests(unittest.TestCase):

    def test_executable_figure_reaches_executed_state_transition(self):
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

        authorized_trace = runtime.trace(figure.figure_id)
        authorized_event_types = [event.event_type for event in authorized_trace]
        self.assertIn("EXECUTION_AUTHORIZED", authorized_event_types)

        runtime.transition(figure.figure_id, FigureState.EXECUTED)

        self.assertEqual(figure.state, FigureState.EXECUTED)

        trace = runtime.trace(figure.figure_id)
        event_types = [event.event_type for event in trace]
        authorized_index = event_types.index("EXECUTION_AUTHORIZED")
        transitioned_events = [
            event for event in trace[authorized_index + 1:]
            if event.event_type == "STATE_TRANSITIONED"
        ]
        self.assertTrue(transitioned_events)
        self.assertEqual(
            transitioned_events[0].payload,
            {"previous": FigureState.EXECUTABLE.value, "target": FigureState.EXECUTED.value},
        )


if __name__ == "__main__":
    unittest.main()