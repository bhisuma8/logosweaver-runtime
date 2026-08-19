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


class FixedJudge:
    """Controlled fixture judge for explicit E.2 execution evidence."""

    def __init__(self, kind, verdict):
        self.kind = kind
        self.verdict = verdict

    def evaluate(self, figure, contract, context):
        return JudgeVerdict(
            self.kind,
            self.verdict,
            rationale="E.2 controlled execution-boundary verdict",
        )


def contract():
    return ExecutionContract.create(
        preconditions=["fixture condition established"],
        scope="bounded execution action",
        required_state=FigureState.EXECUTABLE,
        permitted_actions=["execute"],
        expected_observations=["execution recorded"],
        postconditions=["execution boundary preserved"],
        reevaluation_conditions=["runtime condition changes"],
    )


class E2ExecutionBoundaryV05Tests(unittest.TestCase):
    """Minimal E.2 execution-boundary evaluation.

    This slice verifies the frozen Response Gate behavior when a response
    requires execution: missing contract -> STOP, missing authorization
    -> DEFER, and sufficient authorized conditions -> ALLOW.
    """

    FIGURE_ID = "e2-execution-fixture"

    def make_runtime(self, attach_contract=True, evaluate=False):
        runtime = LogosWeaverRuntime()
        figure = SemanticFigure(
            self.FIGURE_ID,
            "e2-execution-workspace",
            state=FigureState.EXECUTABLE,
        )
        runtime.register(figure)

        if attach_contract:
            runtime.attach_contract(self.FIGURE_ID, contract())

        if evaluate:
            runtime.evaluate_contract(
                self.FIGURE_ID,
                [
                    FixedJudge(JudgeKind.EXECUTABLE, Verdict.PASS),
                    FixedJudge(JudgeKind.NEED_INTEGRITY, Verdict.PASS),
                    FixedJudge(JudgeKind.WORKSPACE_INTEGRITY, Verdict.PASS),
                    FixedJudge(JudgeKind.IDENTITY, Verdict.PASS),
                ],
            )

        return runtime

    def test_execution_required_without_contract_stops(self):
        runtime = self.make_runtime(attach_contract=False)

        permission = ResponseGate().evaluate(
            runtime,
            self.FIGURE_ID,
            requires_execution=True,
        )

        self.assertEqual(permission.mode, ResponseMode.STOP)
        self.assertEqual(permission.reason, "EXECUTION_CONTRACT_MISSING")

    def test_execution_required_with_contract_but_without_authorization_defers(self):
        runtime = self.make_runtime(attach_contract=True, evaluate=False)

        permission = ResponseGate().evaluate(
            runtime,
            self.FIGURE_ID,
            requires_execution=True,
        )

        self.assertEqual(permission.mode, ResponseMode.DEFER)
        self.assertEqual(permission.reason, "EXECUTION_NOT_AUTHORIZED")

    def test_execution_required_with_authorized_conditions_allows(self):
        runtime = self.make_runtime(attach_contract=True, evaluate=True)

        permission = ResponseGate().evaluate(
            runtime,
            self.FIGURE_ID,
            requires_execution=True,
        )

        self.assertEqual(permission.mode, ResponseMode.ALLOW)
        self.assertEqual(permission.reason, "CONDITIONS_SUFFICIENT")


if __name__ == "__main__":
    unittest.main()
