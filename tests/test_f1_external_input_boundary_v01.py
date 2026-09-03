import json
import unittest
from typing import Any

from logosweaver import (
    ExecutionContract,
    FigureState,
    Lineage,
    LineageRelation,
    LogosWeaverRuntime,
    SemanticFigure,
)


class ExternalInputBoundaryV01Adapter:
    """Test-only adapter for a plain external input payload used at ingress boundary."""

    @staticmethod
    def external_input_payload(
        *,
        figure_id: str,
        workspace_id: str,
        state: str,
        lineage_id: str | None = None,
        trace: list[dict[str, Any]] | None = None,
        execution_contract: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "figure_id": figure_id,
            "workspace_id": workspace_id,
            "state": state,
            "lineage_id": lineage_id,
            "trace": trace or [],
            "execution_contract": execution_contract,
        }


class ExternalInputBoundaryV01Tests(unittest.TestCase):

    def make_runtime(self) -> LogosWeaverRuntime:
        runtime = LogosWeaverRuntime()

        figure = SemanticFigure(
            figure_id="seed-figure",
            workspace_id="seed-workspace",
            state=FigureState.EXECUTABLE,
            execution_contract=ExecutionContract.create(
                scope="seed-scope",
                required_state=FigureState.EXECUTABLE,
                permitted_actions=("observe",),
            ),
        )

        runtime.register(figure)
        runtime.add_lineage(
            Lineage(
                source_figure_id="seed-figure",
                target_figure_id="seed-figure",
                relations=(LineageRelation.DERIVED_FROM,),
            )
        )

        return runtime

    def test_external_input_is_not_a_semanticfigure(self):
        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="external-figure",
            workspace_id="external-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="lineage-1",
            execution_contract={
                "scope": "external-scope",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["execute", "transition"],
            },
        )

        self.assertIsInstance(payload, dict)
        self.assertNotIsInstance(payload, SemanticFigure)
        self.assertNotIn("runtime", payload)
        self.assertNotIn("register", payload)
        self.assertNotIn("attach_contract", payload)

    def test_authority_bearing_fields_do_not_promote_to_runtime_objects(self):
        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="incoming-figure",
            workspace_id="incoming-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="lineage-external",
            execution_contract={
                "scope": "incoming-scope",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["execute", "mutate"],
            },
            trace=[{"event_type": "EXTERNAL_INGRESS", "figure_id": "incoming-figure"}],
        )

        self.assertNotIsInstance(payload, SemanticFigure)
        self.assertNotIsInstance(payload, ExecutionContract)
        self.assertNotIsInstance(payload, Lineage)
        self.assertFalse(any(isinstance(value, (SemanticFigure, ExecutionContract, Lineage, LogosWeaverRuntime)) for value in payload.values()))
        self.assertFalse(any(callable(value) for value in payload.values()))

    def test_runtime_state_is_not_derived_from_external_input_fields(self):
        runtime = self.make_runtime()
        before_figures = dict(runtime.figures)
        before_state = runtime.figures["seed-figure"].state
        before_event_count = len(runtime.events)

        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="incoming-figure",
            workspace_id="ingress-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="lineage-injected",
            execution_contract={
                "scope": "injected-scope",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["execute", "transition"],
            },
            trace=[{"event_type": "EXTERNAL_INGRESS", "figure_id": "incoming-figure"}],
        )

        self.assertNotIn("incoming-figure", runtime.figures)
        self.assertEqual(runtime.figures["seed-figure"].state, before_state)
        self.assertEqual(runtime.figures, before_figures)
        self.assertEqual(len(runtime.events), before_event_count)

        payload["state"] = FigureState.UNRESOLVED.value
        payload["figure_id"] = "incoming-figure"
        payload["workspace_id"] = "override-workspace"

        self.assertNotIn("incoming-figure", runtime.figures)
        self.assertEqual(runtime.figures["seed-figure"].workspace_id, "seed-workspace")
        self.assertEqual(len(runtime.events), before_event_count)

    def test_external_input_cannot_inject_execution_contract_or_permission(self):
        runtime = self.make_runtime()
        before_contract = runtime.figures["seed-figure"].execution_contract
        before_permissions = list(before_contract.permitted_actions) if before_contract else []

        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="seed-figure",
            workspace_id="seed-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="lineage-injected",
            execution_contract={
                "scope": "external-authority",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["register", "transition", "mutate"],
            },
        )

        self.assertIsInstance(payload["execution_contract"], dict)
        self.assertNotIsInstance(payload["execution_contract"], ExecutionContract)
        self.assertNotEqual(payload["execution_contract"]["permitted_actions"], list(before_permissions))
        self.assertEqual(runtime.figures["seed-figure"].execution_contract, before_contract)
        self.assertEqual(runtime.figures["seed-figure"].execution_contract.permitted_actions, tuple(before_permissions))

    def test_external_input_cannot_grant_runtime_register_authority(self):
        runtime = self.make_runtime()
        before_count = len(runtime.figures)
        before_event_count = len(runtime.events)

        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="new-figure",
            workspace_id="new-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="new-lineage",
            execution_contract={
                "scope": "new-scope",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["register"],
            },
        )

        self.assertNotIn("new-figure", runtime.figures)
        self.assertEqual(len(runtime.figures), before_count)
        self.assertEqual(len(runtime.events), before_event_count)
        self.assertNotIn("register", payload)
        self.assertNotIn("attach_contract", payload)

    def test_external_input_mutation_does_not_change_runtime_lineage_trace_event_count(self):
        runtime = self.make_runtime()
        before_lineages = list(runtime.lineages)
        before_trace = tuple(runtime.trace("seed-figure"))
        before_event_count = len(runtime.events)

        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="seed-figure",
            workspace_id="mutated-workspace",
            state=FigureState.UNRESOLVED.value,
            lineage_id="mutated-lineage",
            trace=[{"event_type": "MUTATED_BY_EXTERNAL_INPUT"}],
            execution_contract={
                "scope": "mutated-authority",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["execute", "mutate", "register"],
            },
        )

        payload["figure_id"] = "tampered-figure"
        payload["state"] = FigureState.UNRESOLVED.value
        payload["lineage_id"] = "tampered-lineage"
        payload["trace"].append({"event_type": "AUTHORITY_FORGERY"})

        self.assertEqual(list(runtime.lineages), before_lineages)
        self.assertEqual(tuple(runtime.trace("seed-figure")), before_trace)
        self.assertEqual(len(runtime.events), before_event_count)
        self.assertEqual(runtime.figures["seed-figure"].figure_id, "seed-figure")
        self.assertEqual(runtime.figures["seed-figure"].workspace_id, "seed-workspace")
        self.assertEqual(runtime.figures["seed-figure"].state, FigureState.EXECUTABLE)

    def test_external_input_json_boundary_remains_plain_serializable(self):
        payload = ExternalInputBoundaryV01Adapter.external_input_payload(
            figure_id="json-figure",
            workspace_id="json-workspace",
            state=FigureState.EXECUTABLE.value,
            lineage_id="json-lineage",
            trace=[{"event_type": "EXTERNAL_INGRESS", "figure_id": "json-figure"}],
            execution_contract={
                "scope": "json-scope",
                "required_state": FigureState.EXECUTABLE.value,
                "permitted_actions": ["observe"],
            },
        )

        serialized = json.dumps(payload)
        restored = json.loads(serialized)

        self.assertIsInstance(restored, dict)
        self.assertEqual(set(restored.keys()), {"figure_id", "workspace_id", "state", "lineage_id", "trace", "execution_contract"})
        self.assertNotIn("runtime", restored)
        self.assertNotIn("register", restored)
        self.assertNotIn("callable", restored)


if __name__ == "__main__":
    unittest.main()
