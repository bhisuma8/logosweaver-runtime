import unittest

from logosweaver import (
    ExecutionContract,
    FigureState,
    JudgeKind,
    JudgeVerdict,
    LogosWeaverRuntime,
    ResponseGate,
    ResponseMode,
    SemanticFigure,
    Verdict,
)
from logosweaver.response_gate import DialogueResponse, ResponseEmitter


class FixedJudge:
    """Controlled fixture judge; supplies explicit Runtime evidence."""

    def __init__(self, kind, verdict):
        self.kind = kind
        self.verdict = verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(
            self.kind,
            self.verdict,
            rationale="E.2 controlled fixture verdict",
        )


def contract():
    return ExecutionContract.create(
        preconditions=["fixture condition established"],
        scope="bounded dialogue response",
        required_state=FigureState.EXECUTABLE,
        permitted_actions=["respond"],
        expected_observations=["response recorded"],
        postconditions=["trace preserved"],
        reevaluation_conditions=["runtime condition changes"],
    )


class E2BehavioralFixtureV05Tests(unittest.TestCase):
    """Minimal E.2 behavioral evaluation slice.

    The fixture keeps the conceptual input identity constant and changes
    only the supplied Runtime evidence. It evaluates the frozen v0.5
    Response Gate and Output Boundary; it does not evaluate response text.
    """

    FIGURE_ID = "e2-fixture"
    INPUT_ID = "same-controlled-input"

    def make_runtime(self, need_verdict, identity_verdict=Verdict.PASS):
        runtime = LogosWeaverRuntime()
        figure = SemanticFigure(
            self.FIGURE_ID,
            "e2-fixture-workspace",
            state=FigureState.EXECUTABLE,
        )
        runtime.register(figure)
        runtime.attach_contract(self.FIGURE_ID, contract())
        runtime.evaluate_contract(
            self.FIGURE_ID,
            [
                FixedJudge(JudgeKind.NEED_INTEGRITY, need_verdict),
                FixedJudge(JudgeKind.IDENTITY, identity_verdict),
            ],
            context={"input_id": self.INPUT_ID},
        )
        return runtime

    def test_same_input_with_need_unresolved_requires_clarify(self):
        runtime = self.make_runtime(Verdict.UNRESOLVED)

        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        self.assertEqual(permission.mode, ResponseMode.CLARIFY)
        self.assertNotEqual(permission.mode, ResponseMode.ALLOW)

    def test_same_input_with_identity_unresolved_requires_reflect(self):
        runtime = self.make_runtime(
            Verdict.PASS,
            identity_verdict=Verdict.UNRESOLVED,
        )

        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        self.assertEqual(permission.mode, ResponseMode.REFLECT)
        self.assertNotEqual(permission.mode, ResponseMode.ALLOW)

    def test_same_input_with_relevant_conditions_passed_allows(self):
        runtime = self.make_runtime(Verdict.PASS)

        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        self.assertEqual(permission.mode, ResponseMode.ALLOW)

    def test_same_input_changes_permission_when_runtime_evidence_changes(self):
        gate = ResponseGate()

        unresolved = self.make_runtime(Verdict.UNRESOLVED)
        identity_unresolved = self.make_runtime(
            Verdict.PASS,
            identity_verdict=Verdict.UNRESOLVED,
        )
        established = self.make_runtime(Verdict.PASS)

        self.assertEqual(
            gate.evaluate(unresolved, self.FIGURE_ID).mode,
            ResponseMode.CLARIFY,
        )
        self.assertEqual(
            gate.evaluate(identity_unresolved, self.FIGURE_ID).mode,
            ResponseMode.REFLECT,
        )
        self.assertEqual(
            gate.evaluate(established, self.FIGURE_ID).mode,
            ResponseMode.ALLOW,
        )

    def test_clarify_permission_rejects_allow_candidate(self):
        runtime = self.make_runtime(Verdict.UNRESOLVED)
        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        response = DialogueResponse(
            ResponseMode.ALLOW,
            "assertive candidate",
            self.FIGURE_ID,
        )
        result = ResponseEmitter().emit(permission, response)

        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_reflect_permission_rejects_allow_candidate(self):
        runtime = self.make_runtime(
            Verdict.PASS,
            identity_verdict=Verdict.UNRESOLVED,
        )
        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        response = DialogueResponse(
            ResponseMode.ALLOW,
            "identity assertion candidate",
            self.FIGURE_ID,
        )
        result = ResponseEmitter().emit(permission, response)

        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_allow_permission_admits_allow_candidate(self):
        runtime = self.make_runtime(Verdict.PASS)
        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        response = DialogueResponse(
            ResponseMode.ALLOW,
            "permitted candidate",
            self.FIGURE_ID,
        )
        result = ResponseEmitter().emit(permission, response)

        self.assertTrue(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_EMITTED")

    def test_explicit_stop_remains_stop_and_rejects_candidate(self):
        runtime = self.make_runtime(Verdict.PASS)
        runtime._event(
            "STOP",
            self.FIGURE_ID,
            reason="EXPLICIT_RUNTIME_STOP",
        )

        permission = ResponseGate().evaluate(runtime, self.FIGURE_ID)

        self.assertEqual(permission.mode, ResponseMode.STOP)

        response = DialogueResponse(
            ResponseMode.CLARIFY,
            "attempted continuation",
            self.FIGURE_ID,
        )
        result = ResponseEmitter().emit(permission, response)

        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_STOPPED")


if __name__ == "__main__":
    unittest.main()
