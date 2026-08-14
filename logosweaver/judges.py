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
