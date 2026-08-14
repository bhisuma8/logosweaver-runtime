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
    conditions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    state: FigureState = FigureState.CANDIDATE
    execution_contract: ExecutionContract | None = None
