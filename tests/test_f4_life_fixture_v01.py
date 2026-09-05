import unittest

from logosweaver import (
    FigureState,
    LogosWeaverRuntime,
    SemanticFigure,
)


class F4LifeFixtureTests(unittest.TestCase):

    def test_birth_figure_enters_runtime_life(self):

        figure = SemanticFigure(
            "f3-birth-001",
            "f3-fixture-workspace",
            distinctions=("A", "B"),
            constraints=("A에 대해서만 실행을 허용한다",),
            state=FigureState.CANDIDATE,
        )

        runtime = LogosWeaverRuntime()
        runtime.register(figure)

        self.assertEqual(
            figure.state,
            FigureState.CANDIDATE,
        )

        runtime.transition(
            figure.figure_id,
            FigureState.BOUNDARY_REVIEW,
        )

        self.assertEqual(
            figure.state,
            FigureState.BOUNDARY_REVIEW,
        )

        trace = runtime.trace(figure.figure_id)

        self.assertEqual(
            [event.event_type for event in trace],
            [
                "FIGURE_REGISTERED",
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


if __name__ == "__main__":
    unittest.main()