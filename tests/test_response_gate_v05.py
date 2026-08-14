import unittest

from logosweaver import (
    ExecutionContract, FigureState, JudgeKind, JudgeVerdict, LogosWeaverRuntime,
    SemanticFigure, Verdict, ResponseGate, ResponseMode,
)
from logosweaver.runtime import RuntimeErrorState


class FixedJudge:
    def __init__(self, kind, verdict):
        self.kind, self.verdict = kind, verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, self.verdict, rationale="explicit test verdict")


def contract():
    return ExecutionContract.create(
        preconditions=["condition established"],
        scope="bounded dialogue operation",
        required_state=FigureState.EXECUTABLE,
        permitted_actions=["respond"],
        expected_observations=["response recorded"],
        postconditions=["trace preserved"],
        reevaluation_conditions=["condition changes"],
    )


class ResponseGateV05Tests(unittest.TestCase):
    def setUp(self):
        self.gate = ResponseGate()

    def runtime_with(self, verdicts):
        runtime = LogosWeaverRuntime()
        figure = SemanticFigure("f-1", "workspace-1", state=FigureState.EXECUTABLE)
        runtime.register(figure)
        runtime.attach_contract("f-1", contract())
        runtime.evaluate_contract(
            "f-1",
            [FixedJudge(kind, verdict) for kind, verdict in verdicts],
        )
        return runtime

    def test_all_pass_allows_response(self):
        runtime = self.runtime_with([
            (JudgeKind.EXECUTABLE, Verdict.PASS),
            (JudgeKind.NEED_INTEGRITY, Verdict.PASS),
            (JudgeKind.WORKSPACE_INTEGRITY, Verdict.PASS),
            (JudgeKind.IDENTITY, Verdict.PASS),
        ])
        permission = self.gate.evaluate(runtime, "f-1", requires_execution=True)
        self.assertEqual(permission.mode, ResponseMode.ALLOW)

    def test_need_unresolved_requires_clarification(self):
        runtime = self.runtime_with([(JudgeKind.NEED_INTEGRITY, Verdict.UNRESOLVED)])
        permission = self.gate.evaluate(runtime, "f-1")
        self.assertEqual(permission.mode, ResponseMode.CLARIFY)
        self.assertNotEqual(permission.mode, ResponseMode.ALLOW)

    def test_identity_unresolved_reflects_without_assertion(self):
        runtime = self.runtime_with([(JudgeKind.IDENTITY, Verdict.UNRESOLVED)])
        permission = self.gate.evaluate(runtime, "f-1")
        self.assertEqual(permission.mode, ResponseMode.REFLECT)

    def test_other_unresolved_defers(self):
        runtime = self.runtime_with([(JudgeKind.WORKSPACE_INTEGRITY, Verdict.UNRESOLVED)])
        permission = self.gate.evaluate(runtime, "f-1")
        self.assertEqual(permission.mode, ResponseMode.DEFER)

    def test_fail_defers_and_does_not_authorize(self):
        runtime = self.runtime_with([(JudgeKind.IDENTITY, Verdict.FAIL)])
        permission = self.gate.evaluate(runtime, "f-1")
        self.assertEqual(permission.mode, ResponseMode.DEFER)

    def test_explicit_stop_cannot_become_allow(self):
        runtime = self.runtime_with([(JudgeKind.NEED_INTEGRITY, Verdict.PASS)])
        runtime._event("STOP", "f-1", reason="EXPLICIT_RUNTIME_STOP")
        permission = self.gate.evaluate(runtime, "f-1")
        self.assertEqual(permission.mode, ResponseMode.STOP)

    def test_missing_execution_contract_stops_execution_bound_response(self):
        runtime = LogosWeaverRuntime()
        runtime.register(SemanticFigure("f-1", "workspace-1", state=FigureState.EXECUTABLE))
        permission = self.gate.evaluate(runtime, "f-1", requires_execution=True)
        self.assertEqual(permission.mode, ResponseMode.STOP)

    def test_same_input_different_runtime_conditions_yield_different_permissions(self):
        allow_runtime = self.runtime_with([(JudgeKind.NEED_INTEGRITY, Verdict.PASS)])
        unresolved_runtime = self.runtime_with([(JudgeKind.NEED_INTEGRITY, Verdict.UNRESOLVED)])
        self.assertEqual(
            self.gate.evaluate(allow_runtime, "f-1").mode,
            ResponseMode.ALLOW,
        )
        self.assertEqual(
            self.gate.evaluate(unresolved_runtime, "f-1").mode,
            ResponseMode.CLARIFY,
        )


if __name__ == "__main__":
    unittest.main()
