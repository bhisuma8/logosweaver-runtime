import unittest

from logosweaver import (
    ExecutionContract, FigureState, JudgeKind, JudgeVerdict,
    LogosWeaverRuntime, ResponseGate, ResponseMode, SemanticFigure, Verdict,
)


class FixedJudge:
    def __init__(self, kind, verdict):
        self.kind = kind
        self.verdict = verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, self.verdict, rationale="controlled fixture verdict")


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


class UserAControlledFixtureV05Tests(unittest.TestCase):
    """State fixture derived only from the documented User A progression.

    It intentionally does not reproduce missing verbatim dialogue text.
    """

    def make_runtime(self, need_verdict, identity_verdict=Verdict.PASS):
        runtime = LogosWeaverRuntime()
        figure = SemanticFigure("user-a", "fixture-workspace", state=FigureState.EXECUTABLE)
        runtime.register(figure)
        runtime.attach_contract("user-a", contract())
        runtime.evaluate_contract(
            "user-a",
            [
                FixedJudge(JudgeKind.NEED_INTEGRITY, need_verdict),
                FixedJudge(JudgeKind.IDENTITY, identity_verdict),
            ],
        )
        return runtime

    def test_initial_business_request_does_not_force_final_need(self):
        runtime = self.make_runtime(Verdict.UNRESOLVED)
        permission = ResponseGate().evaluate(runtime, "user-a")
        self.assertEqual(permission.mode, ResponseMode.CLARIFY)

    def test_capital_requirement_clarified_as_approximate_condition(self):
        runtime = self.make_runtime(Verdict.PASS)
        permission = ResponseGate().evaluate(runtime, "user-a")
        self.assertEqual(permission.mode, ResponseMode.ALLOW)

    def test_identity_or_axiom_validation_remaining_unresolved_prevents_assertion(self):
        runtime = self.make_runtime(Verdict.PASS, identity_verdict=Verdict.UNRESOLVED)
        permission = ResponseGate().evaluate(runtime, "user-a")
        self.assertEqual(permission.mode, ResponseMode.REFLECT)
        self.assertNotEqual(permission.mode, ResponseMode.ALLOW)

    def test_same_input_label_changes_permission_with_runtime_condition(self):
        unresolved = self.make_runtime(Verdict.UNRESOLVED)
        established = self.make_runtime(Verdict.PASS)
        gate = ResponseGate()
        self.assertEqual(gate.evaluate(unresolved, "user-a").mode, ResponseMode.CLARIFY)
        self.assertEqual(gate.evaluate(established, "user-a").mode, ResponseMode.ALLOW)


if __name__ == "__main__":
    unittest.main()
