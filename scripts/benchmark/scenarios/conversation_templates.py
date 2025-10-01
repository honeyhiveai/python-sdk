"""
Conversation Templates Module

This module provides realistic conversation scenarios for tracer performance
benchmarks with varying complexity, turn counts, and span sizes. Follows
Agent OS production code standards.
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SpanSize(Enum):
    """Span size categories for testing different telemetry loads."""
    SMALL = "small"      # 1000-2000 tokens
    MEDIUM = "medium"    # 2000-5000 tokens  
    LARGE = "large"      # 5000-10000 tokens


class ConversationDomain(Enum):
    """Conversation domain categories for realistic scenario variation."""
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class ConversationScenario:
    """A conversation scenario template for benchmark testing.
    
    :param domain: The conversation domain/category
    :type domain: ConversationDomain
    :param complexity: Complexity level (low, medium, high)
    :type complexity: str
    :param expected_turns: Expected number of conversation turns
    :type expected_turns: int
    :param span_size: Expected span size category
    :type span_size: SpanSize
    :param prompt_template: Template for generating prompts
    :type prompt_template: str
    :param context_template: Optional context setup template
    :type context_template: Optional[str]
    :param expected_tokens: Expected token count range
    :type expected_tokens: tuple[int, int]
    :param description: Human-readable description of the scenario
    :type description: str
    
    Example:
        >>> scenario = ConversationScenario(
        ...     domain=ConversationDomain.TECHNICAL,
        ...     complexity="medium",
        ...     expected_turns=3,
        ...     span_size=SpanSize.MEDIUM,
        ...     prompt_template="Explain {topic} in {detail_level} detail",
        ...     expected_tokens=(200, 400)
        ... )
    """
    domain: ConversationDomain
    complexity: str
    expected_turns: int
    span_size: SpanSize
    prompt_template: str
    context_template: Optional[str] = None
    expected_tokens: tuple[int, int] = (100, 300)
    description: str = ""


class ConversationTemplates:
    """Repository of conversation templates for realistic benchmark scenarios.
    
    Provides a comprehensive set of conversation templates across different
    domains, complexity levels, and span sizes to ensure realistic and
    varied testing scenarios.
    
    Example:
        >>> templates = ConversationTemplates()
        >>> scenario = templates.get_scenario_by_size(SpanSize.LARGE)
        >>> prompt = templates.generate_prompt(scenario, operation_id=42)
    """
    
    def __init__(self) -> None:
        """Initialize conversation templates repository."""
        self._scenarios = self._build_scenario_library()
        logger.debug(f"🎭 ConversationTemplates initialized with {len(self._scenarios)} scenarios")
    
    def _build_scenario_library(self) -> List[ConversationScenario]:
        """Build the comprehensive library of conversation scenarios.
        
        :return: List of all available conversation scenarios
        :rtype: List[ConversationScenario]
        """
        scenarios = []
        
        # SMALL SPAN SCENARIOS (1000-2000 tokens)
        scenarios.extend([
            ConversationScenario(
                domain=ConversationDomain.FACTUAL,
                complexity="low",
                expected_turns=1,
                span_size=SpanSize.SMALL,
                prompt_template="Provide a comprehensive explanation of {topic}, including its key principles, applications, and real-world examples. Cover the fundamental concepts, historical development, current state, and practical implications for users.",
                expected_tokens=(1000, 1500),
                description="Comprehensive factual explanation with examples and context"
            ),
            ConversationScenario(
                domain=ConversationDomain.TECHNICAL,
                complexity="low", 
                expected_turns=2,
                span_size=SpanSize.SMALL,
                prompt_template="Provide a detailed step-by-step guide on how to {action} in {technology}. Include prerequisites, detailed instructions, common pitfalls to avoid, troubleshooting tips, best practices, and example code or configurations where applicable.",
                expected_tokens=(1200, 1800),
                description="Detailed technical tutorial with examples and best practices"
            ),
            ConversationScenario(
                domain=ConversationDomain.CREATIVE,
                complexity="low",
                expected_turns=1,
                span_size=SpanSize.SMALL,
                prompt_template="Write a detailed {length} {type} about {topic}. Include rich descriptions, character development, dialogue, setting details, and a compelling narrative arc. Make it engaging and immersive for the reader.",
                expected_tokens=(1100, 1700),
                description="Detailed creative writing with rich descriptions and narrative"
            ),
        ])
        
        # MEDIUM SPAN SCENARIOS (2000-5000 tokens)
        scenarios.extend([
            ConversationScenario(
                domain=ConversationDomain.TECHNICAL,
                complexity="medium",
                expected_turns=3,
                span_size=SpanSize.MEDIUM,
                prompt_template="Provide a comprehensive technical deep-dive into the architecture of {system}, explaining how {component1} interacts with {component2}. Include detailed diagrams, data flow explanations, API specifications, security considerations, performance implications, scalability factors, monitoring strategies, and real-world implementation examples with code samples.",
                expected_tokens=(2200, 3500),
                description="Comprehensive technical architecture deep-dive with implementation details"
            ),
            ConversationScenario(
                domain=ConversationDomain.ANALYTICAL,
                complexity="medium",
                expected_turns=4,
                span_size=SpanSize.MEDIUM,
                prompt_template="Conduct a thorough comparative analysis of {approach1} versus {approach2} for {use_case}. Include detailed pros and cons, performance benchmarks, cost analysis, implementation complexity, maintenance requirements, scalability considerations, security implications, vendor lock-in risks, migration strategies, and provide specific recommendations with supporting evidence and case studies.",
                expected_tokens=(2500, 4000),
                description="Comprehensive comparative analysis with benchmarks and case studies"
            ),
            ConversationScenario(
                domain=ConversationDomain.TROUBLESHOOTING,
                complexity="medium",
                expected_turns=5,
                span_size=SpanSize.MEDIUM,
                prompt_template="I'm experiencing {problem} with the error '{error_message}'. Provide a comprehensive troubleshooting guide including root cause analysis, step-by-step diagnostic procedures, multiple solution approaches, prevention strategies, monitoring recommendations, and detailed explanations of why each solution works.",
                context_template="System: {system}, Version: {version}, Environment: {environment}",
                expected_tokens=(2800, 4500),
                description="Comprehensive troubleshooting guide with root cause analysis"
            ),
        ])
        
        # LARGE SPAN SCENARIOS (5000-10000 tokens)
        scenarios.extend([
            ConversationScenario(
                domain=ConversationDomain.TECHNICAL,
                complexity="high",
                expected_turns=6,
                span_size=SpanSize.LARGE,
                prompt_template="Design and document a complete enterprise-grade {system_type} system for {use_case}. Provide detailed system architecture with microservices breakdown, comprehensive data flow diagrams, API specifications, database schemas, security architecture, error handling strategies, monitoring and alerting systems, scalability and performance optimization plans, disaster recovery procedures, deployment strategies across multiple environments, CI/CD pipeline design, infrastructure as code templates, cost optimization strategies, compliance considerations, and a complete implementation roadmap with timelines and resource requirements.",
                expected_tokens=(5500, 8000),
                description="Enterprise system design with complete technical documentation"
            ),
            ConversationScenario(
                domain=ConversationDomain.CREATIVE,
                complexity="high",
                expected_turns=4,
                span_size=SpanSize.LARGE,
                prompt_template="Write an extensive {genre} story about {character} who must {challenge}. Create a rich, immersive narrative with detailed character development, complex plot progression, multiple subplots, rich world-building, authentic dialogue, emotional depth, symbolic elements, thematic exploration, and a deeply satisfying resolution. Include detailed descriptions of settings, character backstories, internal monologues, and explore the psychological journey of the protagonist.",
                expected_tokens=(6000, 9000),
                description="Extensive creative writing with rich world-building and character development"
            ),
            ConversationScenario(
                domain=ConversationDomain.ANALYTICAL,
                complexity="high",
                expected_turns=5,
                span_size=SpanSize.LARGE,
                prompt_template="Conduct an exhaustive research analysis of {topic} including comprehensive historical context, detailed examination of the current state with statistical data, identification and analysis of key challenges with root cause analysis, evaluation of multiple potential solutions with feasibility studies, risk assessments, cost-benefit analyses, stakeholder impact assessments, implementation strategies, success metrics, and detailed future implications with scenario planning and trend analysis.",
                expected_tokens=(7000, 10000),
                description="Exhaustive research analysis with comprehensive data and projections"
            ),
        ])
        
        return scenarios
    
    def get_all_scenarios(self) -> List[ConversationScenario]:
        """Get all available conversation scenarios.
        
        :return: List of all conversation scenarios
        :rtype: List[ConversationScenario]
        """
        return self._scenarios.copy()
    
    def get_scenarios_by_size(self, span_size: SpanSize) -> List[ConversationScenario]:
        """Get scenarios filtered by span size category.
        
        :param span_size: Target span size category
        :type span_size: SpanSize
        :return: List of scenarios matching the span size
        :rtype: List[ConversationScenario]
        
        Example:
            >>> templates = ConversationTemplates()
            >>> large_scenarios = templates.get_scenarios_by_size(SpanSize.LARGE)
            >>> print(f"Found {len(large_scenarios)} large span scenarios")
        """
        return [s for s in self._scenarios if s.span_size == span_size]
    
    def get_scenarios_by_domain(self, domain: ConversationDomain) -> List[ConversationScenario]:
        """Get scenarios filtered by conversation domain.
        
        :param domain: Target conversation domain
        :type domain: ConversationDomain
        :return: List of scenarios matching the domain
        :rtype: List[ConversationScenario]
        """
        return [s for s in self._scenarios if s.domain == domain]
    
    def get_scenarios_by_complexity(self, complexity: str) -> List[ConversationScenario]:
        """Get scenarios filtered by complexity level.
        
        :param complexity: Target complexity level (low, medium, high)
        :type complexity: str
        :return: List of scenarios matching the complexity
        :rtype: List[ConversationScenario]
        """
        return [s for s in self._scenarios if s.complexity == complexity]
    
    def get_scenario_by_index(self, index: int) -> ConversationScenario:
        """Get scenario by index for deterministic selection.
        
        :param index: Index of the scenario to retrieve
        :type index: int
        :return: Conversation scenario at the specified index
        :rtype: ConversationScenario
        :raises IndexError: If index is out of range
        
        Example:
            >>> templates = ConversationTemplates()
            >>> scenario = templates.get_scenario_by_index(5)
            >>> print(scenario.description)
        """
        if not 0 <= index < len(self._scenarios):
            raise IndexError(f"Scenario index {index} out of range (0-{len(self._scenarios)-1})")
        return self._scenarios[index]
    
    def generate_prompt(self, scenario: ConversationScenario, operation_id: int, **kwargs: Any) -> str:
        """Generate a concrete prompt from a scenario template.
        
        :param scenario: The conversation scenario template
        :type scenario: ConversationScenario
        :param operation_id: Operation ID for deterministic parameter selection
        :type operation_id: int
        :param kwargs: Additional template parameters
        :type kwargs: Any
        :return: Generated prompt string
        :rtype: str
        
        Example:
            >>> templates = ConversationTemplates()
            >>> scenario = templates.get_scenario_by_index(0)
            >>> prompt = templates.generate_prompt(scenario, operation_id=42)
        """
        # Use operation_id for deterministic parameter selection
        import random
        random.seed(operation_id)
        
        # Generate parameters based on scenario domain and complexity
        template_params = self._generate_template_parameters(scenario, operation_id)
        template_params.update(kwargs)
        
        try:
            # Generate the main prompt
            prompt = scenario.prompt_template.format(**template_params)
            
            # Add context if available
            if scenario.context_template:
                context = scenario.context_template.format(**template_params)
                prompt = f"Context: {context}\n\nQuestion: {prompt}"
            
            logger.debug(f"🎭 Generated prompt for {scenario.domain.value} scenario (op_id={operation_id})")
            return prompt
            
        except KeyError as e:
            logger.error(f"Missing template parameter: {e}")
            # Fallback to simple prompt
            return f"Please help with a {scenario.domain.value} question (operation {operation_id})"
    
    def _generate_template_parameters(self, scenario: ConversationScenario, operation_id: int) -> Dict[str, str]:
        """Generate template parameters based on scenario and operation ID.
        
        :param scenario: The conversation scenario
        :type scenario: ConversationScenario
        :param operation_id: Operation ID for deterministic selection
        :type operation_id: int
        :return: Dictionary of template parameters
        :rtype: Dict[str, str]
        """
        import random
        random.seed(operation_id)
        
        # Domain-specific parameter pools
        parameters = {
            ConversationDomain.TECHNICAL: {
                'topic': ['REST APIs', 'microservices', 'database indexing', 'caching strategies', 'load balancing'],
                'technology': ['Python', 'JavaScript', 'Docker', 'Kubernetes', 'PostgreSQL'],
                'action': ['deploy', 'configure', 'optimize', 'debug', 'monitor'],
                'system': ['distributed cache', 'message queue', 'API gateway', 'monitoring system'],
                'component1': ['load balancer', 'database', 'cache layer', 'authentication service'],
                'component2': ['application server', 'message broker', 'storage system', 'logging service'],
                'system_type': ['monitoring', 'e-commerce', 'analytics', 'messaging'],
                'use_case': ['high-traffic web application', 'real-time data processing', 'user authentication'],
                'problem': ['connection timeouts', 'memory leaks', 'slow queries', 'authentication failures'],
                'error_message': ['Connection refused', 'Out of memory', 'Query timeout', 'Invalid credentials'],
                'system': ['Ubuntu 20.04', 'Docker Swarm', 'Kubernetes cluster', 'AWS ECS'],
                'version': ['v2.1.3', 'v1.8.0', 'v3.0.1', 'v2.5.2'],
                'environment': ['production', 'staging', 'development', 'testing'],
            },
            ConversationDomain.CREATIVE: {
                'length': ['short', 'medium-length', 'brief', 'concise'],
                'type': ['story', 'poem', 'dialogue', 'description'],
                'topic': ['space exploration', 'time travel', 'artificial intelligence', 'underwater cities'],
                'character': ['a young scientist', 'an experienced detective', 'a curious child', 'a wise elder'],
                'challenge': ['solve a mystery', 'save their community', 'discover a secret', 'overcome their fears'],
                'genre': ['science fiction', 'mystery', 'adventure', 'fantasy'],
            },
            ConversationDomain.FACTUAL: {
                'topic': ['photosynthesis', 'the water cycle', 'renewable energy', 'machine learning', 'blockchain'],
            },
            ConversationDomain.ANALYTICAL: {
                'approach1': ['microservices', 'monolithic architecture', 'serverless functions', 'container orchestration'],
                'approach2': ['traditional deployment', 'cloud-native solutions', 'hybrid architecture', 'edge computing'],
                'use_case': ['e-commerce platform', 'real-time analytics', 'content delivery', 'user authentication'],
                'topic': ['remote work trends', 'sustainable technology', 'AI ethics', 'cybersecurity challenges'],
            },
            ConversationDomain.TROUBLESHOOTING: {
                'problem': ['application crashes', 'slow performance', 'connection issues', 'data inconsistency'],
                'error_message': ['Segmentation fault', 'Connection timeout', 'Invalid JSON', 'Permission denied'],
                'system': ['Linux server', 'Docker container', 'Kubernetes pod', 'AWS instance'],
                'version': ['v2.1', 'v3.0', 'v1.8', 'v2.5'],
                'environment': ['production', 'staging', 'development', 'testing'],
            },
        }
        
        # Get parameters for this scenario's domain
        domain_params = parameters.get(scenario.domain, {})
        
        # Generate deterministic parameter selection
        result = {}
        for param_name, options in domain_params.items():
            if options:
                selected = random.choice(options)
                result[param_name] = selected
        
        # Add common parameters
        result.update({
            'detail_level': random.choice(['basic', 'intermediate', 'detailed', 'comprehensive']),
            'complexity_level': scenario.complexity,
            'operation_id': str(operation_id),
        })
        
        return result
    
    def get_scenario_statistics(self) -> Dict[str, Any]:
        """Get statistics about the scenario library.
        
        :return: Dictionary with scenario library statistics
        :rtype: Dict[str, Any]
        """
        stats = {
            'total_scenarios': len(self._scenarios),
            'by_span_size': {},
            'by_domain': {},
            'by_complexity': {},
            'token_ranges': {},
        }
        
        # Count by span size
        for size in SpanSize:
            count = len(self.get_scenarios_by_size(size))
            stats['by_span_size'][size.value] = count
        
        # Count by domain
        for domain in ConversationDomain:
            count = len(self.get_scenarios_by_domain(domain))
            stats['by_domain'][domain.value] = count
        
        # Count by complexity
        for complexity in ['low', 'medium', 'high']:
            count = len(self.get_scenarios_by_complexity(complexity))
            stats['by_complexity'][complexity] = count
        
        # Token range analysis
        for scenario in self._scenarios:
            size_key = scenario.span_size.value
            if size_key not in stats['token_ranges']:
                stats['token_ranges'][size_key] = {
                    'min_tokens': scenario.expected_tokens[0],
                    'max_tokens': scenario.expected_tokens[1],
                    'scenarios': 1
                }
            else:
                stats['token_ranges'][size_key]['min_tokens'] = min(
                    stats['token_ranges'][size_key]['min_tokens'],
                    scenario.expected_tokens[0]
                )
                stats['token_ranges'][size_key]['max_tokens'] = max(
                    stats['token_ranges'][size_key]['max_tokens'],
                    scenario.expected_tokens[1]
                )
                stats['token_ranges'][size_key]['scenarios'] += 1
        
        return stats
    
    def get_max_expected_tokens(self) -> int:
        """Get the maximum expected tokens across all conversation scenarios.
        
        :return: Maximum expected tokens from all scenarios
        :rtype: int
        
        Example:
            >>> templates = ConversationTemplates()
            >>> max_tokens = templates.get_max_expected_tokens()
            >>> print(f"Max expected tokens: {max_tokens}")
        """
        if not self._scenarios:
            return 2000  # Fallback default
        
        max_tokens = max(scenario.expected_tokens[1] for scenario in self._scenarios)
        return max_tokens
