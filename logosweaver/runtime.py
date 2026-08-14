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
