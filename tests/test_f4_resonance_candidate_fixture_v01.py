import unittest

from logosweaver import (
    FigureState,
    LogosWeaverRuntime,
    SemanticFigure,
)


class F4ResonanceCandidateFixtureTests(unittest.TestCase):

    def test_boundary_review_enters_resonance_candidate(self):

        figure = SemanticFigure(
            "f3-birth-001",
            "f3-fixture-workspace",
            distinctions=("A", "B"),
            constraints=("A에 대해서만 실행을 허용한다",),
            state=FigureState.CANDIDATE,
        )

        runtime = LogosWeaverRuntime()
        runtime.register(figure)

        runtime.transition(
            figure.figure_id,
            FigureState.BOUNDARY_REVIEW,
        )
        runtime.transition(
            figure.figure_id,
            FigureState.RESONANCE_CANDIDATE,
        )

        self.assertEqual(
            figure.state,
            FigureState.RESONANCE_CANDIDATE,
        )

        trace = runtime.trace(figure.figure_id)

        self.assertEqual(
            [event.event_type for event in trace],
            [
                "FIGURE_REGISTERED",
                "STATE_TRANSITIONED",
                "STATE_TRANSITIONED",
            ],
        )

        self.assertEqual(
            trace[1].payload["previous"],
            FigureState.CANDIDATE.value,
        )
        self.assertEqual(
            trace[1].payload["target"],
            FigureState.BOUNDARY_REVIEW.value,
        )
        self.assertEqual(
            trace[2].payload["previous"],
            FigureState.BOUNDARY_REVIEW.value,
        )
        self.assertEqual(
            trace[2].payload["target"],
            FigureState.RESONANCE_CANDIDATE.value,
        )


if __name__ == "__main__":
    unittest.main()