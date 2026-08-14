import unittest

from logosweaver import (
    ExecutionContract, FigureState, JudgeKind, JudgeVerdict,
    LogosWeaverRuntime, ResponseEmitter, ResponseGate, ResponseMode,
    SemanticFigure, Verdict, DialogueResponse,
)


class FixedJudge:
    def __init__(self, kind, verdict):
        self.kind = kind
        self.verdict = verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, self.verdict, rationale="E.1 controlled runtime condition")


def make_contract():
    return ExecutionContract.create(
        preconditions=["fixture condition established"],
        scope="bounded dialogue response",
        required_state=FigureState.EXECUTABLE,
        permitted_actions=["respond"],
        expected_observations=["response recorded"],
        postconditions=["trace preserved"],
        reevaluation_conditions=["runtime condition changes"],
    )


def make_runtime(need_verdict, identity_verdict=Verdict.PASS):
    runtime = LogosWeaverRuntime()
    figure = SemanticFigure("user-a", "fixture-workspace", state=FigureState.EXECUTABLE)
    runtime.register(figure)
    runtime.attach_contract("user-a", make_contract())
    runtime.evaluate_contract(
        "user-a",
        [
            FixedJudge(JudgeKind.NEED_INTEGRITY, need_verdict),
            FixedJudge(JudgeKind.IDENTITY, identity_verdict),
        ],
    )
    return runtime


class DialogueRuntimeE2EV05Tests(unittest.TestCase):
    """Smallest end-to-end E.1 proof: Runtime condition controls emitted response."""

    def test_same_input_different_runtime_condition_changes_emitted_mode(self):
        user_input = "I need a business."  # Same input in both branches.
        gate = ResponseGate()
        emitter = ResponseEmitter()

        unresolved_runtime = make_runtime(Verdict.UNRESOLVED)
        unresolved_permission = gate.evaluate(unresolved_runtime, "user-a")
        unresolved_response = DialogueResponse(
            ResponseMode.CLARIFY,
            "Please clarify what outcome you mean by business.",
            "user-a",
        )
        unresolved_emission = emitter.emit(unresolved_permission, unresolved_response)

        established_runtime = make_runtime(Verdict.PASS)
        established_permission = gate.evaluate(established_runtime, "user-a")
        established_response = DialogueResponse(
            ResponseMode.ALLOW,
            "We can proceed within the established scope.",
            "user-a",
        )
        established_emission = emitter.emit(established_permission, established_response)

        self.assertEqual(unresolved_permission.mode, ResponseMode.CLARIFY)
        self.assertTrue(unresolved_emission.emitted)
        self.assertEqual(established_permission.mode, ResponseMode.ALLOW)
        self.assertTrue(established_emission.emitted)
        self.assertNotEqual(unresolved_permission.mode, established_permission.mode)
        self.assertEqual(user_input, "I need a business.")

    def test_runtime_unresolved_prevents_unsupported_assertive_output(self):
        runtime = make_runtime(Verdict.UNRESOLVED)
        permission = ResponseGate().evaluate(runtime, "user-a")
        response = DialogueResponse(
            ResponseMode.ALLOW,
            "Your true need is definitely to build a one-billion-KRW business.",
            "user-a",
        )
        result = ResponseEmitter().emit(permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_identity_unresolved_allows_reflection_but_not_identity_claim(self):
        runtime = make_runtime(Verdict.PASS, identity_verdict=Verdict.UNRESOLVED)
        permission = ResponseGate().evaluate(runtime, "user-a")
        self.assertEqual(permission.mode, ResponseMode.REFLECT)

        allowed = DialogueResponse(
            ResponseMode.REFLECT,
            "What has been established so far is that this possibility remains under examination.",
            "user-a",
        )
        forbidden = DialogueResponse(
            ResponseMode.ALLOW,
            "This is your established invariant.",
            "user-a",
        )
        emitter = ResponseEmitter()
        self.assertTrue(emitter.emit(permission, allowed).emitted)
        self.assertFalse(emitter.emit(permission, forbidden).emitted)


if __name__ == "__main__":
    unittest.main()
