import unittest

from logosweaver import FigureState, LogosWeaverRuntime, SemanticFigure


class F4ExecutableFixtureTests(unittest.TestCase):

    def test_resonance_candidate_becomes_executable(self):
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

        self.assertEqual(figure.state, FigureState.EXECUTABLE)

        trace = runtime.trace(figure.figure_id)
        self.assertEqual(
            [event.event_type for event in trace],
            [
                "FIGURE_REGISTERED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
            ],
        )

        transitions = trace[1:]
        self.assertEqual(
            [(event.payload["previous"], event.payload["target"]) for event in transitions],
            [
                (FigureState.CANDIDATE.value, FigureState.BOUNDARY_REVIEW.value),
                (FigureState.BOUNDARY_REVIEW.value, FigureState.RESONANCE_CANDIDATE.value),
                (FigureState.RESONANCE_CANDIDATE.value, FigureState.EXECUTABLE.value),
            ],
        )


if __name__ == "__main__":
    unittest.main()