
from typing import Optional, List, Dict, Any
import os

import honeyhive
from honeyhive.models import components
from honeyhive import HoneyHiveTracer, enrich_session

from realign.simulation import Simulation, Context

class Evaluation(Simulation):
    ''' This class is for automated honeyhive evaluation with tracing '''

    def __init__(self, 
                 hh_api_key: str = None,
                 hh_project: str = None,
                 name: str = None, 
                 dataset_id: Optional[str] = None, 
                 query_list: Optional[List[Dict[str, Any]]] = None,
                 runs: int = None # can be used to run for part of the dataset
                 ):
        super().__init__()

        self.hh_api_key = hh_api_key or os.environ['HH_API_KEY']
        self.hh_project = hh_project or os.environ['HH_PROJECT']
        self.eval_name: str = name
        self.hh_dataset_id: str = dataset_id
        self.query_list = query_list
        
        self._validate_requirements()
        self.hhai = honeyhive.HoneyHive(bearer_auth=self.hh_api_key)
        self.hh_dataset = self._load_dataset()
        self.runs = runs or len(self.hh_dataset.datapoints) if self.hh_dataset else len(query_list) if query_list else 0

        self.evaluation_session_ids: List[str] = []
        self.eval_run: Optional[components.CreateRunResponse] = None
        self.disable_auto_tracing = True
        
    def _validate_requirements(self) -> None:
        ''' Sanity check of requirements for HoneyHive evaluations and tracing. '''
        if not self.hh_api_key:
            raise Exception("Honeyhive API key not found. Please set 'hh_api_key' to initiate Honeyhive Tracer. Cannot run Evaluation")
        if not self.hh_project:
            raise Exception("Honeyhive Project not found. Please set 'hh_project' to initiate Honeyhive Tracer. Cannot run Evaluation")
        if not self.eval_name:
            raise Exception("Evaluation name not found. Please set 'name' to initiate Honeyhive Evaluation.")
        if not self.hh_dataset_id and not self.query_list:
            raise Exception("No valid 'dataset_id' or 'query_list' found. Please provide one to iterate the evaluation over.")

    def _load_dataset(self) -> Optional[Any]:
        ''' Private function to acquire Honeyhive dataset based on dataset_id. '''
        if not self.hh_dataset_id:
            return None
        try:
            dataset = self.hhai.datasets.get_datasets(
                project=self.hh_project,
                dataset_id=self.hh_dataset_id,
            )
            if dataset and dataset.object.testcases and len(dataset.object.testcases) > 0:
                return dataset.object.testcases[0]
        except Exception:
            raise RuntimeError(f"No dataset found with id - {self.hh_dataset_id} for project - {self.hh_project}")

    def _get_inputs(self, run_id: int) -> Optional[Dict[str, Any]]:
        ''' Private function to process and iterate over HoneyHive datapoints from Honeyhive dataset '''
        if self.hh_dataset and self.hh_dataset.datapoints and len(self.hh_dataset.datapoints) > 0 :
            try:
                datapoint_id = self.hh_dataset.datapoints[run_id]
                datapoint_response = self.hhai.datapoints.get_datapoint(id=datapoint_id)
                return datapoint_response.object.datapoint[0].inputs
            except Exception as e:
                print(f"Error getting datapoint: {e}")
        elif self.query_list:
            return self.query_list[run_id]
        return None

    def _initialize_tracer(self):
        ''' Private function to instrument Honeyhive Tracer. '''
        try:
            HoneyHiveTracer.init(
                api_key=self.hh_api_key,
                project=self.hh_project,
                source='evaluation',
                session_name=self.eval_name,
            )
        except:
            raise Exception("Unable to initiate Honeyhive Tracer. Cannot run Evaluation")

    async def _run_evaluation(self, inputs: Optional[Dict[str, Any]]) -> Optional[Any]:
        ''' Private function to safely execute the evaluating function '''
        try:
            return await self.eval_function(inputs)
        except Exception as error:
            print(f"Error in evaluation function: {error}")
            return None

    def _add_trace_metadata(self, inputs: Optional[Dict[str, Any]], evaluation_output: Optional[Any], run_id: int):
        ''' Private function to enrich the session data post flow completion. '''
        try:
            tracing_metadata = {
                "run_id": self.eval_run.run_id,
                "inputs": inputs
            }
            if self.hh_dataset:
                tracing_metadata["datapoint_id"] = self.hh_dataset.datapoints[run_id]
                tracing_metadata["dataset_id"] = self.hh_dataset_id
            if evaluation_output:
                tracing_metadata["outputs"] = evaluation_output

            enrich_session(
                metadata=tracing_metadata,
                outputs=evaluation_output
            )
        except Exception as e:
            print(f"Error adding trace metadata: {e}")

    async def _before_each(self, run_context: Context):
        ''' Private function to load inputs and initialize session for evaluation run. '''
        run_context.inputs = self._get_inputs(run_context.run_id)
        self._initialize_tracer()

        return await super()._before_each(run_context)
    
    async def _after_each(self, run_context: Context):
        ''' Private function to tag session and append to evaluation run. '''
        self._add_trace_metadata(run_context.inputs, run_context.final_state, run_context.run_id)
        self.evaluation_session_ids.append(HoneyHiveTracer.session_id)

        return await super()._after_each(run_context)
    
    async def setup(self, *args, **kwargs):
        ''' Custom instrumentation for inherited function. Initiate an evaluation run in Honeyhive.'''
        eval_run = self.hhai.runs.create_run(request=components.CreateRunRequest(
            project=self.hh_project,
            name=self.eval_name,
            dataset_id=self.hh_dataset_id,
            event_ids=[],
        ))
        self.eval_run = eval_run.create_run_response

    async def windup(self):
        ''' Custom instrumentation for inherited function. Orchestrate the HoneyHive evaluation flow.'''
        try:
            if self.eval_run:
                self.hhai.runs.update_run(
                    run_id=self.eval_run.run_id,
                    update_run_request=components.UpdateRunRequest(
                        event_ids=self.evaluation_session_ids,
                        status="completed"
                    )
                )
        except Exception:
            print("Warning: Unable to mark evaluation as `Completed`")
        await super().windup()


def evaluate(
        function = None,
        hh_api_key: str = None,
        hh_project: str = None,
        name: str = None, 
        dataset_id: Optional[str] = None, 
        query_list: Optional[List[Dict[str, Any]]] = None, 
        runs: int = None # can be used to run for part of the dataset
        ):
    
    if function is None:
        raise Exception("No evaluation function found. Please define 'function' parameter.")
    
    class FunctionEvaluation(Evaluation):
        async def main(self, run_context):
            inputs = run_context.inputs 
            output = function(inputs)
            return output
    
    eval = FunctionEvaluation(
        hh_api_key=hh_api_key,
        hh_project=hh_project,
        name=name,
        dataset_id=dataset_id,
        query_list=query_list,
        runs=runs
    )
    eval.run()
