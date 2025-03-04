from honeyhive.sdk import HoneyHive
from honeyhive.models import components
from honeyhive import HoneyHiveTracer, enrich_session
from .evaluators import evaluator, aevaluator

from concurrent.futures import ThreadPoolExecutor
import collections
import contextvars
import functools

from rich.style import Style
from rich.console import Console
from rich.table import Table

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable
import os
import hashlib
import json
import time
import sys
import traceback
import asyncio
import inspect

@dataclass
class EvaluationResult:
    run_id: str
    stats: Dict[str, Any]
    dataset_id: str 
    session_ids: list
    status: str
    suite: str
    data: Dict[str, list]

    def to_json(self):
        # save data dict to json file
        with open(f"{self.suite}.json", "w") as f:
            json.dump(self.data, f, indent=4)

class DatasetLoader:

    @staticmethod
    def load_dataset(hhai: HoneyHive, project: str, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Private function to acquire Honeyhive dataset based on dataset_id."""
        if not dataset_id:
            return None
        try:
            dataset = hhai.datasets.get_datasets(
                project=project,
                dataset_id=dataset_id,
            )
            if (
                dataset
                and dataset.object.testcases
                and len(dataset.object.testcases) > 0
            ):
                return dataset.object.testcases[0]
        except Exception:
            raise RuntimeError(
                f"No dataset found with id - {dataset_id} for project - {project}. Please use the correct dataset id and project name."
            )


console = Console()

class Evaluation:
    """This class is for automated honeyhive evaluation with tracing"""

    def __init__(
        self,
        hh_api_key: str = None,
        hh_project: str = None,
        name: Optional[str] = None,
        suite: Optional[str] = None,
        function: Optional[Callable] = None,
        dataset: Optional[List[Any]] = None,
        evaluators: Optional[List[Any]] = None,
        dataset_id: Optional[str] = None,
        max_workers: int = 10,
        run_concurrently: bool = True,
        server_url: Optional[str] = None,
        verbose: bool = False,
    ):
        
        if function is None:
            raise Exception(
                "Please provide a function to evaluate."
            )
        
        # if name is not provided, use the file name
        try:
            if name is None:
                name = os.path.basename(sys._getframe(1).f_code.co_filename)
        except Exception:
            name = "default"

        # get the directory of the file being evaluated
        try:
            if suite is None:
                suite = os.path.dirname(sys._getframe(1).f_code.co_filename).split(os.sep)[-1]
        except Exception:
            suite = "default"
        
        self.hh_api_key = hh_api_key or os.environ["HH_API_KEY"]
        self.hh_project = hh_project or os.environ["HH_PROJECT"]
        self.eval_name: str = name
        self.hh_dataset_id: Optional[str] = dataset_id
        self.client_side_evaluators = evaluators or []
        self.status: str = "pending"
        self.max_workers: int = max_workers
        self.run_concurrently: bool = run_concurrently
        self.dataset = dataset
        self.func_to_evaluate: Callable = function
        self.suite = suite
        self.disable_auto_tracing = True
        self.eval_run: Optional[components.CreateRunResponse] = None
        self.evaluation_session_ids: collections.deque = collections.deque()
        self._validate_requirements()

        self.hhai = HoneyHive(bearer_auth=self.hh_api_key, server_url=server_url)
        self.hh_dataset = DatasetLoader.load_dataset(self.hhai, self.hh_project, self.hh_dataset_id)

        self.server_url = server_url
        self.verbose = verbose

        # generated id for external datasets
        # TODO: large dataset optimization
        # TODO: dataset might not be json serializable
        self.external_dataset_id: str = (
            Evaluation.generate_hash(json.dumps(dataset)) if dataset else None
        )

        # increase the OTEL export timeout to 30 seconds
        # os.environ["OTEL_EXPORTER_OTLP_TIMEOUT"] = "30000"

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
        if self.dataset is not None:
            if not isinstance(self.dataset, list):
                raise Exception("Dataset must be a list")
            if not all(isinstance(item, dict) for item in self.dataset):
                raise Exception("All items in dataset must be dictionaries")

    @staticmethod
    def generate_hash(input_string: str) -> str:
        return f"EXT-{hashlib.md5(input_string.encode('utf-8')).hexdigest()[:24]}"

    # ------------------------------------------------------------

    def _get_tracing_metadata(
        self,
        datapoint_idx: int,
    ):
        """Get tracing metadata for evaluation."""
        tracing_metadata = {"run_id": self.eval_run.run_id}
        if self.hh_dataset:
            tracing_metadata["datapoint_id"] = self.hh_dataset.datapoints[datapoint_idx]
            tracing_metadata["dataset_id"] = self.hh_dataset_id
        if self.external_dataset_id:
            tracing_metadata["datapoint_id"] = Evaluation.generate_hash(
                json.dumps(self.dataset[datapoint_idx])
            )
            tracing_metadata["dataset_id"] = self.external_dataset_id

        return tracing_metadata

    def _enrich_evaluation_session(
        self,
        datapoint_idx: int,
        session_id: str,
        outputs: Optional[Any],
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Private function to enrich the session data post flow completion."""
        try:
            tracing_metadata = self._get_tracing_metadata(datapoint_idx)
            tracing_metadata.update(metadata)

            if not isinstance(outputs, dict):
                outputs = {"output": outputs}

            enrich_session(
                session_id=session_id,
                metadata=tracing_metadata,
                outputs=outputs,
                metrics=metrics,
            )
        except Exception as e:
            print(f"Error adding trace metadata: {e}")

    def _get_evaluator_metadata(self, eval_func, evaluator_name: str) -> dict:
        """Get metadata for an evaluator if it's decorated."""
        if not isinstance(eval_func, evaluator):
            return {}
            
        eval_settings_dict = evaluator.all_evaluator_settings[evaluator_name].resolve_settings().dict()
        # remove all None values, weight if 1.0 and asserts if False
        filtered_dict = {}
        for k, v in eval_settings_dict.items():
            if not (v is None or (k == 'weight' and v == 1.0) or (k == 'asserts' and v is False)):
                filtered_dict[k] = v
        return {
            'eval_settings': filtered_dict,
        }

    def _run_single_evaluator(
        self,
        eval_func,
        evaluator_name: str,
        outputs: Any,
        inputs: Dict[str, Any],
        ground_truth: Dict[str, Any]
    ) -> tuple[str, Any, dict]:
        """Run a single evaluator and return its name, result and metadata."""
        metadata = self._get_evaluator_metadata(eval_func, evaluator_name)

        try:
            # if evaluator takes 1 argument, pass outputs
            if eval_func.__code__.co_argcount == 1:
                evaluator_result = eval_func(outputs)
            # if evaluator takes 2 arguments, pass outputs and inputs
            elif eval_func.__code__.co_argcount == 2:
                evaluator_result = eval_func(outputs, inputs)
            # if evaluator takes 3 arguments, pass outputs, inputs, and ground_truth
            elif eval_func.__code__.co_argcount == 3:
                evaluator_result = eval_func(outputs, inputs, ground_truth)
            else:
                raise ValueError(f"Evaluator {evaluator_name} must accept either 1, 2, or 3 arguments (outputs, inputs, ground_truth)")
            
            return evaluator_name, evaluator_result, metadata

        except AssertionError:
            return evaluator_name, None, metadata
        except Exception as e:
            print(f"Error in evaluator: {str(e)}\n")
            print(traceback.format_exc())
            return evaluator_name, None, metadata

    async def _arun_single_evaluator(
        self,
        eval_func,
        evaluator_name: str,
        outputs: Any,
        inputs: Dict[str, Any],
        ground_truth: Dict[str, Any]
    ) -> tuple[str, Any, dict]:
        """Run a single async evaluator and return its name, result and metadata."""
        metadata = self._get_evaluator_metadata(eval_func, evaluator_name)

        try:
            # if evaluator takes 1 argument, pass outputs
            if eval_func.__code__.co_argcount == 1:
                evaluator_result = await eval_func(outputs)
            # if evaluator takes 2 arguments, pass outputs and inputs
            elif eval_func.__code__.co_argcount == 2:
                evaluator_result = await eval_func(outputs, inputs)
            # if evaluator takes 3 arguments, pass outputs, inputs, and ground_truth
            elif eval_func.__code__.co_argcount == 3:
                evaluator_result = await eval_func(outputs, inputs, ground_truth)
            else:
                raise ValueError(f"Evaluator {evaluator_name} must accept either 1, 2, or 3 arguments (outputs, inputs, ground_truth)")
            
            return evaluator_name, evaluator_result, metadata

        except AssertionError:
            return evaluator_name, None, metadata
        except Exception as e:
            print(f"Error in evaluator: {str(e)}\n")
            print(traceback.format_exc())
            return evaluator_name, None, metadata

    def _run_evaluators(
        self, 
        outputs: Optional[Any], 
        inputs: Optional[Dict[str, Any]], 
        ground_truth: Optional[Dict[str, Any]]
    ):
        """Run evaluators and collect metrics."""
        metrics = {}
        metadata = {}

        if not self.client_side_evaluators:
            return metrics, metadata

        # Separate sync and async evaluators
        sync_evaluators = []
        async_evaluators = []
        eval_names = set()

        for index, eval_func in enumerate(self.client_side_evaluators):
            evaluator_name = getattr(eval_func, "__name__", f"evaluator_{index}")
            if evaluator_name in eval_names:
                raise ValueError(f"Evaluator {evaluator_name} is defined multiple times")
            eval_names.add(evaluator_name)

            if inspect.iscoroutinefunction(eval_func):
                async_evaluators.append((eval_func, evaluator_name))
            else:
                sync_evaluators.append((eval_func, evaluator_name))

        # Run sync evaluators first
        for eval_func, name in sync_evaluators:
            name, result, meta = self._run_single_evaluator(
                eval_func, name, outputs, inputs, ground_truth
            )
            metrics[name] = result
            if meta:
                metadata[name] = meta

        # Run async evaluators concurrently if any exist
        if async_evaluators:
            print('Evaluators cannot be run async. Please use sync evaluators only.')
        # if async_evaluators:

        #     async def arun_async_evaluators():
        #         async_tasks = [
        #             self._arun_single_evaluator(eval_func, name, outputs, inputs, ground_truth)
        #             for eval_func, name in async_evaluators
        #         ]
        #         return await asyncio.gather(*async_tasks)

        #     async_results = asyncio.run(arun_async_evaluators())

        #     for name, result, meta in async_results:
        #         metrics[name] = result
        #         if meta:
        #             metadata[name] = meta

        return metrics, metadata

    def _create_result(self, inputs, ground_truth, outputs, metrics, metadata):
        """Create standardized result dictionary."""
        return {
            'input': inputs,
            'ground_truth': ground_truth,
            'output': outputs,
            'metrics': metrics,
            'metadata': metadata,
        }

    def _get_inputs_and_ground_truth(self, datapoint_idx: int):
        """Get inputs and ground truth for evaluation from dataset."""
        if (
            self.hh_dataset
            and self.hh_dataset.datapoints
            and len(self.hh_dataset.datapoints) > 0
        ):
            datapoint_id = self.hh_dataset.datapoints[datapoint_idx]
            datapoint_response = self.hhai.datapoints.get_datapoint(id=datapoint_id)
            return (
                datapoint_response.object.datapoint[0].inputs or {}, 
                datapoint_response.object.datapoint[0].ground_truth or {}
            )
        elif self.dataset:
            return (
                self.dataset[datapoint_idx].get('inputs', {}), 
                self.dataset[datapoint_idx].get('ground_truths', {})
            )
        return ({}, {})

    def _init_tracer(self, datapoint_idx: int, inputs: Dict[str, Any]) -> HoneyHiveTracer:
        """Initialize HoneyHiveTracer for evaluation."""
        hh = HoneyHiveTracer(
            api_key=self.hh_api_key,
            project=self.hh_project,
            source="evaluation",
            session_name=self.eval_name,
            inputs={'inputs': inputs},
            is_evaluation=True,
            verbose=self.verbose,
            server_url=self.server_url,
            **self._get_tracing_metadata(datapoint_idx)
        )
        return hh

    def run_each(self, datapoint_idx: int) -> Dict[str, Any]:
        """Run evaluation for a single datapoint in its own thread."""

        inputs = {}
        ground_truth = {}
        outputs = None
        metrics = {}
        metadata = {}
        session_id = None

        # Get inputs
        try:
            inputs, ground_truth = self._get_inputs_and_ground_truth(datapoint_idx)
        except Exception as e:
            print(f"Error getting inputs for index {datapoint_idx}: {e}")
            return self._create_result(inputs, ground_truth, outputs, metrics, metadata)

        # Initialize tracer
        try:
            hh = self._init_tracer(datapoint_idx, inputs)
            session_id = hh.session_id
            self.evaluation_session_ids.append(session_id)
        except Exception as e:
            print(traceback.format_exc())
            raise Exception(
                f"Unable to initiate Honeyhive Tracer. Cannot run Evaluation: {e}"
            )
        # Run the function
        try:
            if inspect.iscoroutinefunction(self.func_to_evaluate):
                raise ValueError("Evaluation task must be sync. Please use asyncio.run() to run coroutines inside the task.")
            else:
                if self.func_to_evaluate.__code__.co_argcount == 2:
                    outputs = self.func_to_evaluate(inputs, ground_truth)
                elif self.func_to_evaluate.__code__.co_argcount == 1:
                    outputs = self.func_to_evaluate(inputs)
                else:
                    raise ValueError(f"Evaluation function must accept either 1 or 2 arguments (inputs, ground_truth)")
        except Exception as e:
            print(f"Error in evaluation function: {e}")
            print(traceback.format_exc())
        
        # Run evaluators
        metrics, metadata = self._run_evaluators(outputs, inputs, ground_truth)
        
        # Add trace metadata, outputs, and metrics to session

        self._enrich_evaluation_session(
            datapoint_idx,
            session_id, 
            outputs,
            metrics,
            metadata
        )

        console.print(f"Test case {datapoint_idx} complete")
        
        return self._create_result(inputs, ground_truth, outputs, metrics, metadata)

    def run(self):
        """Public function to run the evaluation."""

        # create run
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

        self.eval_result = EvaluationResult(
            run_id=self.eval_run.run_id,
            dataset_id=self.hh_dataset_id or self.external_dataset_id,
            session_ids=[],
            status=self.status,
            suite=self.suite,
            stats={},
            data={},
        )

        #########################################################
        # Run evaluations
        #########################################################

        if self.hh_dataset:
            num_points = len(self.hh_dataset.datapoints)
        elif self.dataset:
            num_points = len(self.dataset)
        else:
            raise Exception("No dataset found")
        
        start_time = time.time()
        if self.run_concurrently:
            # Use ThreadPoolExecutor to run evaluations concurrently
            max_workers = int(os.getenv("HH_MAX_WORKERS", self.max_workers))
            with console.status("[bold green]Working on evals...") as status:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    try:
                        # Submit tasks and get futures with proper context propagation
                        futures = []
                        for i in range(num_points):
                            ctx = contextvars.copy_context()
                            futures.append(
                                executor.submit(
                                    ctx.run,
                                    functools.partial(self.run_each, i)
                                )
                            )
                        
                        # Collect results and log any errors
                        results = []
                        for future in futures:
                            try:
                                results.append(future.result())
                            except Exception as e:
                                print(f"Error in evaluation thread: {e}")
                                # Still add None result to maintain ordering
                                results.append(None)
                    except KeyboardInterrupt:
                        executor.shutdown(wait=False)
                        raise
        else:
            results = []
            for i in range(num_points):
                result = self.run_each(i)
                results.append(result)

        end_time = time.time()
        #########################################################

        # Process results
        self.eval_result.stats = {
            'duration_s': round(end_time - start_time, 3),
        }
        self.eval_result.data = {
            'input': [],
            'output': [],
            'metrics': [],
            'metadata': [],
            'ground_truth': []
        }
        for r in results:
            for k in self.eval_result.data.keys():
                self.eval_result.data[k].append(r[k])

        # Convert deque to list after all threads complete
        self.eval_result.session_ids = list(self.evaluation_session_ids)

        #########################################################
        # Update run
        #########################################################
        try:
            if self.eval_run:
                self.status = "completed"
                self.hhai.experiments.update_run(
                    run_id=self.eval_run.run_id,
                    update_run_request=components.UpdateRunRequest(
                        event_ids=self.eval_result.session_ids, 
                        status=self.status
                    ),
                )
        except Exception:
            print("Warning: Unable to mark evaluation as `Completed`")


    def print_run(self):
        """Print the results of the evaluation."""

        # get column names
        input_cols = {k for result in self.eval_result.data['input'] for k in result.keys()}
        metric_cols = {k for result in self.eval_result.data['metrics'] for k in result.keys()}
        metadata_cols = {k for result in self.eval_result.data['metadata'] for k in result.keys()}
        ground_truth_cols = {k for result in self.eval_result.data['ground_truth'] for k in result.keys()}

        # make table
        table = Table(
            title=f"Evaluation Results: {self.eval_name}",
            show_lines=True,
            title_style=Style(
                color="black",
                bgcolor="yellow",
                bold=True,
                frame=True,
            ),
        )
        table.add_column("Suite", justify="center", style="magenta")
        for k in input_cols:
            table.add_column(f'Inputs.{k}', justify="center", style="green")
        table.add_column("Outputs", justify="center", style="blue")
        for k in ground_truth_cols:
            table.add_column(f'Ground Truths.{k}', justify="center", style="green")
        for k in metric_cols:
            table.add_column(f'Metrics.{k}', justify="center", style="blue")
        for k in metadata_cols:
            table.add_column(f'Metadata.{k}', justify="center", style="green")

        def truncated(string, max_length=500):
            if len(string) > max_length:
                return string[:max_length] + "..."
            return string

        # Get length of any list in data dict since they're all equal length
        n_rows = len(self.eval_result.data['input'])
        
        for idx in range(n_rows):
            row_values = [self.eval_result.suite]
            # Add input columns
            for k in input_cols:
                row_values.append(truncated(str(self.eval_result.data['input'][idx].get(k, ''))))
            # Add output column
            row_values.append(truncated(str(self.eval_result.data['output'][idx])))
            # Add ground truth columns
            for k in ground_truth_cols:
                row_values.append(truncated(str(self.eval_result.data['ground_truth'][idx].get(k, ''))))
            # Add metric columns
            for k in metric_cols:
                row_values.append(truncated(str(self.eval_result.data['metrics'][idx].get(k, ''))))
            # Add metadata columns
            for k in metadata_cols:
                row_values.append(truncated(str(self.eval_result.data['metadata'][idx].get(k, ''))))
            table.add_row(*row_values)

        console.print(table)

        # add footer with evaluation duration
        print(f"Evaluation Duration: {self.eval_result.stats['duration_s']} seconds\n")

        print('Exporting traces to HoneyHive...')


def evaluate(*args, **kwargs):

    eval = Evaluation(*args, **kwargs)

    # run evaluation
    eval.run()

    # print evaluation results
    eval.print_run()

    return EvaluationResult(
        run_id=eval.eval_run.run_id,
        dataset_id=eval.hh_dataset_id or eval.external_dataset_id,
        session_ids=eval.evaluation_session_ids,
        status=eval.status,
        data=eval.eval_result.data,
        stats=eval.eval_result.stats,
        suite=eval.suite
    )


__all__ = [
    "evaluate",
    "evaluator",
    "aevaluator",
]
