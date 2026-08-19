import unittest
from logosweaver import ExecutionContract, FigureState, JudgeKind, JudgeVerdict, LogosWeaverRuntime, SemanticFigure, Verdict

class FixedJudge:
    def __init__(self, kind, verdict): self.kind, self.verdict = kind, verdict
    def evaluate(self, figure, contract, context):
        return JudgeVerdict(self.kind, self.verdict, rationale='E.2 trace observability fixture')

def contract():
    return ExecutionContract.create(
        preconditions=['fixture condition established'], scope='bounded runtime evaluation',
        required_state=FigureState.EXECUTABLE, permitted_actions=['execute'],
        expected_observations=['evaluation recorded'], postconditions=['trace preserved'],
        reevaluation_conditions=['runtime condition changes'])

class E2TraceObservabilityV05Tests(unittest.TestCase):
    FIGURE_ID='e2-trace-fixture'
    def make_runtime(self, verdict=Verdict.PASS):
        runtime=LogosWeaverRuntime(); figure=SemanticFigure(self.FIGURE_ID,'e2-trace-workspace',state=FigureState.EXECUTABLE)
        runtime.register(figure); runtime.attach_contract(self.FIGURE_ID,contract())
        runtime.evaluate_contract(self.FIGURE_ID,[FixedJudge(JudgeKind.EXECUTABLE,verdict)],context={'fixture':'E2_TRACE'})
        return runtime
    def test_trace_preserves_registration_contract_and_judge_events(self):
        event_types=[e.event_type for e in self.make_runtime().trace(self.FIGURE_ID)]
        self.assertEqual(event_types,['FIGURE_REGISTERED','EXECUTION_CONTRACT_ATTACHED','JUDGE_EVALUATED','EXECUTION_AUTHORIZED'])
    def test_judge_event_preserves_verdict_and_observation_context(self):
        event=next(e for e in self.make_runtime().trace(self.FIGURE_ID) if e.event_type=='JUDGE_EVALUATED')
        self.assertEqual(event.payload['judge'],JudgeKind.EXECUTABLE.value); self.assertEqual(event.payload['verdict'],Verdict.PASS.value)
        self.assertEqual(event.payload['rationale'],'E.2 trace observability fixture'); self.assertEqual(event.payload['observations'],[])
    def test_unresolved_evaluation_preserves_stop_and_state_transition(self):
        runtime=self.make_runtime(Verdict.UNRESOLVED); trace=runtime.trace(self.FIGURE_ID)
        self.assertEqual([e.event_type for e in trace],['FIGURE_REGISTERED','EXECUTION_CONTRACT_ATTACHED','JUDGE_EVALUATED','STOP','STATE_TRANSITIONED'])
        self.assertEqual(runtime.figures[self.FIGURE_ID].state,FigureState.UNRESOLVED)
        stop=next(e for e in trace if e.event_type=='STOP'); self.assertEqual(stop.payload['reason'],'JUDGE_UNRESOLVED')
        transition=next(e for e in trace if e.event_type=='STATE_TRANSITIONED'); self.assertEqual(transition.payload['target'],FigureState.UNRESOLVED.value)
    def test_trace_is_scoped_to_requested_figure(self):
        runtime=self.make_runtime(); other=SemanticFigure('e2-other-figure','e2-other-workspace',state=FigureState.EXECUTABLE); runtime.register(other)
        trace=runtime.trace(self.FIGURE_ID); self.assertTrue(trace); self.assertTrue(all(e.figure_id==self.FIGURE_ID for e in trace)); self.assertFalse(any(e.figure_id=='e2-other-figure' for e in trace))
if __name__=='__main__': unittest.main()
