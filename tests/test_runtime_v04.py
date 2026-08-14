import unittest

  

from logosweaver import (

    ExecutionContract, FigureState, JudgeKind, JudgeVerdict, Lineage,

    LineageRelation, LogosWeaverRuntime, SemanticFigure, Verdict,

)

from logosweaver.judges import ExecutableJudge, IdentityJudge, NeedIntegrityJudge, WorkspaceIntegrityJudge

from logosweaver.runtime import RuntimeErrorState

  
  

class FixedJudge:

    def __init__(self, kind, verdict): self.kind, self.verdict = kind, verdict

    def evaluate(self, figure, contract, context):

        return JudgeVerdict(self.kind, self.verdict, rationale="explicit test verdict")

  
  

class RuntimeV04Tests(unittest.TestCase):

    def setUp(self):

        self.runtime = LogosWeaverRuntime()

        self.figure = SemanticFigure("f-1", "workspace-1", state=FigureState.EXECUTABLE)

        self.runtime.register(self.figure)

        self.contract = ExecutionContract.create(

            preconditions=["consent recorded"], scope="one bounded experiment",

            required_state=FigureState.EXECUTABLE, permitted_actions=["observe"],

            expected_observations=["event recorded"], postconditions=["trace preserved"],

            reevaluation_conditions=["condition changes"],

        )

        self.runtime.attach_contract("f-1", self.contract)

  

    def test_contract_preserves_all_specification_fields(self):

        self.assertEqual(self.contract.preconditions, ("consent recorded",))

        self.assertEqual(self.contract.scope, "one bounded experiment")

        self.assertEqual(self.contract.permitted_actions, ("observe",))

        self.assertEqual(self.contract.reevaluation_conditions, ("condition changes",))

  

    def test_passes_authorize_without_auto_execution(self):

        judges = [FixedJudge(kind, Verdict.PASS) for kind in JudgeKind]

        self.runtime.evaluate_contract("f-1", judges)

        self.assertEqual(self.figure.state, FigureState.EXECUTABLE)

        self.assertIn("EXECUTION_AUTHORIZED", [e.event_type for e in self.runtime.trace("f-1")])

  

    def test_fail_blocks_but_preserves_state_and_verdict(self):

        self.runtime.evaluate_contract("f-1", [FixedJudge(JudgeKind.IDENTITY, Verdict.FAIL)])

        self.assertEqual(self.figure.state, FigureState.EXECUTABLE)

        self.assertEqual(self.runtime.verdicts["f-1"][0].verdict, Verdict.FAIL)

        self.assertIn("EXECUTION_BLOCKED", [e.event_type for e in self.runtime.trace("f-1")])

  

    def test_unresolved_emits_stop_and_preserves_evidence(self):

        result = self.runtime.evaluate_contract("f-1", [FixedJudge(JudgeKind.NEED_INTEGRITY, Verdict.UNRESOLVED)])

        self.assertEqual(result[0].verdict, Verdict.UNRESOLVED)

        self.assertEqual(self.figure.state, FigureState.UNRESOLVED)

        self.assertEqual([e.event_type for e in self.runtime.trace("f-1")][-2:], ["STOP", "STATE_TRANSITIONED"])

  

    def test_judge_responsibilities_are_distinct(self):

        self.assertEqual(ExecutableJudge.kind, JudgeKind.EXECUTABLE)

        self.assertEqual(NeedIntegrityJudge.kind, JudgeKind.NEED_INTEGRITY)

        self.assertEqual(WorkspaceIntegrityJudge.kind, JudgeKind.WORKSPACE_INTEGRITY)

        self.assertEqual(IdentityJudge.kind, JudgeKind.IDENTITY)

  

    def test_required_state_is_enforced_without_semantic_interpretation(self):

        self.figure.state = FigureState.CANDIDATE

        with self.assertRaises(RuntimeErrorState):

            self.runtime.evaluate_contract("f-1", [FixedJudge(JudgeKind.EXECUTABLE, Verdict.PASS)])

  

    def test_duplicate_judge_is_rejected(self):

        with self.assertRaises(RuntimeErrorState):

            self.runtime.evaluate_contract("f-1", [FixedJudge(JudgeKind.IDENTITY, Verdict.PASS), FixedJudge(JudgeKind.IDENTITY, Verdict.PASS)])

  

    def test_lineage_is_recorded_alongside_v04_contracts(self):

        child = SemanticFigure("f-2", "workspace-1")

        self.runtime.register(child)

        self.runtime.add_lineage(Lineage("f-1", "f-2", (LineageRelation.DERIVED_FROM, LineageRelation.RESONATES_WITH)))

        self.assertEqual(len(self.runtime.lineages), 1)

        self.assertEqual(self.runtime.lineages[0].relations[1], LineageRelation.RESONATES_WITH)

  

    def test_invalid_transition_remains_rejected(self):

        with self.assertRaises(RuntimeErrorState):

            self.runtime.transition("f-1", FigureState.OBSERVED)

  
  

if __name__ == "__main__":

    unittest.main()


