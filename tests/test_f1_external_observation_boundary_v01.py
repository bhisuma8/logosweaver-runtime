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


def _contains_runtime_handle(value: Any) -> bool:
    if callable(value):
        return True
    if isinstance(value, dict):
        return any(_contains_runtime_handle(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_runtime_handle(item) for item in value)
    return False


class ExternalObservationBoundaryV01Adapter:
    """Test-only adapter that projects Runtime state to the external observation boundary."""

    @staticmethod
    def plain_observation(runtime: LogosWeaverRuntime, figure_id: str) -> dict[str, Any]:
        figure = runtime.figures[figure_id]
        lineage_id = None

        for lineage in runtime.lineages:
            if lineage.target_figure_id == figure_id or lineage.source_figure_id == figure_id:
                lineage_id = lineage.lineage_id
                break

        return {
            "workspace_id": figure.workspace_id,
            "figure_id": figure.figure_id,
            "state": figure.state.value,
            "lineage_id": lineage_id,
            "trace": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "figure_id": event.figure_id,
                    "payload": dict(event.payload),
                    "occurred_at": event.occurred_at,
                }
                for event in runtime.trace(figure_id)
            ],
        }


class ExternalObservationBoundaryV01Tests(unittest.TestCase):

    def make_runtime(self) -> LogosWeaverRuntime:
        runtime = LogosWeaverRuntime()

        source = SemanticFigure(
            figure_id="boundary-source",
            workspace_id="boundary-workspace",
            state=FigureState.EXECUTABLE,
            execution_contract=ExecutionContract.create(
                scope="source-scope",
                required_state=FigureState.EXECUTABLE,
            ),
        )

        figure = SemanticFigure(
            figure_id="boundary-figure",
            workspace_id="boundary-workspace",
            state=FigureState.EXECUTABLE,
            execution_contract=ExecutionContract.create(
                scope="figure-scope",
                required_state=FigureState.EXECUTABLE,
            ),
        )

        runtime.register(source)
        runtime.register(figure)
        runtime.add_lineage(
            Lineage(
                source_figure_id="boundary-source",
                target_figure_id="boundary-figure",
                relations=(LineageRelation.DERIVED_FROM,),
            )
        )

        # Fixture-only event creation for setup. This is not part of the external
        # observation API and does not add runtime execution authority.
        runtime._event("FIGURE_REGISTERED", figure.figure_id, state=figure.state.value)
        runtime._event("EXECUTION_AUTHORIZED", figure.figure_id, contract_id=figure.execution_contract.contract_id)

        return runtime

    def test_external_observation_contract_has_exactly_five_fields(self):
        runtime = self.make_runtime()
        observation = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "boundary-figure")

        self.assertEqual(
            set(observation.keys()),
            {"workspace_id", "figure_id", "state", "lineage_id", "trace"},
        )
        self.assertNotIn("boundary", observation)
        self.assertNotIn("distinctions", observation)
        self.assertNotIn("conditions", observation)
        self.assertNotIn("constraints", observation)
        self.assertNotIn("execution_contract", observation)

    def test_observation_contains_no_runtime_objects_or_authority_handles(self):
        runtime = self.make_runtime()
        observation = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "boundary-figure")

        self.assertNotIn("runtime", observation)
        self.assertNotIn("figures", observation)
        self.assertNotIn("lineages", observation)
        self.assertNotIn("verdicts", observation)
        self.assertNotIn("execution_contract", observation)

        self.assertFalse(any(isinstance(value, (LogosWeaverRuntime, SemanticFigure, ExecutionContract, Lineage)) for value in observation.values()))
        self.assertFalse(_contains_runtime_handle(observation))

        self.assertFalse(any(isinstance(value, (LogosWeaverRuntime, SemanticFigure, ExecutionContract, Lineage)) for item in observation["trace"] for value in item.values()))
        self.assertFalse(any(callable(value) for item in observation["trace"] for value in item.values()))

    def test_observation_is_json_serializable_boundary(self):
        runtime = self.make_runtime()
        observation = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "boundary-figure")

        serialized = json.dumps(observation)
        restored = json.loads(serialized)

        self.assertIsInstance(restored, dict)
        self.assertEqual(set(restored.keys()), {"workspace_id", "figure_id", "state", "lineage_id", "trace"})
        self.assertNotIn("execution_contract", restored)
        self.assertNotIn("boundary", restored)
        self.assertNotIn("constraints", restored)

        for item in restored["trace"]:
            self.assertIsInstance(item, dict)
            self.assertEqual(item["figure_id"], "boundary-figure")
            self.assertTrue(
                all(
                    isinstance(value, (str, int, float, bool, dict, list, type(None)))
                    for value in item["payload"].values()
                )
            )

        self.assertTrue(serialized)

    def test_observation_mutation_does_not_mutate_runtime(self):
        runtime = self.make_runtime()
        original_figure = runtime.figures["boundary-figure"]
        original_state = original_figure.state
        original_lineage_id = runtime.lineages[0].lineage_id
        original_trace = tuple(runtime.trace("boundary-figure"))
        original_event_count = len(runtime.events)

        observation = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "boundary-figure")
        observation["figure_id"] = "tampered-figure"
        observation["state"] = FigureState.UNRESOLVED.value
        observation["lineage_id"] = "tampered-lineage"
        observation["trace"].append({"event_type": "MUTATED_BY_OBSERVER"})

        self.assertEqual(runtime.figures["boundary-figure"].figure_id, "boundary-figure")
        self.assertEqual(runtime.figures["boundary-figure"].state, original_state)
        self.assertEqual(runtime.lineages[0].lineage_id, original_lineage_id)
        self.assertEqual(tuple(runtime.trace("boundary-figure")), original_trace)
        self.assertEqual(len(runtime.events), original_event_count)

    def test_observation_has_no_runtime_reentry_handle(self):
        runtime = self.make_runtime()
        observation = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "boundary-figure")

        self.assertNotIn("runtime", observation)
        self.assertNotIn("execute", observation)
        self.assertNotIn("transition", observation)
        self.assertNotIn("mutate", observation)
        self.assertNotIn("reenter", observation)
        self.assertFalse(_contains_runtime_handle(observation))

        for item in observation["trace"]:
            self.assertFalse(_contains_runtime_handle(item))

    def test_workspace_and_figure_identity_are_isolated_in_observation(self):
        runtime = LogosWeaverRuntime()

        figure_a = SemanticFigure(
            figure_id="figure-a",
            workspace_id="workspace-alpha",
            state=FigureState.EXECUTABLE,
        )
        figure_b = SemanticFigure(
            figure_id="figure-b",
            workspace_id="workspace-beta",
            state=FigureState.EXECUTABLE,
        )

        runtime.register(figure_a)
        runtime.register(figure_b)

        observation_a = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "figure-a")
        observation_b = ExternalObservationBoundaryV01Adapter.plain_observation(runtime, "figure-b")

        self.assertEqual(observation_a["workspace_id"], "workspace-alpha")
        self.assertEqual(observation_b["workspace_id"], "workspace-beta")
        self.assertEqual(observation_a["figure_id"], "figure-a")
        self.assertEqual(observation_b["figure_id"], "figure-b")
        self.assertNotEqual(observation_a["workspace_id"], observation_b["workspace_id"])
        self.assertNotEqual(observation_a["figure_id"], observation_b["figure_id"])
        self.assertNotEqual(observation_a["figure_id"], "figure-b")
        self.assertNotEqual(observation_b["figure_id"], "figure-a")


if __name__ == "__main__":
    unittest.main()
