from typing import Optional, List, Dict, Any, Callable
import os
import hashlib
import json
import time

from honeyhive.sdk import HoneyHive
from honeyhive.models import components
from honeyhive import HoneyHiveTracer
from concurrent.futures import ThreadPoolExecutor
import collections

class Evaluation:
    """This class is for automated honeyhive evaluation with tracing"""

    def __init__(
        self,
        hh_api_key: str = None,
        hh_project: str = None,
        name: str = None,
        function: Optional[Callable] = None,
        dataset: Optional[List[Dict[str, Any]]] = None,
        evaluators: Optional[List[Any]] = None,
        dataset_id: Optional[str] = None,
    ):
        self.hh_api_key = hh_api_key or os.environ["HH_API_KEY"]
        self.hh_project = hh_project or os.environ["HH_PROJECT"]
        self.eval_name: str = name
        self.hh_dataset_id: str = dataset_id
        self.dataset = dataset
        self.client_side_evaluators = evaluators or []
        self.status: str = "pending"

        self._validate_requirements()
        self.hhai = HoneyHive(bearer_auth=self.hh_api_key)
        self.hh_dataset = self._load_dataset()
        self.func_to_evaluate: Callable = function

        # self.runs = (
        #     runs or len(self.hh_dataset.datapoints)
        #     if self.hh_dataset
        #     else len(query_list) if query_list else 0
        # )

        # session ids of each run in a thread-safe collection
        self.evaluation_session_ids: collections.deque = collections.deque()

        # run response
        self.eval_run: Optional[components.CreateRunResponse] = None
        # disable auto tracing
        self.disable_auto_tracing = True
        # generated id for external datasets
        # TODO: large dataset optimization
        self.external_dataset_id: str = (
            self._generate_hash(json.dumps(dataset)) if dataset else None
        )

    def _validate_requirements(self) -> None:
        """Sanity check of requirements for HoneyHive evaluations and tracing."""
        if not self.hh_api_key:
            raise Exception(
                "Honeyhive API key not found. Please set 'hh_api_key' to initiate Honeyhive Tracer. Cannot run Evaluation"
            )
        if not self.hh_project:
            raise Exception(
                "Honeyhive Project not found. Please set 'hh_project' to initiate Honeyhive Tracer. Cannot run Evaluation"
            )
        if not self.eval_name:
            raise Exception(
                "Evaluation name not found. Please set 'name' to initiate Honeyhive Evaluation."
            )
        if not self.hh_dataset_id and not self.dataset:
            raise Exception(
                "No valid 'dataset_id' or 'dataset' found. Please provide one to iterate the evaluation over."
            )

    def _generate_hash(self, input_string: str) -> str:
        hash_object = hashlib.md5(input_string.encode("utf-8"))
        return f"EXT-{hash_object.hexdigest()[:24]}"

    def _load_dataset(self) -> Optional[Any]:
        """Private function to acquire Honeyhive dataset based on dataset_id."""
        if not self.hh_dataset_id:
            return None
        try:
            dataset = self.hhai.datasets.get_datasets(
                project=self.hh_project,
                dataset_id=self.hh_dataset_id,
            )
            if (
                dataset
                and dataset.object.testcases
                and len(dataset.object.testcases) > 0
            ):
                return dataset.object.testcases[0]
        except Exception:
            raise RuntimeError(
                f"No dataset found with id - {self.hh_dataset_id} for project - {self.hh_project}"
            )

    # ------------------------------------------------------------

    def _add_trace_metadata(
        self,
        evaluation_output: Optional[Any],
        run_id: int,
        hh: HoneyHiveTracer,
        metrics: Optional[Dict[str, Any]] = None,
    ):
        """Private function to enrich the session data post flow completion."""
        try:
            tracing_metadata = {"run_id": self.eval_run.run_id}
            if self.hh_dataset:
                tracing_metadata["datapoint_id"] = self.hh_dataset.datapoints[run_id]
                tracing_metadata["dataset_id"] = self.hh_dataset_id
            if self.external_dataset_id:
                tracing_metadata["datapoint_id"] = self._generate_hash(
                    json.dumps(self.dataset[run_id])
                )
                tracing_metadata["dataset_id"] = self.external_dataset_id

            if not isinstance(evaluation_output, dict):
                evaluation_output = {"output": evaluation_output}

            hh.enrich_session(
                metadata=tracing_metadata,
                outputs=evaluation_output
            )
        except Exception as e:
            print(f"Error adding trace metadata: {e}")

    def _run_evaluators(
        self, inputs: Optional[Dict[str, Any]], evaluation_output: Optional[Any]
    ):
        """Private function to run evaluators and collect metrics."""
        metrics = {}
        if self.client_side_evaluators:
            for index, evaluator in enumerate(self.client_side_evaluators):
                try:
                    evaluator_result = evaluator(inputs, evaluation_output)
                    if isinstance(evaluator_result, dict):
                        if isinstance(evaluator_result, dict):
                            metrics.update(evaluator_result)
                            continue
                        evaluator_name = getattr(
                            evaluator, "__name__", f"evaluator_{index}"
                        )
                        metrics[evaluator_name] = evaluator_result
                except Exception as e:
                    print(f"Error in evaluator: {str(e)}")
        return metrics
    
    def run_each(self, eval_index: int):
        """Private function to run the evaluation for each datapoint."""
        print('Running evaluation: ', eval_index)
        # Get inputs from either honeyhive dataset or provided dataset
        inputs = None
        if (
            self.hh_dataset
            and self.hh_dataset.datapoints
            and len(self.hh_dataset.datapoints) > 0
        ):
            try:
                datapoint_id = self.hh_dataset.datapoints[eval_index]
                datapoint_response = self.hhai.datapoints.get_datapoint(id=datapoint_id)
                inputs = datapoint_response.object.datapoint[0].inputs
            except Exception as e:
                print(f"Error getting datapoint: {e}")
        elif self.dataset:
            inputs = self.dataset[eval_index]

        try:
            hh = HoneyHiveTracer(
                api_key=self.hh_api_key,
                project=self.hh_project,
                source="evaluation",
                session_name=self.eval_name,
                inputs=inputs,
                is_evaluation=True,
            )
            self.evaluation_session_ids.append(hh.session_id)
        except:
            raise Exception(
                "Unable to initiate Honeyhive Tracer. Cannot run Evaluation"
            )
        
        try:
            evaluation_output = self.func_to_evaluate(inputs)
        except Exception as error:
            print(f"Error in evaluation function: {error}")
            evaluation_output = None

        # TODO: the trace of the evaluator is being captured in the main trace
        metrics = self._run_evaluators(
            inputs, evaluation_output
        )
        
        self._add_trace_metadata(evaluation_output, eval_index, hh, metrics)

    def run(self):
        """Public function to run the evaluation."""
        eval_run = self.hhai.experiments.create_run(
            request=components.CreateRunRequest(
                project=self.hh_project,
                name=self.eval_name,
                dataset_id=self.hh_dataset_id or self.external_dataset_id,
                event_ids=[],
                status=self.status,
            )
        )
        self.eval_run = eval_run.create_run_response

        start_time = time.time()
        
        # TODO: remove this flag
        run_concurrently = True
        if run_concurrently:
            # Use ThreadPoolExecutor to run evaluations concurrently
            with ThreadPoolExecutor() as executor:
                executor.map(lambda i: self.run_each(i), range(len(self.dataset)))
        else:
            for i in range(len(self.dataset)):
                self.run_each(i)
        
        end_time = time.time()
        print(f"Evaluation completed in {round(end_time - start_time, 3)} seconds")

        # convert deque to list after all threads have completed
        self.evaluation_session_ids = list(self.evaluation_session_ids)

        try:
            if self.eval_run:
                self.status = "completed"
                self.hhai.experiments.update_run(
                    run_id=self.eval_run.run_id,
                    update_run_request=components.UpdateRunRequest(
                        event_ids=self.evaluation_session_ids, status=self.status
                    ),
                )
        except Exception:
            print("Warning: Unable to mark evaluation as `Completed`")

def evaluate(
    function=None,
    hh_api_key: str = None,
    hh_project: str = None,
    name: str = None,
    dataset_id: Optional[str] = None,
    dataset: Optional[List[Dict[str, Any]]] = None,
    evaluators: Optional[List[Any]] = None,
):

    if function is None:
        raise Exception(
            "No evaluation function found. Please define 'function' parameter."
        )

    eval = Evaluation(
        hh_api_key=hh_api_key,
        hh_project=hh_project,
        name=name,
        function=function,
        dataset=dataset,
        evaluators=evaluators,
        dataset_id=dataset_id,
    )
    eval.run()

    return {
        "run_id": eval.eval_run.run_id,
        "dataset_id": eval.hh_dataset_id or eval.external_dataset_id,
        "session_ids": eval.evaluation_session_ids,
        "status": eval.status,
    }
