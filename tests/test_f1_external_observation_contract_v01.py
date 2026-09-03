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


class ExternalObservationContractV01Adapter:
    """Test-only adapter that reads Runtime state and emits the v0.1 external observation."""

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


class ExternalObservationContractV01Tests(unittest.TestCase):

    def make_runtime(self) -> LogosWeaverRuntime:
        runtime = LogosWeaverRuntime()

        source = SemanticFigure(
            figure_id="obs-source",
            workspace_id="obs-workspace",
            state=FigureState.EXECUTABLE,
            execution_contract=ExecutionContract.create(
                scope="obs-source-scope",
                required_state=FigureState.EXECUTABLE,
            ),
        )

        figure = SemanticFigure(
            figure_id="obs-figure",
            workspace_id="obs-workspace",
            state=FigureState.EXECUTABLE,
            execution_contract=ExecutionContract.create(
                scope="obs-figure-scope",
                required_state=FigureState.EXECUTABLE,
            ),
        )

        runtime.register(source)
        runtime.register(figure)
        runtime.add_lineage(
            Lineage(
                source_figure_id="obs-source",
                target_figure_id="obs-figure",
                relations=(LineageRelation.DERIVED_FROM,),
            )
        )

        # Fixture-only runtime event creation for test setup. This is not part of the
        # external observation API or any new Runtime boundary capability.
        runtime._event("FIGURE_REGISTERED", figure.figure_id, state=figure.state.value)
        runtime._event("EXECUTION_AUTHORIZED", figure.figure_id, contract_id=figure.execution_contract.contract_id)

        return runtime

    def test_contract_field_closure(self):
        runtime = self.make_runtime()
        observation = ExternalObservationContractV01Adapter.plain_observation(runtime, "obs-figure")

        self.assertEqual(
            set(observation.keys()),
            {"workspace_id", "figure_id", "state", "lineage_id", "trace"},
        )

        self.assertEqual(observation["workspace_id"], "obs-workspace")
        self.assertEqual(observation["figure_id"], "obs-figure")
        self.assertEqual(observation["state"], FigureState.EXECUTABLE.value)
        self.assertIsInstance(observation["lineage_id"], str)
        self.assertEqual(observation["lineage_id"], runtime.lineages[0].lineage_id)
        self.assertIsInstance(observation["trace"], list)
        self.assertTrue(observation["trace"])

    def test_serialization_no_runtime_object_reference(self):
        runtime = self.make_runtime()
        observation = ExternalObservationContractV01Adapter.plain_observation(runtime, "obs-figure")

        self.assertIsInstance(observation, dict)
        self.assertNotIn("runtime", observation)
        self.assertNotIn("figures", observation)
        self.assertNotIn("lineages", observation)
        self.assertNotIn("verdicts", observation)
        self.assertNotIn("execution_contract", observation)
        self.assertNotIn("boundary", observation)
        self.assertNotIn("constraints", observation)
        self.assertFalse(any(isinstance(value, (LogosWeaverRuntime, SemanticFigure, ExecutionContract, Lineage)) for value in observation.values()))

        serialized = json.dumps(observation)
        restored = json.loads(serialized)

        self.assertIsInstance(restored, dict)
        self.assertEqual(set(restored.keys()), {"workspace_id", "figure_id", "state", "lineage_id", "trace"})
        self.assertNotIn("runtime", restored)
        self.assertNotIn("figures", restored)
        self.assertNotIn("lineages", restored)
        self.assertNotIn("verdicts", restored)
        self.assertNotIn("execution_contract", restored)
        self.assertNotIn("boundary", restored)
        self.assertNotIn("constraints", restored)

        for item in restored["trace"]:
            self.assertIsInstance(item, dict)
            self.assertEqual(item["figure_id"], "obs-figure")
            self.assertTrue(
                all(
                    isinstance(value, (str, int, float, bool, dict, list, type(None)))
                    for value in item["payload"].values()
                )
            )

        self.assertTrue(serialized)

    def test_external_observation_mutation_does_not_mutate_runtime(self):
        runtime = self.make_runtime()
        original_figure = runtime.figures["obs-figure"]
        original_state = original_figure.state
        original_lineage_id = runtime.lineages[0].lineage_id
        original_trace = tuple(runtime.trace("obs-figure"))
        original_event_count = len(runtime.events)

        observation = ExternalObservationContractV01Adapter.plain_observation(runtime, "obs-figure")
        observation["figure_id"] = "tampered-figure"
        observation["state"] = FigureState.UNRESOLVED.value
        observation["lineage_id"] = "tampered-lineage"
        observation["trace"].append({"event_type": "MUTATED_BY_OBSERVER"})

        self.assertEqual(runtime.figures["obs-figure"].figure_id, "obs-figure")
        self.assertEqual(runtime.figures["obs-figure"].state, original_state)
        self.assertEqual(runtime.lineages[0].lineage_id, original_lineage_id)
        self.assertEqual(tuple(runtime.trace("obs-figure")), original_trace)
        self.assertEqual(len(runtime.events), original_event_count)
        self.assertEqual(runtime.figures["obs-figure"].workspace_id, "obs-workspace")

    def test_workspace_and_figure_referential_integrity(self):
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

        observation_a = ExternalObservationContractV01Adapter.plain_observation(runtime, "figure-a")
        observation_b = ExternalObservationContractV01Adapter.plain_observation(runtime, "figure-b")

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
