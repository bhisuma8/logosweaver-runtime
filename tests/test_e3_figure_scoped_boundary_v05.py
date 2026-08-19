"""
E.3 — Figure-Scoped Response Boundary Evaluation

Engineering Question:
    Can v0.5.4 reliably preserve Figure-scoped response permission
    when multiple SemanticFigures coexist, without modifying the
    frozen Runtime semantics?

Evaluation scope:
    - Two independent SemanticFigures coexist in one workspace.
    - Each Figure has its own ResponsePermission.
    - A permission may emit only the response belonging to the same Figure.
    - Cross-Figure emission must be rejected.
    - No Re-entry, Figure Fork, Mutation, or Lineage semantics are introduced.

E3-EQ1 result:
    PASS — 4/4 behavioral cases passed.

Observed matrix:
    Figure A permission -> Figure A response : PASS
    Figure B permission -> Figure B response : PASS
    Figure A permission -> Figure B response : REJECT / FIGURE_ID_MISMATCH
    Figure B permission -> Figure A response : REJECT / FIGURE_ID_MISMATCH

Regression result:
    33 tests executed, 0 failures.

Note:
    The v0.5.4 README records a 32-test baseline. The supplied source
    artifact's discovered test inventory differed by one test; this
    bookkeeping discrepancy did not affect the E3-EQ1 result and was
    not modified as part of this evaluation.

Architectural boundary:
    This test establishes only Figure-scoped response isolation under
    coexisting independent Figures. It does NOT establish semantics for:
    - Same-Figure Re-entry
    - Figure Fork
    - Mutation-related identity changes
    - Lineage effects on permission scope

Git status:
    This file is an E.3 evaluation artifact. No production Runtime
    semantics are modified by this test.
"""

import unittest

from logosweaver import (
    DialogueResponse,
    ResponseEmitter,
    ResponseMode,
    ResponsePermission,
)


class FigureScopedBoundaryV05Tests(unittest.TestCase):
    def setUp(self):
        self.emitter = ResponseEmitter()

        self.permission_a = ResponsePermission(
            ResponseMode.CLARIFY,
            "FIGURE_A_PERMISSION",
            "figure-a",
        )

        self.permission_b = ResponsePermission(
            ResponseMode.ALLOW,
            "FIGURE_B_PERMISSION",
            "figure-b",
        )

        self.response_a = DialogueResponse(
            ResponseMode.CLARIFY,
            "Response belonging to Figure A.",
            "figure-a",
        )

        self.response_b = DialogueResponse(
            ResponseMode.ALLOW,
            "Response belonging to Figure B.",
            "figure-b",
        )

    def test_figure_a_permission_emits_figure_a_response(self):
        result = self.emitter.emit(
            self.permission_a,
            self.response_a,
        )

        self.assertTrue(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_EMITTED")
        self.assertEqual(result.response.figure_id, "figure-a")

    def test_figure_b_permission_emits_figure_b_response(self):
        result = self.emitter.emit(
            self.permission_b,
            self.response_b,
        )

        self.assertTrue(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_EMITTED")
        self.assertEqual(result.response.figure_id, "figure-b")

    def test_figure_a_permission_rejects_figure_b_response(self):
        result = self.emitter.emit(
            self.permission_a,
            self.response_b,
        )

        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "FIGURE_ID_MISMATCH")

    def test_figure_b_permission_rejects_figure_a_response(self):
        result = self.emitter.emit(
            self.permission_b,
            self.response_a,
        )

        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "FIGURE_ID_MISMATCH")


if __name__ == "__main__":
    unittest.main()
