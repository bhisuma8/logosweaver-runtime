import unittest

from logosweaver import FigureState, LogosWeaverRuntime, SemanticFigure


class F3SecondBirthFixtureTests(unittest.TestCase):

    def test_second_birth_fixture_registers_candidate(self):
        material = {
            "material_id": "m-f3-002",
            "raw_text": "이번 작업에서는 X와 Y를 구분하고 X만 실행 대상으로 둔다.",
        }
        evidence = {
            "material_id": material["material_id"],
            "figure_id": "f3-birth-002",
        }

        figure = SemanticFigure(
            evidence["figure_id"],
            "f3-fixture-workspace-002",
            distinctions=("X", "Y"),
            constraints=("X만 실행 대상으로 둔다",),
        )

        runtime = LogosWeaverRuntime()
        runtime.register(figure)

        self.assertEqual(figure.state, FigureState.CANDIDATE)
        self.assertIn(evidence["figure_id"], runtime.figures)
        self.assertEqual(
            runtime.figures[evidence["figure_id"]].figure_id,
            evidence["figure_id"],
        )

        trace = runtime.trace(evidence["figure_id"])
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0].event_type, "FIGURE_REGISTERED")
        self.assertEqual(trace[0].figure_id, evidence["figure_id"])


if __name__ == "__main__":
    unittest.main()
