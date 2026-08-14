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
