# LogosWeaver Runtime v0.5.4 — Canonical Injection Snapshot

> This snapshot preserves the supplied v0.5.4 FULL SOURCE baseline, applies only the E.5-approved `SemanticCondition` refinement to `models.py` and `__init__.py`, and includes the behavioral evaluation and lifecycle evidence tests from E.2/E.3 through F.5. The pre-refinement FULL SOURCE is not duplicated as a separate repository artifact.

## 01 — Original v0.5.4 Injection Baseline with Approved Source Refinement

1. README.md
2. logosweaver folder/
    __init__.py
    models.py
    runtime.py
    judges.py
    response_gate.py


3. tests folder/
    test_runtime_v04.py
    test_response_gate_v05.py
    test_user_a_fixture_v05.py
    test_response_output_boundary_v05.py
    test_response_emitter_v05.py
    test_dialogue_runtime_e2e_v05.py
    
    `Add E.2 and E.3 behavioral evaluation tests`
    test_e2_behavioral_v05.py
    test_e2_execution_boundary_v05.py
    test_e2_trace_observability_v05.py
    test_e3_figure_scoped_boundary_v05.py
      
    `Add F.1-F.2 boundary evidence & continuity records`
    test_f1_external_boundary_v05.py  
    test_f1_external_input_boundary_v01.py  
    test_f1_external_observation_boundary_v01.py 
    test_f1_external_observation_contract_v01.py
     
    `Add F.3-F.4 lifecycle evidence and freeze records`
    test_f3_birth_fixture_v01.py
    test_f4_executable_fixture_v01.py  
    test_f4_executed_state_transition_fixture_v01.py 
    test_f4_execution_authorization_fixture_v01.py 
    test_f4_life_fixture_v01.py 
    test_f4_observed_state_transition_fixture_v01.py
    test_f4_resonance_candidate_fixture_v01.py

    `Add F.5 bounded Runtime MVP evidence reconstruction fixture`
    test_f5_runtime_mvp_lineage_fixture_v01.py

----
## LogosWeaver Runtime v0.5.4

  

This is a refinement of the v0.5 Dialogue Runtime / Response Gate slice.

  

### Added in this slice

  

- End-to-end E.1 behavioral fixture connecting Runtime judgment → Response Gate → Response Permission → ResponseEmitter.

- Demonstrates the required condition-dependent behavior:

  same user input + different Runtime state/evidence → different permitted response mode.

- Demonstrates that an unresolved Runtime condition blocks an assertive `ALLOW` response.

- Demonstrates that unresolved Identity permits `REFLECT` but blocks an identity claim expressed as `ALLOW`.

  

### Preserved

  

- v0.4 SemanticFigure, state machine, Event/Trace, Lineage

- ExecutionContract

- 3+1 Judge separation

- PASS / FAIL / UNRESOLVED semantics

- STOP preservation

- v0.5 ResponseMode and ResponsePermission

- ResponseOutputBoundary

- DialogueResponse and ResponseEmitter

  

### Scope discipline

  

No Semantic Figure, Runtime State Machine, Event Model, Lineage Model, Execution Contract, or 3+1 Judge redesign was introduced.

  

The E.1 fixture uses only the documented User A conceptual progression; it does not invent missing verbatim dialogue.

  

### Tests

  

```powershell

python -m unittest discover -s tests -v

```

  

Historical E.1 baseline: 32 tests were expected to pass.

This is not a current aggregate test-count claim. The E.2/E.3 tests below were synchronized subsequently, and the existing E.3 record preserves a separate bookkeeping discrepancy (33 tests executed vs the earlier 32-test baseline).

----
## [File] `logosweaver/__init__.py`

```python

"""LogosWeaver Runtime v0.5."""

from .judges import ExecutableJudge, IdentityJudge, NeedIntegrityJudge, UnresolvedJudge, WorkspaceIntegrityJudge

from .models import ExecutionContract, FigureState, JudgeKind, JudgeVerdict, Lineage, LineageRelation, SemanticCondition, SemanticFigure, Verdict

from .response_gate import DialogueResponse, ResponseAdmission, ResponseEmitter, ResponseGate, ResponseMode, ResponseOutputBoundary, ResponsePermission, ResponseEmission

from .runtime import LogosWeaverRuntime, RuntimeErrorState

__all__ = ["ExecutableJudge","ExecutionContract","FigureState","IdentityJudge","JudgeKind","JudgeVerdict",

           "Lineage","LineageRelation","LogosWeaverRuntime","NeedIntegrityJudge","RuntimeErrorState",

           "SemanticCondition","SemanticFigure","UnresolvedJudge","Verdict","WorkspaceIntegrityJudge",

           "DialogueResponse","ResponseAdmission","ResponseEmitter","ResponseGate","ResponseMode","ResponseOutputBoundary","ResponsePermission","ResponseEmission"]
```


----
## [File] `logosweaver/judges.py`

```python
"""3+1 Judge interfaces. No implementation here decides semantic truth."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing import Mapping, Any

from .models import ExecutionContract, JudgeKind, JudgeVerdict, SemanticFigure, Verdict

  

class Judge(ABC):

    kind: JudgeKind

    @abstractmethod

    def evaluate(self, figure: SemanticFigure, contract: ExecutionContract,

                 context: Mapping[str, Any]) -> JudgeVerdict:

        """Return a declared assessment; do not silently convert uncertainty."""

  

class ExecutableJudge(Judge):

    kind = JudgeKind.EXECUTABLE

  

class NeedIntegrityJudge(Judge):

    kind = JudgeKind.NEED_INTEGRITY

  

class WorkspaceIntegrityJudge(Judge):

    kind = JudgeKind.WORKSPACE_INTEGRITY

  

class IdentityJudge(Judge):

    kind = JudgeKind.IDENTITY

  

class UnresolvedJudge(Judge):

    """Safe default until a domain-specific judge is supplied."""

    def __init__(self, kind: JudgeKind) -> None:

        self.kind = kind

    def evaluate(self, figure: SemanticFigure, contract: ExecutionContract,

                 context: Mapping[str, Any]) -> JudgeVerdict:

        return JudgeVerdict(judge=self.kind, verdict=Verdict.UNRESOLVED,

                            rationale="No semantic judge implementation supplied.")
                            
```

----
## [File] `logosweaver/models.py`

```python
"""Stable data structures for LogosWeaver Runtime v0.4."""

  

from __future__ import annotations

from dataclasses import dataclass, field

from enum import Enum

from typing import Any, Mapping, Sequence

from uuid import uuid4

  

class FigureState(str, Enum):

    CANDIDATE = "CANDIDATE"

    BOUNDARY_REVIEW = "BOUNDARY_REVIEW"

    RESONANCE_CANDIDATE = "RESONANCE_CANDIDATE"

    EXECUTABLE = "EXECUTABLE"

    EXECUTED = "EXECUTED"

    OBSERVED = "OBSERVED"

    IDENTITY_REVIEW = "IDENTITY_REVIEW"

    MUTATED = "MUTATED"

    LINEAGE_ACTIVE = "LINEAGE_ACTIVE"

    UNRESOLVED = "UNRESOLVED"

  

class Verdict(str, Enum):

    PASS = "PASS"

    FAIL = "FAIL"

    UNRESOLVED = "UNRESOLVED"

  

class JudgeKind(str, Enum):

    EXECUTABLE = "EXECUTABLE"

    NEED_INTEGRITY = "NEED_INTEGRITY"

    WORKSPACE_INTEGRITY = "WORKSPACE_INTEGRITY"

    IDENTITY = "IDENTITY"

  

class LineageRelation(str, Enum):

    DERIVED_FROM = "DERIVED_FROM"

    RESONATES_WITH = "RESONATES_WITH"

    MUTATED_FROM = "MUTATED_FROM"

    REINSTANTIATED_FROM = "REINSTANTIATED_FROM"

    CONVERGED_WITH = "CONVERGED_WITH"

    CONTESTED_WITH = "CONTESTED_WITH"

  

@dataclass(frozen=True)

class ExecutionContract:

    """A declared execution boundary; its content is never auto-interpreted."""

    contract_id: str = field(default_factory=lambda: str(uuid4()))

    preconditions: tuple[str, ...] = ()

    scope: str = ""

    required_state: FigureState = FigureState.EXECUTABLE

    permitted_actions: tuple[str, ...] = ()

    expected_observations: tuple[str, ...] = ()

    postconditions: tuple[str, ...] = ()

    reevaluation_conditions: tuple[str, ...] = ()

  

    @classmethod

    def create(cls, *, preconditions: Sequence[str] = (), scope: str = "",

               required_state: FigureState = FigureState.EXECUTABLE,

               permitted_actions: Sequence[str] = (),

               expected_observations: Sequence[str] = (),

               postconditions: Sequence[str] = (),

               reevaluation_conditions: Sequence[str] = ()) -> "ExecutionContract":

        return cls(preconditions=tuple(preconditions), scope=scope,

                   required_state=required_state, permitted_actions=tuple(permitted_actions),

                   expected_observations=tuple(expected_observations),

                   postconditions=tuple(postconditions),

                   reevaluation_conditions=tuple(reevaluation_conditions))

  

@dataclass(frozen=True)

class JudgeVerdict:

    judge: JudgeKind

    verdict: Verdict

    rationale: str = ""

    observations: tuple[str, ...] = ()

    evidence: Mapping[str, Any] = field(default_factory=dict)

  

@dataclass(frozen=True)

class SemanticCondition:

    expression: str


@dataclass(frozen=True)

class Lineage:

    source_figure_id: str

    target_figure_id: str

    relations: tuple[LineageRelation, ...]

    lineage_id: str = field(default_factory=lambda: str(uuid4()))

  

@dataclass

class SemanticFigure:

    figure_id: str

    workspace_id: str

    boundary: str = ""

    distinctions: tuple[str, ...] = ()

    conditions: tuple[SemanticCondition, ...] = ()

    constraints: tuple[str, ...] = ()

    state: FigureState = FigureState.CANDIDATE

    execution_contract: ExecutionContract | None = None
    
```


----
## [File] `logosweaver/response_gate.py`

```python
"""Minimal v0.5 Dialogue Runtime / Response Gate.

  

The gate consumes Runtime results. It does not evaluate semantic truth and does not

act as a fifth Judge.

"""

from __future__ import annotations

  

from dataclasses import dataclass

from enum import Enum

  

from .models import JudgeKind, Verdict

from .runtime import LogosWeaverRuntime

  
  

class ResponseMode(str, Enum):

    ALLOW = "ALLOW"

    CLARIFY = "CLARIFY"

    REFLECT = "REFLECT"

    DEFER = "DEFER"

    STOP = "STOP"

  
  

@dataclass(frozen=True)

class ResponsePermission:

    mode: ResponseMode

    reason: str

    figure_id: str

  
  

class ResponseGate:

    """Translate already-recorded Runtime conditions into response permission."""

  

    def evaluate(

        self,

        runtime: LogosWeaverRuntime,

        figure_id: str,

        *,

        requires_execution: bool = False,

    ) -> ResponsePermission:

        figure = runtime.figures[figure_id]

        trace = runtime.trace(figure_id)

        verdicts = runtime.verdicts.get(figure_id, ())

  

        # Explicit Runtime STOP is never upgraded to ALLOW.

        stop_events = [event for event in trace if event.event_type == "STOP"]

        if stop_events:

            reason = stop_events[-1].payload.get("reason", "RUNTIME_STOP")

            if reason != "JUDGE_UNRESOLVED":

                return ResponsePermission(ResponseMode.STOP, str(reason), figure_id)

  

        # A missing contract is an execution boundary, not a conversational guess.

        if requires_execution and figure.execution_contract is None:

            return ResponsePermission(

                ResponseMode.STOP,

                "EXECUTION_CONTRACT_MISSING",

                figure_id,

            )

  

        unresolved = [v for v in verdicts if v.verdict is Verdict.UNRESOLVED]

        if unresolved:

            kinds = {v.judge for v in unresolved}

            if JudgeKind.NEED_INTEGRITY in kinds:

                return ResponsePermission(

                    ResponseMode.CLARIFY,

                    "NEED_INTEGRITY_UNRESOLVED",

                    figure_id,

                )

            if JudgeKind.IDENTITY in kinds:

                return ResponsePermission(

                    ResponseMode.REFLECT,

                    "IDENTITY_UNRESOLVED",

                    figure_id,

                )

            return ResponsePermission(

                ResponseMode.DEFER,

                "RUNTIME_UNRESOLVED",

                figure_id,

            )

  

        if any(v.verdict is Verdict.FAIL for v in verdicts):

            return ResponsePermission(

                ResponseMode.DEFER,

                "RUNTIME_JUDGMENT_FAIL",

                figure_id,

            )

  

        if requires_execution and not any(

            event.event_type == "EXECUTION_AUTHORIZED" for event in trace

        ):

            return ResponsePermission(

                ResponseMode.DEFER,

                "EXECUTION_NOT_AUTHORIZED",

                figure_id,

            )

  

        if verdicts and all(v.verdict is Verdict.PASS for v in verdicts):

            return ResponsePermission(ResponseMode.ALLOW, "CONDITIONS_SUFFICIENT", figure_id)

  

        return ResponsePermission(ResponseMode.DEFER, "RUNTIME_CONDITION_INSUFFICIENT", figure_id)

  

@dataclass(frozen=True)

class ResponseAdmission:

    """Output-boundary decision for a proposed response mode.

  

    The admission layer checks only the already-derived permission. It does not

    inspect or reinterpret response text, and therefore does not become a

    semantic judge.

    """

  

    admitted: bool

    requested_mode: ResponseMode

    permitted_mode: ResponseMode

    reason: str

    figure_id: str

  
  

class ResponseOutputBoundary:

    """Minimal boundary between Response Permission and generated output."""

  

    def admit(

        self,

        permission: ResponsePermission,

        requested_mode: ResponseMode,

    ) -> ResponseAdmission:

        if permission.mode is ResponseMode.STOP:

            return ResponseAdmission(

                False, requested_mode, permission.mode,

                "RESPONSE_STOPPED", permission.figure_id,

            )

  

        if requested_mode is permission.mode:

            return ResponseAdmission(

                True, requested_mode, permission.mode,

                "RESPONSE_MODE_PERMITTED", permission.figure_id,

            )

  

        return ResponseAdmission(

            False, requested_mode, permission.mode,

            "RESPONSE_MODE_NOT_PERMITTED", permission.figure_id,

        )

  

@dataclass(frozen=True)

class DialogueResponse:

    """A proposed conversational output carrying its declared response mode.

  

    The payload is opaque to the Runtime. This object binds generated content to

    the response permission without asking the Runtime to judge semantic truth.

    """

  

    mode: ResponseMode

    content: str

    figure_id: str

  
  

@dataclass(frozen=True)

class ResponseEmission:

    """Result of admitting a proposed DialogueResponse at the output boundary."""

  

    emitted: bool

    response: DialogueResponse

    reason: str

  
  

class ResponseEmitter:

    """Minimal final handoff from Response Permission to conversational output."""

  

    def emit(

        self,

        permission: ResponsePermission,

        response: DialogueResponse,

    ) -> ResponseEmission:

        if response.figure_id != permission.figure_id:

            return ResponseEmission(False, response, "FIGURE_ID_MISMATCH")

  

        admission = ResponseOutputBoundary().admit(permission, response.mode)

        if not admission.admitted:

            return ResponseEmission(False, response, admission.reason)

  

        return ResponseEmission(True, response, "RESPONSE_EMITTED")
        
```


----
## [File] `logosweaver/runtime.py`

```python

"""Event-preserving runtime orchestration for v0.4."""

from __future__ import annotations

from dataclasses import dataclass, field

from datetime import datetime, timezone

from typing import Any, Iterable, Mapping

from uuid import uuid4

from .judges import Judge

from .models import ExecutionContract, FigureState, JudgeKind, JudgeVerdict, Lineage, SemanticFigure, Verdict

  

class RuntimeErrorState(ValueError):

    pass

  

@dataclass(frozen=True)

class RuntimeEvent:

    event_id: str

    event_type: str

    figure_id: str

    payload: Mapping[str, Any]

    occurred_at: str

  

@dataclass

class LogosWeaverRuntime:

    figures: dict[str, SemanticFigure] = field(default_factory=dict)

    events: list[RuntimeEvent] = field(default_factory=list)

    lineages: list[Lineage] = field(default_factory=list)

    verdicts: dict[str, list[JudgeVerdict]] = field(default_factory=dict)

  

    _transitions = {

        FigureState.CANDIDATE: {FigureState.BOUNDARY_REVIEW, FigureState.UNRESOLVED},

        FigureState.BOUNDARY_REVIEW: {FigureState.RESONANCE_CANDIDATE, FigureState.UNRESOLVED},

        FigureState.RESONANCE_CANDIDATE: {FigureState.EXECUTABLE, FigureState.UNRESOLVED},

        FigureState.EXECUTABLE: {FigureState.EXECUTED, FigureState.UNRESOLVED},

        FigureState.EXECUTED: {FigureState.OBSERVED, FigureState.UNRESOLVED},

        FigureState.OBSERVED: {FigureState.IDENTITY_REVIEW, FigureState.UNRESOLVED},

        FigureState.IDENTITY_REVIEW: {FigureState.MUTATED, FigureState.LINEAGE_ACTIVE, FigureState.UNRESOLVED},

        FigureState.MUTATED: {FigureState.LINEAGE_ACTIVE, FigureState.UNRESOLVED},

        FigureState.LINEAGE_ACTIVE: {FigureState.UNRESOLVED},

        FigureState.UNRESOLVED: set(),

    }

  

    def _event(self, event_type: str, figure_id: str, **payload: Any) -> RuntimeEvent:

        event = RuntimeEvent(str(uuid4()), event_type, figure_id, payload,

                             datetime.now(timezone.utc).isoformat())

        self.events.append(event)

        return event

  

    def register(self, figure: SemanticFigure) -> None:

        if figure.figure_id in self.figures:

            raise RuntimeErrorState(f"Figure already registered: {figure.figure_id}")

        self.figures[figure.figure_id] = figure

        self._event("FIGURE_REGISTERED", figure.figure_id, state=figure.state.value)

  

    def transition(self, figure_id: str, target: FigureState) -> None:

        figure = self.figures[figure_id]

        if target not in self._transitions[figure.state]:

            raise RuntimeErrorState(f"Invalid transition: {figure.state.value} -> {target.value}")

        previous = figure.state

        figure.state = target

        self._event("STATE_TRANSITIONED", figure_id, previous=previous.value, target=target.value)

  

    def attach_contract(self, figure_id: str, contract: ExecutionContract) -> None:

        figure = self.figures[figure_id]

        figure.execution_contract = contract

        self._event("EXECUTION_CONTRACT_ATTACHED", figure_id, contract_id=contract.contract_id)

  

    def add_lineage(self, lineage: Lineage) -> None:

        if lineage.source_figure_id not in self.figures or lineage.target_figure_id not in self.figures:

            raise RuntimeErrorState("Lineage figures must be registered.")

        self.lineages.append(lineage)

        self._event("LINEAGE_RECORDED", lineage.target_figure_id,

                    lineage_id=lineage.lineage_id,

                    source_figure_id=lineage.source_figure_id,

                    relations=[relation.value for relation in lineage.relations])

  

    def evaluate_contract(self, figure_id: str, judges: Iterable[Judge],

                          context: Mapping[str, Any] | None = None) -> tuple[JudgeVerdict, ...]:

        figure = self.figures[figure_id]

        contract = figure.execution_contract

        if contract is None:

            raise RuntimeErrorState("An execution contract is required before evaluation.")

        if figure.state != contract.required_state:

            raise RuntimeErrorState(

                f"Contract requires {contract.required_state.value}; figure is {figure.state.value}."

            )

        results: list[JudgeVerdict] = []

        seen: set[JudgeKind] = set()

        for judge in judges:

            if judge.kind in seen:

                raise RuntimeErrorState(f"Duplicate judge: {judge.kind.value}")

            result = judge.evaluate(figure, contract, context or {})

            if result.judge != judge.kind:

                raise RuntimeErrorState("Judge returned a verdict for a different responsibility.")

            seen.add(judge.kind)

            results.append(result)

            self._event("JUDGE_EVALUATED", figure_id, judge=result.judge.value,

                        verdict=result.verdict.value, rationale=result.rationale,

                        observations=list(result.observations))

        self.verdicts.setdefault(figure_id, []).extend(results)

        if any(result.verdict is Verdict.UNRESOLVED for result in results):

            self._event("STOP", figure_id, reason="JUDGE_UNRESOLVED",

                        judges=[r.judge.value for r in results if r.verdict is Verdict.UNRESOLVED])

            self.transition(figure_id, FigureState.UNRESOLVED)

        elif any(result.verdict is Verdict.FAIL for result in results):

            self._event("EXECUTION_BLOCKED", figure_id, reason="JUDGE_FAIL")

        else:

            self._event("EXECUTION_AUTHORIZED", figure_id, contract_id=contract.contract_id)

        return tuple(results)

  

    def trace(self, figure_id: str) -> tuple[RuntimeEvent, ...]:

        return tuple(event for event in self.events if event.figure_id == figure_id)
        
```

----
## `test_dialogue_runtime_e2e_v05.py`

```python
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
```

----
## `test_response_emitter_v05.py`

```python
import unittest

from logosweaver import (
    DialogueResponse,
    ResponseEmitter,
    ResponseMode,
    ResponsePermission,
)


class ResponseEmitterV05Tests(unittest.TestCase):
    def setUp(self):
        self.emitter = ResponseEmitter()
        self.permission = ResponsePermission(
            ResponseMode.CLARIFY,
            "NEED_INTEGRITY_UNRESOLVED",
            "f-1",
        )

    def test_permitted_response_is_emitted(self):
        response = DialogueResponse(ResponseMode.CLARIFY, "Please clarify the intended scope.", "f-1")
        result = self.emitter.emit(self.permission, response)
        self.assertTrue(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_EMITTED")
        self.assertEqual(result.response.content, response.content)

    def test_unpermitted_allow_response_is_not_emitted(self):
        response = DialogueResponse(ResponseMode.ALLOW, "The user's true need is X.", "f-1")
        result = self.emitter.emit(self.permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_stop_permission_blocks_output(self):
        permission = ResponsePermission(ResponseMode.STOP, "EXPLICIT_RUNTIME_STOP", "f-1")
        response = DialogueResponse(ResponseMode.CLARIFY, "We should pause here.", "f-1")
        result = self.emitter.emit(permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "RESPONSE_STOPPED")

    def test_figure_identity_is_not_crossed_at_output_boundary(self):
        response = DialogueResponse(ResponseMode.CLARIFY, "Clarify this.", "f-2")
        result = self.emitter.emit(self.permission, response)
        self.assertFalse(result.emitted)
        self.assertEqual(result.reason, "FIGURE_ID_MISMATCH")


if __name__ == "__main__":
    unittest.main()

```

----
## `test_response_gate_v05.py`

```python
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

```

----
## `test_response_output_boundary_v05.py`

```python
import unittest

from logosweaver import ResponseMode, ResponseOutputBoundary, ResponsePermission


class ResponseOutputBoundaryV05Tests(unittest.TestCase):
    def setUp(self):
        self.boundary = ResponseOutputBoundary()
        self.permission = ResponsePermission(
            ResponseMode.CLARIFY,
            "NEED_INTEGRITY_UNRESOLVED",
            "f-1",
        )

    def test_permitted_mode_is_admitted(self):
        admission = self.boundary.admit(self.permission, ResponseMode.CLARIFY)
        self.assertTrue(admission.admitted)
        self.assertEqual(admission.permitted_mode, ResponseMode.CLARIFY)

    def test_unpermitted_allow_is_rejected(self):
        admission = self.boundary.admit(self.permission, ResponseMode.ALLOW)
        self.assertFalse(admission.admitted)
        self.assertEqual(admission.reason, "RESPONSE_MODE_NOT_PERMITTED")

    def test_stop_rejects_every_requested_mode(self):
        permission = ResponsePermission(ResponseMode.STOP, "EXPLICIT_RUNTIME_STOP", "f-1")
        for mode in ResponseMode:
            admission = self.boundary.admit(permission, mode)
            self.assertFalse(admission.admitted)
            self.assertEqual(admission.reason, "RESPONSE_STOPPED")

    def test_identity_reflection_permission_does_not_admit_allow(self):
        permission = ResponsePermission(
            ResponseMode.REFLECT,
            "IDENTITY_UNRESOLVED",
            "f-1",
        )
        admission = self.boundary.admit(permission, ResponseMode.ALLOW)
        self.assertFalse(admission.admitted)
        self.assertEqual(admission.permitted_mode, ResponseMode.REFLECT)


if __name__ == "__main__":
    unittest.main()

```

----
## `test_runtime_v04.py`

```python
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
    
```

----
## `test_user_a_fixture_v05.py`

```python
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
    
```


----

# 02 — Phase E.2 / E.3 Evaluation Tests Added After the Original FULL SOURCE

## `test_e2_behavioral_v05.py`

```python
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
```

## `test_e2_execution_boundary_v05.py`

```python
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
```

## `test_e2_trace_observability_v05.py`

```python
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
```

## `test_e3_figure_scoped_boundary_v05.py`

```python
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
```

----
# 03 — F.5 Closure / Continuity Synchronization

**Phase:** F.5 — Runtime MVP Evidence Reconstruction  
**Runtime Baseline:** v0.5.4  
**Runtime Status:** Behavioral Freeze  
**F.5 Status:** PASS  
**Continuity:** F.3 = Birth → F.4 = Life / lifecycle-Lineage boundary measurement → F.5 = bounded Runtime MVP evidence reconstruction → F.6 = repository integration / pre-boundary research

F.5 established a bounded evidence reconstruction using existing Runtime primitives and test-controlled composition. No production bridge was required for this proof.

Authoritative fixture:

```text
tests/test_f5_runtime_mvp_lineage_fixture_v01.py
```

The fixture is test-controlled, uses explicit lifecycle transitions and explicit Lineage composition, and is not a Mutation Engine or Identity Engine. Its essential evidence chain is:

```text
Figure A
→ registration
→ Boundary / Resonance / Executable
→ ExecutionContract
→ PASS Judges
→ EXECUTION_AUTHORIZED
→ EXECUTED
→ OBSERVED
→ IDENTITY_REVIEW
→ MUTATED state evidence
→ explicit Figure B
→ explicit A→B Lineage
→ runtime.add_lineage()
→ LINEAGE_RECORDED
→ Figure-scoped Trace
```

This evidence preserves the following boundary: explicit state is not an automatic semantic engine; Figure B is explicitly constructed; `MUTATED_FROM` is representational Lineage; `add_lineage()` records Lineage but does not perform mutation; and `LINEAGE_RECORDED` is recording evidence, not semantic preservation.

Judge / STOP remains inherited continuity evidence. The F.5 fixture itself uses PASS-only Judges and does not directly exercise a STOP path.

Reported results:

```text
F.5 fixture: reported PASS
Full suite: reported 78 tests PASS
```

The repository contains no durable execution record proving that all 78 tests were executed successfully. These therefore remain reported results, not repository-recorded execution evidence.

F.5 production modification = 0. It adds no production API, model, event, state, ontology, or semantic engine. The earlier E.5 `SemanticCondition` representation refinement is not an F.5 modification.

F.5 does not establish an Identity Engine, Mutation Engine, automatic execution, automatic observation, semantic Identity evaluation, automatic Mutation, automatic resulting-Figure derivation, automatic preservation, RAG, Lounge integration, LLM integration, or a public API/deployment.

F.5 is a closure / continuity phase, not a Runtime release. The v0.5.4 Runtime remains behaviorally frozen.

