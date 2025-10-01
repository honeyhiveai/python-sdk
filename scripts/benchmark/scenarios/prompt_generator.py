"""
Prompt Generator Module

This module provides deterministic prompt generation for reproducible A/B testing
across LLM providers. Ensures identical conversation flows for fair benchmarking
while maintaining realistic variability. Follows Agent OS production code standards.
"""

import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from .conversation_templates import ConversationTemplates, ConversationScenario, SpanSize, ConversationDomain

logger = logging.getLogger(__name__)


class PromptGenerator:
    """Deterministic prompt generator for reproducible benchmark testing.
    
    Generates realistic and varied prompts while ensuring identical conversation
    flows between different LLM providers for fair A/B testing. Uses seeded
    randomness to maintain reproducibility across benchmark runs.
    
    :param seed: Base seed for deterministic randomization
    :type seed: Optional[int]
    :param conversation_templates: Template repository for scenario generation
    :type conversation_templates: Optional[ConversationTemplates]
    
    Example:
        >>> generator = PromptGenerator(seed=42)
        >>> prompts = generator.generate_prompt_batch(
        ...     count=10,
        ...     span_size_mode="mixed"
        ... )
        >>> print(f"Generated {len(prompts)} deterministic prompts")
    """
    
    def __init__(self, seed: Optional[int] = None, conversation_templates: Optional[ConversationTemplates] = None) -> None:
        """Initialize prompt generator with deterministic randomization.
        
        :param seed: Base seed for reproducible randomization
        :type seed: Optional[int]
        :param conversation_templates: Template repository, creates new if None
        :type conversation_templates: Optional[ConversationTemplates]
        """
        self.base_seed = seed or 12345
        self.templates = conversation_templates or ConversationTemplates()
        self._prompt_cache: Dict[int, str] = {}
        
        logger.debug(f"🎲 PromptGenerator initialized with seed {self.base_seed}")
    
    def generate_prompt(self, operation_id: int, span_size_mode: str = "mixed") -> Tuple[str, ConversationScenario]:
        """Generate a single deterministic prompt for the given operation ID.
        
        Uses the operation_id as a seed to ensure identical prompts are generated
        for the same operation across different benchmark runs and LLM providers.
        
        :param operation_id: Unique operation identifier for deterministic generation
        :type operation_id: int
        :param span_size_mode: Span size selection mode (small, medium, large, mixed)
        :type span_size_mode: str
        :return: Tuple of (generated_prompt, scenario_used)
        :rtype: Tuple[str, ConversationScenario]
        
        Example:
            >>> generator = PromptGenerator(seed=42)
            >>> prompt, scenario = generator.generate_prompt(
            ...     operation_id=5,
            ...     span_size_mode="large"
            ... )
            >>> print(f"Generated {scenario.span_size.value} span prompt")
        """
        # Check cache first
        cache_key = hash((operation_id, span_size_mode, self.base_seed))
        if cache_key in self._prompt_cache:
            # Need to regenerate scenario for return value
            scenario = self._select_scenario(operation_id, span_size_mode)
            return self._prompt_cache[cache_key], scenario
        
        # Set deterministic seed based on operation_id and base_seed
        deterministic_seed = self.base_seed + operation_id
        random.seed(deterministic_seed)
        
        # Select scenario deterministically
        scenario = self._select_scenario(operation_id, span_size_mode)
        
        # Generate prompt from scenario
        prompt = self.templates.generate_prompt(scenario, operation_id)
        
        # Cache the result
        self._prompt_cache[cache_key] = prompt
        
        logger.debug(f"🎲 Generated prompt for op_id={operation_id}, size={scenario.span_size.value}")
        return prompt, scenario
    
    def generate_prompt_batch(self, count: int, span_size_mode: str = "mixed", start_id: int = 0) -> List[Tuple[str, ConversationScenario]]:
        """Generate a batch of deterministic prompts.
        
        :param count: Number of prompts to generate
        :type count: int
        :param span_size_mode: Span size selection mode
        :type span_size_mode: str
        :param start_id: Starting operation ID for the batch
        :type start_id: int
        :return: List of (prompt, scenario) tuples
        :rtype: List[Tuple[str, ConversationScenario]]
        
        Example:
            >>> generator = PromptGenerator()
            >>> batch = generator.generate_prompt_batch(
            ...     count=5,
            ...     span_size_mode="mixed",
            ...     start_id=10
            ... )
            >>> for i, (prompt, scenario) in enumerate(batch):
            ...     print(f"Prompt {i}: {scenario.domain.value}")
        """
        batch = []
        for i in range(count):
            operation_id = start_id + i
            prompt, scenario = self.generate_prompt(operation_id, span_size_mode)
            batch.append((prompt, scenario))
        
        logger.debug(f"🎲 Generated batch of {count} prompts (start_id={start_id})")
        return batch
    
    def _select_scenario(self, operation_id: int, span_size_mode: str) -> ConversationScenario:
        """Select a scenario deterministically based on operation_id and span_size_mode.
        
        :param operation_id: Operation ID for deterministic selection
        :type operation_id: int
        :param span_size_mode: Span size selection mode
        :type span_size_mode: str
        :return: Selected conversation scenario
        :rtype: ConversationScenario
        """
        # Set seed for deterministic selection
        random.seed(self.base_seed + operation_id)
        
        # Get scenarios based on span size mode
        if span_size_mode == "mixed":
            # Distribute across all span sizes with weighted selection
            # 40% small, 40% medium, 20% large (realistic distribution)
            size_weights = [(SpanSize.SMALL, 0.4), (SpanSize.MEDIUM, 0.4), (SpanSize.LARGE, 0.2)]
            rand_val = random.random()
            cumulative = 0.0
            selected_size = SpanSize.MEDIUM  # default
            
            for size, weight in size_weights:
                cumulative += weight
                if rand_val <= cumulative:
                    selected_size = size
                    break
            
            scenarios = self.templates.get_scenarios_by_size(selected_size)
        elif span_size_mode in ["small", "medium", "large"]:
            size_enum = SpanSize(span_size_mode)
            scenarios = self.templates.get_scenarios_by_size(size_enum)
        else:
            logger.warning(f"Unknown span_size_mode: {span_size_mode}, using mixed")
            scenarios = self.templates.get_all_scenarios()
        
        if not scenarios:
            logger.error(f"No scenarios found for span_size_mode: {span_size_mode}")
            # Fallback to all scenarios
            scenarios = self.templates.get_all_scenarios()
        
        # Select scenario deterministically
        scenario_index = operation_id % len(scenarios)
        return scenarios[scenario_index]
    
    def generate_conversation_flow(self, operation_id: int, max_turns: int = 5) -> List[Tuple[str, ConversationScenario]]:
        """Generate a multi-turn conversation flow deterministically.
        
        Creates a realistic conversation with multiple exchanges, useful for
        testing complex tracing scenarios and conversation context handling.
        
        :param operation_id: Base operation ID for deterministic generation
        :type operation_id: int
        :param max_turns: Maximum number of conversation turns
        :type max_turns: int
        :return: List of conversation turns as (prompt, scenario) tuples
        :rtype: List[Tuple[str, ConversationScenario]]
        
        Example:
            >>> generator = PromptGenerator()
            >>> conversation = generator.generate_conversation_flow(
            ...     operation_id=42,
            ...     max_turns=3
            ... )
            >>> for turn, (prompt, scenario) in enumerate(conversation):
            ...     print(f"Turn {turn + 1}: {scenario.description}")
        """
        random.seed(self.base_seed + operation_id)
        
        # Select initial scenario to determine conversation domain and complexity
        initial_scenario = self._select_scenario(operation_id, "mixed")
        
        # Determine actual number of turns based on scenario complexity
        if initial_scenario.complexity == "low":
            num_turns = min(random.randint(1, 2), max_turns)
        elif initial_scenario.complexity == "medium":
            num_turns = min(random.randint(2, 4), max_turns)
        else:  # high complexity
            num_turns = min(random.randint(3, max_turns), max_turns)
        
        conversation = []
        
        for turn in range(num_turns):
            # Use turn-specific operation ID for variety within conversation
            turn_operation_id = operation_id * 100 + turn
            
            # For follow-up turns, prefer same domain but vary complexity
            if turn == 0:
                prompt, scenario = self.generate_prompt(turn_operation_id, "mixed")
            else:
                # Generate follow-up in same domain
                domain_scenarios = self.templates.get_scenarios_by_domain(initial_scenario.domain)
                if domain_scenarios:
                    random.seed(self.base_seed + turn_operation_id)
                    scenario = random.choice(domain_scenarios)
                    prompt = self.templates.generate_prompt(scenario, turn_operation_id)
                else:
                    prompt, scenario = self.generate_prompt(turn_operation_id, "mixed")
            
            conversation.append((prompt, scenario))
        
        logger.debug(f"🎲 Generated conversation flow with {num_turns} turns (op_id={operation_id})")
        return conversation
    
    def get_prompt_statistics(self, operation_ids: List[int], span_size_mode: str = "mixed") -> Dict[str, Any]:
        """Analyze prompt generation statistics for a set of operation IDs.
        
        :param operation_ids: List of operation IDs to analyze
        :type operation_ids: List[int]
        :param span_size_mode: Span size mode for generation
        :type span_size_mode: str
        :return: Statistics about generated prompts
        :rtype: Dict[str, Any]
        
        Example:
            >>> generator = PromptGenerator()
            >>> stats = generator.get_prompt_statistics(
            ...     operation_ids=list(range(100)),
            ...     span_size_mode="mixed"
            ... )
            >>> print(f"Domain distribution: {stats['domain_distribution']}")
        """
        domain_counts = {}
        size_counts = {}
        complexity_counts = {}
        total_prompts = len(operation_ids)
        
        for op_id in operation_ids:
            _, scenario = self.generate_prompt(op_id, span_size_mode)
            
            # Count domains
            domain = scenario.domain.value
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # Count sizes
            size = scenario.span_size.value
            size_counts[size] = size_counts.get(size, 0) + 1
            
            # Count complexity
            complexity = scenario.complexity
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        # Calculate distributions
        domain_distribution = {k: (v / total_prompts) * 100 for k, v in domain_counts.items()}
        size_distribution = {k: (v / total_prompts) * 100 for k, v in size_counts.items()}
        complexity_distribution = {k: (v / total_prompts) * 100 for k, v in complexity_counts.items()}
        
        return {
            'total_prompts': total_prompts,
            'domain_distribution': domain_distribution,
            'size_distribution': size_distribution,
            'complexity_distribution': complexity_distribution,
            'domain_counts': domain_counts,
            'size_counts': size_counts,
            'complexity_counts': complexity_counts,
            'span_size_mode': span_size_mode,
            'base_seed': self.base_seed,
        }
    
    def reset_cache(self) -> None:
        """Clear the prompt generation cache."""
        self._prompt_cache.clear()
        logger.debug("🎲 Prompt cache cleared")
    
    def set_seed(self, new_seed: int) -> None:
        """Update the base seed for prompt generation.
        
        :param new_seed: New base seed value
        :type new_seed: int
        """
        self.base_seed = new_seed
        self.reset_cache()  # Clear cache since seed changed
        logger.debug(f"🎲 Base seed updated to {new_seed}")
    
    def validate_determinism(self, operation_id: int, iterations: int = 5) -> bool:
        """Validate that prompt generation is deterministic.
        
        :param operation_id: Operation ID to test
        :type operation_id: int
        :param iterations: Number of iterations to test
        :type iterations: int
        :return: True if all iterations produce identical results
        :rtype: bool
        
        Example:
            >>> generator = PromptGenerator(seed=42)
            >>> is_deterministic = generator.validate_determinism(
            ...     operation_id=100,
            ...     iterations=10
            ... )
            >>> print(f"Deterministic: {is_deterministic}")
        """
        first_prompt, first_scenario = self.generate_prompt(operation_id)
        
        for i in range(1, iterations):
            prompt, scenario = self.generate_prompt(operation_id)
            if prompt != first_prompt or scenario != first_scenario:
                logger.error(f"Determinism validation failed at iteration {i}")
                return False
        
        logger.debug(f"🎲 Determinism validated for op_id={operation_id} ({iterations} iterations)")
        return True
