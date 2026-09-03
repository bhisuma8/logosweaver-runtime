import unittest

from logosweaver import (
    FigureState,
    LogosWeaverRuntime,
    SemanticFigure,
)


class F1ExternalBoundaryV05Tests(unittest.TestCase):

    def make_two_figure_runtime(self):
        runtime = LogosWeaverRuntime()

        figure_a = SemanticFigure(
            "f1-figure-a",
            "f1-workspace",
            state=FigureState.EXECUTABLE,
        )

        figure_b = SemanticFigure(
            "f1-figure-b",
            "f1-workspace",
            state=FigureState.EXECUTABLE,
        )

        runtime.register(figure_a)
        runtime.register(figure_b)

        return runtime

    def test_referential_integrity_of_figure_scoped_trace(self):
        runtime = self.make_two_figure_runtime()

        trace_a = runtime.trace("f1-figure-a")
        trace_b = runtime.trace("f1-figure-b")

        # Each Figure must have its own registration evidence.
        self.assertTrue(trace_a)
        self.assertTrue(trace_b)

        # A's trace contains A events only.
        self.assertTrue(
            all(
                event.figure_id == "f1-figure-a"
                for event in trace_a
            )
        )

        # B's trace contains B events only.
        self.assertTrue(
            all(
                event.figure_id == "f1-figure-b"
                for event in trace_b
            )
        )

        # Cross-Figure events must not appear.
        self.assertFalse(
            any(
                event.figure_id == "f1-figure-b"
                for event in trace_a
            )
        )

        self.assertFalse(
            any(
                event.figure_id == "f1-figure-a"
                for event in trace_b
            )
        )

    def test_terminal_observation_does_not_mutate_runtime(self):
        runtime = LogosWeaverRuntime()

        figure = SemanticFigure(
            "f1-terminal",
            "f1-terminal-workspace",
            state=FigureState.UNRESOLVED,
        )

        runtime.register(figure)

        before_state = runtime.figures["f1-terminal"].state
        before_trace = tuple(
            runtime.trace("f1-terminal")
        )
        before_event_count = len(runtime.events)

        first = runtime.trace("f1-terminal")
        second = runtime.trace("f1-terminal")
        third = runtime.trace("f1-terminal")

        # Repeated observation must be observationally stable.
        self.assertEqual(first, second)
        self.assertEqual(second, third)

        # Runtime state must remain unchanged.
        self.assertEqual(
            runtime.figures["f1-terminal"].state,
            before_state,
        )

        # The observed trace must remain unchanged.
        self.assertEqual(
            tuple(runtime.trace("f1-terminal")),
            before_trace,
        )

        # Observation must not create Runtime events.
        self.assertEqual(
            len(runtime.events),
            before_event_count,
        )

        # Terminal state must remain terminal.
        self.assertEqual(
            runtime.figures["f1-terminal"].state,
            FigureState.UNRESOLVED,
        )


if __name__ == "__main__":
    unittest.main()