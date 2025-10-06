
```
class LangfuseClient:
    """
    Simplified Langfuse client demonstrating key integration patterns:
    
    1. Singleton Management: Single client instance across system
    2. Trace Lifecycle: Complete trace management from start to finish
    3. Score Upload: Automated scoring with metadata preservation
    4. Error Handling: Graceful degradation when telemetry unavailable
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Langfuse client (singleton pattern)."""
        if not self._initialized:
            self.traces: Dict[str, TraceData] = {}
            self.scores: List[ScoreData] = []
            self.dataset_runs: Dict[str, DatasetRunData] = {}  # **NEW**: Dataset run tracking
            self.enabled = self._load_configuration()
            self.logger = logging.getLogger(f"{self.__class__.__name__}")
            
            if self.enabled:
                self.logger.info("Langfuse client initialized successfully")
            else:
                self.logger.warning("Langfuse client disabled - running in mock mode")
            
            LangfuseClient._initialized = True
    
    def _load_configuration(self) -> bool:
        """Load Langfuse configuration from environment variables."""
        try:
            # Check for required environment variables
            host = os.getenv("LANGFUSE_HOST")
            public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            
            if host and public_key and secret_key:
                self.host = host
                self.public_key = public_key
                self.secret_key = secret_key
                return True
            else:
                self.logger.info("Langfuse environment variables not found, running in mock mode")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading Langfuse configuration: {e}")
            return False
    
    async def start_trace(self, trace_id: str, trace_data: Dict[str, Any]) -> bool:
        """
        Start a new trace with telemetry integration.
        
        Demonstrates:
        - Trace lifecycle management
        - Metadata preservation
        - Error handling with graceful degradation
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Started trace {trace_id}")
                return True
            
            # Create trace data structure
            trace = TraceData(
                trace_id=trace_id,
                name=trace_data.get("name", "unnamed_trace"),
                start_time=datetime.now(),
                status=TraceStatus.STARTED,
                input_data=trace_data.get("input_data"),
                metadata=trace_data.get("metadata", {})
            )
            
            # Store trace for lifecycle management
            self.traces[trace_id] = trace
            
            # In real implementation, this would call Langfuse API
            self.logger.info(f"Started trace '{trace_id}' with name '{trace.name}'")
            
            # Simulate trace creation
            await asyncio.sleep(0.01)  # Simulate API call latency
            
            trace.status = TraceStatus.RUNNING
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start trace {trace_id}: {e}")
            return False
    
    async def end_trace(self, trace_id: str, result_data: Dict[str, Any]) -> bool:
        """
        End a trace with result data and metrics.
        
        Demonstrates:
        - Trace lifecycle completion
        - Result data preservation
        - Performance metrics capture
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Ended trace {trace_id}")
                return True
            
            # Retrieve and update trace
            if trace_id not in self.traces:
                self.logger.warning(f"Trace {trace_id} not found for ending")
                return False
            
            trace = self.traces[trace_id]
            trace.end_time = datetime.now()
            trace.output_data = result_data.get("result")
            trace.metadata.update(result_data.get("metadata", {}))
            
            # Determine final status
            if result_data.get("status") == "error":
                trace.status = TraceStatus.FAILED
            else:
                trace.status = TraceStatus.COMPLETED
            
            # Calculate execution time
            execution_time = (trace.end_time - trace.start_time).total_seconds()
            trace.metadata["execution_time_seconds"] = execution_time
            
            # In real implementation, this would update Langfuse trace
            self.logger.info(f"Ended trace '{trace_id}' with status '{trace.status.value}' (duration: {execution_time:.2f}s)")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to end trace {trace_id}: {e}")
            return False
    
    async def add_score(
        self,
        trace_id: str,
        name: str,
        value: Union[int, float, bool],
        observation_id: Optional[str] = None,
        comment: Optional[str] = None,
        data_type: str = "NUMERIC"
    ) -> bool:
        """
        Add score to trace with comprehensive metadata.
        
        Demonstrates:
        - Score upload system
        - Metadata preservation
        - Type safety and validation
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Added score '{name}' = {value} to trace {trace_id}")
                return True
            
            # Validate trace exists
            if trace_id not in self.traces:
                self.logger.warning(f"Cannot add score to non-existent trace {trace_id}")
                return False
            
            # Create score data
            score = ScoreData(
                name=name,
                value=value,
                trace_id=trace_id,
                observation_id=observation_id,
                comment=comment,
                data_type=data_type
            )
            
            # Store score
            self.scores.append(score)
            
            # In real implementation, this would call Langfuse scoring API
            self.logger.info(f"Added score '{name}' = {value} to trace '{trace_id}'")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add score to trace {trace_id}: {e}")
            return False
    
    async def create_dataset(self, name: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create dataset for evaluation data.
        
        Demonstrates:
        - Dataset management
        - Metadata handling
        - Factory pattern support
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Created dataset '{name}'")
                return True
            
            # In real implementation, this would call Langfuse dataset API
            self.logger.info(f"Created dataset '{name}': {description}")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create dataset '{name}': {e}")
            return False
    
    async def add_dataset_item(
        self,
        dataset_name: str,
        input_data: Any,
        expected_output: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add item to dataset for evaluation.
        
        Demonstrates:
        - Dataset item management
        - Input/output data handling
        - Metadata preservation
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Added item to dataset '{dataset_name}'")
                return True
            
            # In real implementation, this would call Langfuse dataset item API
            self.logger.debug(f"Added item to dataset '{dataset_name}'")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add item to dataset '{dataset_name}': {e}")
            return False
    
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of all traces for monitoring."""
        if not self.enabled:
            return {"enabled": False, "mode": "mock"}
        
        total_traces = len(self.traces)
        completed_traces = len([t for t in self.traces.values() if t.status == TraceStatus.COMPLETED])
        failed_traces = len([t for t in self.traces.values() if t.status == TraceStatus.FAILED])
        
        return {
            "enabled": True,
            "total_traces": total_traces,
            "completed_traces": completed_traces,
            "failed_traces": failed_traces,
            "success_rate": completed_traces / total_traces if total_traces > 0 else 0,
            "total_scores": len(self.scores)
        }
    
    def get_trace_details(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific trace."""
        if trace_id not in self.traces:
            return None
        
        trace = self.traces[trace_id]
        trace_scores = [s for s in self.scores if s.trace_id == trace_id]
        
        return {
            "trace_id": trace.trace_id,
            "name": trace.name,
            "status": trace.status.value,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "input_data": trace.input_data,
            "output_data": trace.output_data,
            "metadata": trace.metadata,
            "scores": [
                {
                    "name": s.name,
                    "value": s.value,
                    "comment": s.comment,
                    "data_type": s.data_type
                }
                for s in trace_scores
            ]
        }
    
    async def flush(self) -> bool:
        """Flush any pending telemetry data (graceful shutdown)."""
        try:
            if not self.enabled:
                return True
            
            # In real implementation, this would ensure all data is sent to Langfuse
            self.logger.info(f"Flushing telemetry data: {len(self.traces)} traces, {len(self.scores)} scores")
            
            # Simulate flush operation
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to flush telemetry data: {e}")
            return False
    
    async def create_dataset_run(
        self,
        dataset_name: str,
        run_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new dataset run for tracking execution.
        
        Demonstrates:
        - Dataset run lifecycle management
        - Run tracking and monitoring
        - Progress reporting capabilities
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Created dataset run '{run_name}' for dataset '{dataset_name}'")
                return f"mock_run_{dataset_name}_{len(self.dataset_runs)}"
            
            # Generate unique run ID
            run_id = f"run_{dataset_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.dataset_runs)}"
            
            # Create dataset run data
            run_data = DatasetRunData(
                run_id=run_id,
                dataset_name=dataset_name,
                run_name=run_name,
                created_at=datetime.now(),
                status="RUNNING",
                metadata=metadata or {}
            )
            
            # Store run for tracking
            self.dataset_runs[run_id] = run_data
            
            # In real implementation, this would call Langfuse dataset run API
            self.logger.info(f"Created dataset run '{run_name}' (ID: {run_id}) for dataset '{dataset_name}'")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return run_id
            
        except Exception as e:
            self.logger.error(f"Failed to create dataset run '{run_name}' for dataset '{dataset_name}': {e}")
            return None
    
    async def update_dataset_run(
        self,
        run_id: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """
        Update dataset run progress and statistics.
        
        Demonstrates:
        - Progress tracking during execution
        - Real-time statistics updates
        - Run status management
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Updated dataset run {run_id}")
                return True
            
            # Validate run exists
            if run_id not in self.dataset_runs:
                self.logger.warning(f"Dataset run {run_id} not found for update")
                return False
            
            run_data = self.dataset_runs[run_id]
            
            # Update progress statistics
            if "total_items" in progress_data:
                run_data.total_items = progress_data["total_items"]
            if "processed_items" in progress_data:
                run_data.processed_items = progress_data["processed_items"]
            if "successful_items" in progress_data:
                run_data.successful_items = progress_data["successful_items"]
            if "failed_items" in progress_data:
                run_data.failed_items = progress_data["failed_items"]
            
            # Update status if provided
            if "status" in progress_data:
                run_data.status = progress_data["status"]
            
            # Update metadata
            if "metadata" in progress_data:
                run_data.metadata.update(progress_data["metadata"])
            
            # In real implementation, this would update Langfuse dataset run
            self.logger.debug(f"Updated dataset run {run_id}: {run_data.processed_items}/{run_data.total_items} items processed")
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update dataset run {run_id}: {e}")
            return False
    
    async def finalize_dataset_run(
        self,
        run_id: str,
        final_status: str = "COMPLETED"
    ) -> bool:
        """
        Finalize dataset run with completion status and summary.
        
        Demonstrates:
        - Run lifecycle completion
        - Final statistics calculation
        - Summary reporting
        """
        try:
            if not self.enabled:
                self.logger.debug(f"Mock mode: Finalized dataset run {run_id} with status {final_status}")
                return True
            
            # Validate run exists
            if run_id not in self.dataset_runs:
                self.logger.warning(f"Dataset run {run_id} not found for finalization")
                return False
            
            run_data = self.dataset_runs[run_id]
            
            # Set completion status and timestamp
            run_data.status = final_status
            run_data.completed_at = datetime.now()
            
            # Calculate execution time
            execution_time = (run_data.completed_at - run_data.created_at).total_seconds()
            run_data.metadata["execution_time_seconds"] = execution_time
            
            # Calculate success rate
            if run_data.total_items > 0:
                success_rate = run_data.successful_items / run_data.total_items
                run_data.metadata["success_rate"] = success_rate
            
            # In real implementation, this would finalize Langfuse dataset run
            self.logger.info(
                f"Finalized dataset run {run_id} for dataset '{run_data.dataset_name}': "
                f"{run_data.successful_items}/{run_data.total_items} successful "
                f"(duration: {execution_time:.2f}s)"
            )
            
            # Simulate API call
            await asyncio.sleep(0.01)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to finalize dataset run {run_id}: {e}")
            return False
    
    def get_dataset_run_summary(self) -> Dict[str, Any]:
        """Get summary of all dataset runs for monitoring."""
        if not self.enabled:
            return {"enabled": False, "mode": "mock"}
        
        total_runs = len(self.dataset_runs)
        completed_runs = len([r for r in self.dataset_runs.values() if r.status == "COMPLETED"])
        failed_runs = len([r for r in self.dataset_runs.values() if r.status == "FAILED"])
        running_runs = len([r for r in self.dataset_runs.values() if r.status == "RUNNING"])
        
        # Calculate aggregate statistics
        total_items_processed = sum(r.processed_items for r in self.dataset_runs.values())
        total_successful_items = sum(r.successful_items for r in self.dataset_runs.values())
        
        return {
            "enabled": True,
            "total_runs": total_runs,
            "completed_runs": completed_runs,
            "failed_runs": failed_runs,
            "running_runs": running_runs,
            "completion_rate": completed_runs / total_runs if total_runs > 0 else 0,
            "total_items_processed": total_items_processed,
            "total_successful_items": total_successful_items,
            "overall_success_rate": total_successful_items / total_items_processed if total_items_processed > 0 else 0
        }
    
    def get_dataset_run_details(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific dataset run."""
        if run_id not in self.dataset_runs:
            return None
        
        run_data = self.dataset_runs[run_id]
        
        return {
            "run_id": run_data.run_id,
            "dataset_name": run_data.dataset_name,
            "run_name": run_data.run_name,
            "status": run_data.status,
            "created_at": run_data.created_at.isoformat(),
            "completed_at": run_data.completed_at.isoformat() if run_data.completed_at else None,
            "total_items": run_data.total_items,
            "processed_items": run_data.processed_items,
            "successful_items": run_data.successful_items,
            "failed_items": run_data.failed_items,
            "success_rate": run_data.successful_items / run_data.total_items if run_data.total_items > 0 else 0,
            "metadata": run_data.metadata
        }
 
 
# Factory function for getting client instance (singleton pattern)
def get_langfuse_client() -> LangfuseClient:
    """Get singleton Langfuse client instance."""
    return LangfuseClient()
 
 
# Convenience functions for common operations
async def start_trace(trace_id: str, trace_data: Dict[str, Any]) -> bool:
    """Convenience function to start a trace."""
    client = get_langfuse_client()
    return await client.start_trace(trace_id, trace_data)
 
 
async def end_trace(trace_id: str, result_data: Dict[str, Any]) -> bool:
    """Convenience function to end a trace."""
    client = get_langfuse_client()
    return await client.end_trace(trace_id, result_data)
 
 
async def add_score(trace_id: str, name: str, value: Union[int, float, bool], **kwargs) -> bool:
    """Convenience function to add a score."""
    client = get_langfuse_client()
    return await client.add_score(trace_id, name, value, **kwargs)
 
 
# Dataset run convenience functions
async def create_dataset_run(dataset_name: str, run_name: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Convenience function to create a dataset run."""
    client = get_langfuse_client()
    return await client.create_dataset_run(dataset_name, run_name, metadata)
 
 
async def update_dataset_run(run_id: str, progress_data: Dict[str, Any]) -> bool:
    """Convenience function to update dataset run progress."""
    client = get_langfuse_client()
    return await client.update_dataset_run(run_id, progress_data)
 
 
async def finalize_dataset_run(run_id: str, final_status: str = "COMPLETED") -> bool:
    """Convenience function to finalize a dataset run."""
    client = get_langfuse_client()
    return await client.finalize_dataset_run(run_id, final_status)
```

Usage example:

```
async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conversation simulation with autonomous decision-making.
        
        Demonstrates:
        - Dynamic persona selection
        - Context-aware conversation generation
        - Autonomous simulation parameters
        - Results aggregation and analysis
        """
        workflow_data = input_data.get("workflow_data", {})
        num_conversations = workflow_data.get("num_conversations", 3)
        conversation_length = workflow_data.get("conversation_length", 5)
        
        self.logger.info(f"Starting simulation of {num_conversations} conversations")
        
        # Autonomous persona selection
        selected_personas = await self._select_personas(num_conversations)
        
        # Generate conversations for each persona
        conversations = []
        simulation_metrics = {
            "total_conversations": 0,
            "successful_conversations": 0,
            "average_conversation_length": 0,
            "persona_distribution": {},
            "category_distribution": {}
        }
        
        for persona in selected_personas:
            try:
                # Generate conversation starter based on persona context
                conversation_starter = await self._generate_conversation_starter(persona)
                
                # Simulate conversation
                conversation_result = await self._simulate_conversation(
                    persona, conversation_starter, conversation_length
                )
                
                conversations.append(conversation_result)
                simulation_metrics["total_conversations"] += 1
                
                if conversation_result.get("status") == "completed":
                    simulation_metrics["successful_conversations"] += 1
                
                # Track persona and category distribution
                persona_name = persona["name"]
                category = conversation_result.get("category", "unknown")
                
                simulation_metrics["persona_distribution"][persona_name] = \
                    simulation_metrics["persona_distribution"].get(persona_name, 0) + 1
                simulation_metrics["category_distribution"][category] = \
                    simulation_metrics["category_distribution"].get(category, 0) + 1
                
                # Add telemetry for individual conversation
                if self.telemetry_client:
                    await self.telemetry_client.add_score(
                        trace_id=conversation_result.get("trace_id", "unknown"),
                        name="conversation_success",
                        value=1 if conversation_result.get("status") == "completed" else 0,
                        comment=f"Conversation with {persona_name}"
                    )
                
            except Exception as e:
                self.logger.warning(f"Failed to simulate conversation for persona {persona['name']}: {e}")
                conversations.append({
                    "persona": persona["name"],
                    "status": "failed",
                    "error": str(e)
                })
        
        # Calculate final metrics
        if conversations:
            completed_conversations = [c for c in conversations if c.get("status") == "completed"]
            if completed_conversations:
                avg_length = sum(len(c.get("messages", [])) for c in completed_conversations) / len(completed_conversations)
                simulation_metrics["average_conversation_length"] = avg_length
        
        simulation_metrics["success_rate"] = (
            simulation_metrics["successful_conversations"] / simulation_metrics["total_conversations"]
            if simulation_metrics["total_conversations"] > 0 else 0
        )
        
        self.logger.info(f"Completed simulation: {simulation_metrics['successful_conversations']}/{simulation_metrics['total_conversations']} successful")
        
        return {
            "conversations": conversations,
            "metrics": simulation_metrics,
            "personas_used": len(selected_personas),
            "timestamp": datetime.now().isoformat()
        }
 
async def _simulate_conversation(
        self,
        persona: Dict[str, Any],
        conversation_starter: Dict[str, Any],
        max_turns: int
    ) -> Dict[str, Any]:
        """
        Simulate complete conversation with autonomous turn generation.
        
        Demonstrates:
        - Conversation state management
        - Dynamic response generation
        - Context preservation across turns
        """
        conversation_id = f"conv_{persona['cif']}_{datetime.now().strftime('%H%M%S')}"
        trace_id = f"trace_{conversation_id}"
        
        # Start telemetry trace for conversation
        if self.telemetry_client:
            await self.telemetry_client.start_trace(trace_id, {
                "name": f"conversation_simulation",
                "persona": persona["name"],
                "category": conversation_starter["category"],
                "input_data": {
                    "persona": persona,
                    "starter": conversation_starter
                }
            })
        
        messages = []
        current_turn = 0
        
        # Add initial user message
        messages.append({
            "role": "user",
            "content": conversation_starter["text"],
            "timestamp": datetime.now().isoformat(),
            "turn": current_turn
        })
        
        try:
            # Simulate conversation turns
            while current_turn < max_turns:
                current_turn += 1
                
                # Generate assistant response (simulated)
                assistant_response = await self._generate_assistant_response(
                    messages, persona, conversation_starter["category"]
                )
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_response,
                    "timestamp": datetime.now().isoformat(),
                    "turn": current_turn
                })
                
                # Decide if conversation should continue (autonomous decision)
                should_continue = await self._should_continue_conversation(messages, current_turn, max_turns)
                if not should_continue:
                    break
                
                # Generate follow-up user message if continuing
                if current_turn < max_turns:
                    current_turn += 1
                    user_followup = await self._generate_user_followup(
                        messages, persona, conversation_starter["category"]
                    )
                    
                    messages.append({
                        "role": "user",
                        "content": user_followup,
                        "timestamp": datetime.now().isoformat(),
                        "turn": current_turn
                    })
                
                # Simulate processing delay
                await asyncio.sleep(0.1)
            
            # End telemetry trace
            if self.telemetry_client:
                await self.telemetry_client.end_trace(trace_id, {
                    "status": "success",
                    "result": {
                        "conversation_id": conversation_id,
                        "message_count": len(messages),
                        "turns": current_turn
                    }
                })
            
            return {
                "conversation_id": conversation_id,
                "trace_id": trace_id,
                "persona": persona["name"],
                "category": conversation_starter["category"],
                "messages": messages,
                "status": "completed",
                "turns": current_turn,
                "duration_simulated": True
            }
            
        except Exception as e:
            # End telemetry trace with error
            if self.telemetry_client:
                await self.telemetry_client.end_trace(trace_id, {
                    "status": "error",
                    "error": str(e)
                })
            
            raise e
 ```