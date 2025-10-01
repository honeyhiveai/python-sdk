"""
Universal LLM Discovery Engine v4.0 - Core Processing Engine

O(1) provider detection and data extraction using pre-compiled bundles.
This is the main processing engine that handles:
1. O(1) provider detection using frozenset operations
2. Compiled extraction function execution
3. HoneyHive schema mapping
4. Fallback processing for unknown providers

Graceful Degradation Compliance:
- Uses safe_log for all logging to prevent host application crashes
- Never propagates exceptions to host application
- Provides fallback behavior for all failure scenarios
- Handles non-dict inputs gracefully
"""

import time
from typing import Dict, Any, Optional, FrozenSet, List, Callable, Set, Tuple
from pathlib import Path

from .bundle_loader import DevelopmentAwareBundleLoader
from ....utils.logger import safe_log


class UniversalProviderProcessor:
    """Core processing engine for Universal LLM Discovery Engine v4.0."""

    def __init__(
        self,
        bundle_loader: Optional[DevelopmentAwareBundleLoader] = None,
        tracer_instance: Optional[Any] = None,
    ):
        """
        Initialize the universal provider processor.

        Args:
            bundle_loader: Optional bundle loader. If None, will create default loader.
            tracer_instance: Optional tracer instance for safe logging.
        """
        self.tracer_instance = tracer_instance
        self.bundle_loader = bundle_loader or self._create_default_bundle_loader()
        self.bundle = None
        self.provider_signatures = {}  # Forward index: provider → [signatures]
        self.signature_to_provider = (
            {}
        )  # NEW: Inverted index: signature → (provider, confidence)
        self.extraction_functions = {}
        self.field_mappings = {}
        self.transform_registry = {}
        self.validation_rules = {}

        # Performance monitoring
        self.performance_stats = {
            "total_processed": 0,
            "provider_detections": {},
            "fallback_usage": 0,
            "processing_times": [],
            "errors": 0,
        }

        # Load bundle with graceful degradation
        self._load_bundle()

    def _create_default_bundle_loader(self) -> Optional[DevelopmentAwareBundleLoader]:
        """Create default bundle loader with standard paths."""

        try:
            current_dir = Path(__file__).parent
            bundle_path = current_dir / "compiled_providers.pkl"
            source_path = (
                current_dir.parent.parent.parent.parent.parent / "config" / "dsl"
            )

            return DevelopmentAwareBundleLoader(
                bundle_path=bundle_path,
                source_path=source_path if source_path.exists() else None,
                tracer_instance=self.tracer_instance,
            )
        except Exception as e:
            safe_log(
                self.tracer_instance,
                "warning",
                "Failed to create default bundle loader: %s",
                e,
            )
            return None

    def _load_bundle(self):
        """Load and prepare provider bundle with graceful degradation."""

        try:
            # Check if bundle loader is available
            if not self.bundle_loader:
                safe_log(
                    self.tracer_instance,
                    "warning",
                    "No bundle loader available, using fallback mode",
                )
                return

            start_time = time.perf_counter()

            # Load bundle through bundle loader
            self.bundle = self.bundle_loader.load_provider_bundle()

            # Extract components with fallbacks
            self.provider_signatures = getattr(self.bundle, "provider_signatures", {})
            self.field_mappings = getattr(self.bundle, "field_mappings", {})
            self.transform_registry = getattr(self.bundle, "transform_registry", {})
            self.validation_rules = getattr(self.bundle, "validation_rules", {})

            # NEW: Load inverted index for O(1) exact match detection
            if hasattr(self.bundle, "signature_to_provider"):
                self.signature_to_provider = self.bundle.signature_to_provider
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Loaded inverted signature index with %d entries",
                    len(self.signature_to_provider),
                )
            else:
                # Fallback: build inverted index at runtime (legacy compatibility)
                safe_log(
                    self.tracer_instance,
                    "warning",
                    "Bundle missing inverted index, building at runtime (legacy mode)",
                )
                self.signature_to_provider = self._build_inverted_index_fallback()

            # Get compiled extraction functions
            self.extraction_functions = {}
            for provider_name in self.provider_signatures.keys():
                try:
                    func = self.bundle_loader.get_extraction_function(provider_name)
                    if func:
                        self.extraction_functions[provider_name] = func
                    else:
                        safe_log(
                            self.tracer_instance,
                            "warning",
                            "No extraction function available for provider: %s",
                            provider_name,
                        )
                except Exception as e:
                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "Failed to get extraction function for %s: %s",
                        provider_name,
                        e,
                    )

            load_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

            safe_log(
                self.tracer_instance,
                "info",
                "Loaded Universal LLM Discovery Engine v4.0",
            )
            safe_log(
                self.tracer_instance,
                "info",
                "  Providers: %d",
                len(self.provider_signatures),
            )
            safe_log(
                self.tracer_instance,
                "info",
                "  Total signatures: %d",
                sum(len(sigs) for sigs in self.provider_signatures.values()),
            )
            safe_log(self.tracer_instance, "info", "  Load time: %.2fms", load_time)

        except Exception as e:
            safe_log(
                self.tracer_instance, "warning", "Failed to load provider bundle: %s", e
            )
            # Continue with empty configurations - graceful degradation
            self.provider_signatures = {}
            self.field_mappings = {}
            self.transform_registry = {}
            self.validation_rules = {}
            self.extraction_functions = {}

    def process_span_attributes(self, attributes: Any) -> Dict[str, Any]:
        """
        Main processing entry point with graceful degradation.

        Convert span attributes to HoneyHive schema using O(1) provider detection.
        Handles non-dict inputs gracefully and never crashes host application.

        Args:
            attributes: Raw span attributes from instrumentor (expected to be dict)

        Returns:
            Dict with HoneyHive schema structure (inputs, outputs, config, metadata)
        """

        # Graceful handling of non-dict inputs
        if not isinstance(attributes, dict):
            safe_log(
                self.tracer_instance,
                "debug",
                "Non-dict attributes received: %s",
                type(attributes),
            )
            return self._fallback_processing({})

        start_time = time.perf_counter()

        try:
            # Step 1: Two-Tier Detection (Instrumentor + Provider)
            instrumentor, provider = self._detect_instrumentor_and_provider(attributes)

            # Update stats
            self.performance_stats["total_processed"] += 1

            if provider == "unknown":
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "No provider detected (instrumentor: %s), using fallback processing",
                    instrumentor,
                )
                self.performance_stats["fallback_usage"] += 1
                result = self._fallback_processing(attributes)
            else:
                # Update provider detection stats
                if provider not in self.performance_stats["provider_detections"]:
                    self.performance_stats["provider_detections"][provider] = 0
                self.performance_stats["provider_detections"][provider] += 1

                # Step 2: O(1) Data Extraction (with instrumentor-aware routing)
                result = self._extract_provider_data(provider, attributes, instrumentor)

            # Step 3: Validation and Enhancement
            validated_result = self._validate_and_enhance(result, provider)

            # Record processing time
            processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            self.performance_stats["processing_times"].append(processing_time)

            safe_log(
                self.tracer_instance,
                "debug",
                "Successfully processed span data using %s provider in %.4fms",
                provider,
                processing_time,
            )

            return validated_result

        except Exception as e:
            self.performance_stats["errors"] += 1
            safe_log(self.tracer_instance, "debug", "Span processing failed: %s", e)

            # Return fallback result on error - never crash host application
            return self._fallback_processing(
                attributes if isinstance(attributes, dict) else {}
            )

    def _detect_provider(self, attributes: Dict[str, Any]) -> str:
        """
        Two-tier detection: Instrumentor + Provider.

        TIER 1: Instrumentor Detection (Semantic Convention Layer)
        - Detects: OpenInference, Traceloop, OpenLit, Direct OTel
        - Based on: Attribute structure and naming patterns
        - Purpose: Route to correct semantic convention mapping

        TIER 2: Provider Detection (LLM Provider Layer)
        - Detects: OpenAI, Anthropic, Gemini
        - Based on: Explicit provider fields and model patterns
        - Purpose: Route to provider-specific response handling

        Performance:
        - Exact match: O(1) via hash table lookup (for non-wildcard signatures)
        - Dynamic normalization: O(n) where n = number of attributes
        - Wildcard match: O(signatures × fields) for patterns with wildcards
        - Subset match: O(log n) via size-based bucketing fallback

        Dynamic Logic:
        - Analyzes attribute structure to detect arrays/objects
        - Reconstructs patterns from flattened keys (e.g., "llm.input_messages.0" → "llm.input_messages.*")
        - Enables structural matching, not just literal string matching

        Args:
            attributes: Span attributes to analyze

        Returns:
            Provider name or 'unknown' (for backward compatibility, returns provider only)
            
        Note: Internally detects both instrumentor and provider, but current API returns
        provider for backward compatibility. Use _detect_instrumentor_and_provider() for full info.
        """
        # Delegate to two-tier detection and return only provider for backward compatibility
        instrumentor, provider = self._detect_instrumentor_and_provider(attributes)
        return provider

    def _detect_instrumentor_and_provider(self, attributes: Dict[str, Any]) -> Tuple[str, str]:
        """
        Two-tier detection returning both instrumentor and provider.
        
        Returns:
            Tuple of (instrumentor, provider) where:
            - instrumentor: traceloop, openinference, openlit, direct_otel, or unknown
            - provider: openai, anthropic, gemini, or unknown
        """
        if not attributes:
            safe_log(self.tracer_instance, "debug", "No attributes, returning unknown")
            return ("unknown", "unknown")

        # Dynamic attribute normalization: reconstruct structural patterns from flattened keys
        normalized_keys = self._normalize_attribute_keys(attributes.keys())
        
        attribute_keys = frozenset(attributes.keys())
        normalized_frozenset = frozenset(normalized_keys)

        # Step 1: O(1) exact match lookup via inverted index (original keys)
        if attribute_keys in self.signature_to_provider:
            pattern_name, confidence = self.signature_to_provider[attribute_keys]
            instrumentor, provider = self._parse_pattern_name(pattern_name)
            safe_log(
                self.tracer_instance,
                "debug",
                "✅ Exact signature match: %s → [%s, %s] (confidence: %.2f) in O(1) time",
                pattern_name,
                instrumentor,
                provider,
                confidence,
            )
            return (instrumentor, provider)

        # Step 2: O(1) exact match lookup with normalized keys (for wildcard patterns)
        if normalized_frozenset in self.signature_to_provider:
            pattern_name, confidence = self.signature_to_provider[normalized_frozenset]
            instrumentor, provider = self._parse_pattern_name(pattern_name)
            safe_log(
                self.tracer_instance,
                "debug",
                "✅ Normalized signature match: %s → [%s, %s] (confidence: %.2f) in O(1) time",
                pattern_name,
                instrumentor,
                provider,
                confidence,
            )
            return (instrumentor, provider)

        # Step 3: Wildcard signature matching (for complex patterns)
        wildcard_pattern = self._match_wildcard_signatures(normalized_keys, attributes)
        if wildcard_pattern != "unknown":
            instrumentor, provider = self._parse_pattern_name(wildcard_pattern)
            return (instrumentor, provider)

        # Step 4: O(log n) subset match (prioritized before value-based detection)
        # Pass attributes for value-based tiebreaking when multiple patterns match
        safe_log(
            self.tracer_instance,
            "debug",
            "No exact or wildcard match, trying subset matching",
        )
        subset_pattern = self._find_best_subset_match(normalized_frozenset, attributes)
        
        # If subset matching found a specific pattern, use it
        if subset_pattern != "unknown":
            instrumentor, provider = self._parse_pattern_name(subset_pattern)
            safe_log(
                self.tracer_instance,
                "debug",
                "✅ Subset match: %s → [%s, %s]",
                subset_pattern,
                instrumentor,
                provider,
            )
            return (instrumentor, provider)

        # Step 5: Dynamic value-based detection fallback (last resort)
        instrumentor = self._detect_instrumentor(attributes)
        provider = self._detect_provider_by_values(attributes)
        
        if provider != "unknown":
            safe_log(
                self.tracer_instance,
                "debug",
                "✅ Value-based detection: [%s, %s] (explicit provider indicator found)",
                instrumentor,
                provider,
            )
            return (instrumentor, provider)

        # No match found
        return (instrumentor, "unknown")

    def _parse_pattern_name(self, pattern_name: str) -> Tuple[str, str]:
        """
        Parse compound pattern name into instrumentor and provider.
        
        Pattern names follow the convention: {instrumentor}_{provider}
        Examples:
        - "traceloop_openai" → ("traceloop", "openai")
        - "openinference_anthropic" → ("openinference", "anthropic")
        - "direct_gemini" → ("direct", "gemini")
        - "openai" → ("unknown", "openai")  # fallback for simple names
        - "unknown" → ("unknown", "unknown")
        
        Args:
            pattern_name: Pattern name from structure_patterns.yaml
            
        Returns:
            Tuple of (instrumentor, provider)
        """
        if pattern_name == "unknown":
            return ("unknown", "unknown")
        
        # Split on first underscore
        parts = pattern_name.split("_", 1)
        
        if len(parts) == 2:
            instrumentor, provider = parts
            return (instrumentor, provider)
        else:
            # No underscore - assume it's just a provider name
            return ("unknown", pattern_name)

    def _detect_instrumentor(self, attributes: Dict[str, Any]) -> str:
        """
        Detect instrumentor framework from attribute patterns.
        
        TIER 1: Instrumentor Detection (Semantic Convention Layer)
        
        Instrumentors use different attribute naming patterns:
        - Traceloop: gen_ai.* (OpenTelemetry GenAI semantic conventions)
        - OpenInference: llm.* (Arize OpenInference)
        - OpenLit: openlit.* (OpenLIT specific)
        - Direct OTel: Custom attribute patterns
        
        This is purely pattern-based detection using attribute key prefixes.
        
        Args:
            attributes: Span attributes to analyze
            
        Returns:
            Instrumentor name: traceloop, openinference, openlit, direct_otel, or unknown
        """
        if not attributes:
            return "unknown"
        
        # Count attribute prefixes
        prefix_counts = {
            "traceloop": 0,
            "openinference": 0,
            "openlit": 0,
            "direct_otel": 0,
        }
        
        for key in attributes.keys():
            if key.startswith("gen_ai."):
                prefix_counts["traceloop"] += 1
            elif key.startswith("llm."):
                prefix_counts["openinference"] += 1
            elif key.startswith("openlit."):
                prefix_counts["openlit"] += 1
            elif key.startswith("otel.") or key.startswith("custom."):
                prefix_counts["direct_otel"] += 1
        
        # Return instrumentor with highest count
        max_count = max(prefix_counts.values())
        if max_count == 0:
            return "unknown"
        
        for instrumentor, count in prefix_counts.items():
            if count == max_count:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Detected instrumentor: %s (%d matching attributes)",
                    instrumentor,
                    count,
                )
                return instrumentor
        
        return "unknown"

    def _detect_provider_by_values(self, attributes: Dict[str, Any]) -> str:
        """
        Detect provider by analyzing attribute VALUES for explicit provider indicators.
        
        This implements FULL DYNAMIC LOGIC by examining actual data content, not just keys.
        
        Dynamic Analysis:
        - Checks explicit provider fields (e.g., gen_ai.system, llm.provider)
        - Analyzes model names for provider-specific patterns
        - Examines API endpoints and URLs
        - Validates provider consistency across multiple indicators
        
        This solves the signature collision problem where multiple providers share
        generic field names (e.g., both OpenAI and Anthropic use gen_ai.system).
        
        Priority Order:
        1. Explicit provider fields with known values
        2. Provider-specific model name patterns
        3. API endpoint patterns
        
        Performance: O(n) where n = number of provider indicator fields checked
        
        Args:
            attributes: Span attributes to analyze
            
        Returns:
            Provider name if explicitly detected, 'unknown' otherwise
        """
        # Define provider indicator fields and their expected values
        provider_indicators = {
            "openai": {
                "explicit_fields": {
                    "gen_ai.system": ["openai", "OpenAI", "OPENAI"],
                    "llm.provider": ["openai", "OpenAI", "OPENAI"],
                    "openlit.provider": ["openai", "OpenAI", "OPENAI"],
                },
                "model_patterns": ["gpt-", "text-davinci", "text-embedding"],
                "url_patterns": ["api.openai.com", "openai.com"],
            },
            "anthropic": {
                "explicit_fields": {
                    "gen_ai.system": ["anthropic", "Anthropic", "ANTHROPIC"],
                    "llm.provider": ["anthropic", "Anthropic", "ANTHROPIC"],
                    "openlit.provider": ["anthropic", "Anthropic", "ANTHROPIC"],
                },
                "model_patterns": ["claude-"],
                "url_patterns": ["api.anthropic.com", "anthropic.com"],
            },
            "gemini": {
                "explicit_fields": {
                    "gen_ai.system": ["google", "Google", "GOOGLE", "gemini", "Gemini"],
                    "llm.provider": ["google", "Google", "gemini", "Gemini"],
                    "openlit.provider": ["google", "Google", "GOOGLE", "gemini", "Gemini"],
                },
                "model_patterns": ["gemini-", "models/gemini"],
                "url_patterns": ["generativelanguage.googleapis.com", "ai.google.dev"],
            },
        }
        
        best_match = "unknown"
        best_score = 0
        
        # Check each provider's indicators
        for provider, indicators in provider_indicators.items():
            score = 0
            
            # Check explicit provider fields (highest priority)
            for field, expected_values in indicators["explicit_fields"].items():
                if field in attributes:
                    value = str(attributes[field]).strip()
                    if value in expected_values:
                        score += 100  # Strong signal - explicit provider match
                        safe_log(
                            self.tracer_instance,
                            "debug",
                            "Found explicit provider indicator: %s = %s → %s",
                            field,
                            value,
                            provider,
                        )
            
            # Check model name patterns (medium priority)
            model_fields = ["gen_ai.request.model", "llm.model_name", "llm.model", "model"]
            for field in model_fields:
                if field in attributes:
                    model = str(attributes[field]).lower()
                    for pattern in indicators["model_patterns"]:
                        if pattern.lower() in model:
                            score += 50  # Medium signal - model pattern match
                            safe_log(
                                self.tracer_instance,
                                "debug",
                                "Found model pattern %s in %s → %s",
                                pattern,
                                model,
                                provider,
                            )
                            break
            
            # Check URL patterns (lower priority)
            url_fields = ["http.url", "server.address", "url.full", "http.target"]
            for field in url_fields:
                if field in attributes:
                    url = str(attributes[field]).lower()
                    for pattern in indicators["url_patterns"]:
                        if pattern.lower() in url:
                            score += 30  # Lower signal - URL pattern match
                            safe_log(
                                self.tracer_instance,
                                "debug",
                                "Found URL pattern %s in %s → %s",
                                pattern,
                                url,
                                provider,
                            )
                            break
            
            # Update best match if this provider has higher score
            if score > best_score:
                best_match = provider
                best_score = score
        
        # Only return if we have high confidence (explicit provider field match)
        if best_score >= 100:
            safe_log(
                self.tracer_instance,
                "debug",
                "Dynamic value-based detection: %s (score: %d)",
                best_match,
                best_score,
            )
            return best_match
        
        return "unknown"

    def _normalize_attribute_keys(self, attribute_keys) -> Set[str]:
        """
        Dynamically normalize attribute keys by detecting and reconstructing structural patterns.
        
        This implements FULL DYNAMIC LOGIC - not static pattern matching.
        
        Dynamic Analysis:
        - Detects array patterns (e.g., "llm.input_messages.0.message.role")
        - Detects object patterns (e.g., "config.model_config.temperature")
        - Reconstructs wildcard patterns (e.g., "llm.input_messages.*")
        
        Algorithm:
        1. Group keys by their base prefix (before array indices)
        2. Detect numeric indices indicating arrays
        3. Replace array index patterns with wildcard notation
        
        Examples:
        - "llm.input_messages.0.message.role" → "llm.input_messages.*"
        - "llm.input_messages.1.message.content" → "llm.input_messages.*"
        - "llm.model" → "llm.model" (unchanged)
        
        Performance: O(n × m) where n = number of keys, m = average key depth
        
        Args:
            attribute_keys: Iterable of attribute key strings
            
        Returns:
            Set of normalized keys with wildcard patterns
        """
        normalized = set()
        pattern_groups = {}  # Track patterns that have been normalized
        
        for key in attribute_keys:
            # Split key into parts
            parts = key.split('.')
            
            # Analyze each part for numeric indices
            normalized_parts = []
            is_pattern = False
            
            for i, part in enumerate(parts):
                # Check if this part is a numeric index (array element)
                if part.isdigit():
                    # This is an array index - mark for wildcard replacement
                    is_pattern = True
                    # Don't include the index in normalized key
                    # Instead, mark the previous part for wildcard
                    break
                else:
                    normalized_parts.append(part)
            
            if is_pattern:
                # Reconstruct as wildcard pattern
                base_pattern = '.'.join(normalized_parts)
                wildcard_pattern = base_pattern + '.*' if base_pattern else '*'
                
                # Track this pattern to avoid duplicates
                if wildcard_pattern not in pattern_groups:
                    pattern_groups[wildcard_pattern] = []
                pattern_groups[wildcard_pattern].append(key)
                
                normalized.add(wildcard_pattern)
            else:
                # No pattern detected, keep original key
                normalized.add(key)
        
        safe_log(
            self.tracer_instance,
            "debug",
            "Normalized %d keys to %d patterns (detected %d array patterns)",
            len(list(attribute_keys)),
            len(normalized),
            len(pattern_groups),
        )
        
        return normalized

    def _match_wildcard_signatures(self, normalized_keys: Set[str], attributes: Dict[str, Any]) -> str:
        """
        Match signatures using normalized keys (dynamic pattern matching).

        With dynamic normalization, wildcard patterns are matched directly:
        - Signature: "llm.input_messages.*"
        - Normalized incoming: "llm.input_messages.*" (from flattened keys)
        - Result: Exact match

        Performance: O(signatures × fields) for partial matches

        Args:
            normalized_keys: Dynamically normalized attribute keys
            attributes: Original span attributes (for logging)

        Returns:
            Pattern name or 'unknown'
        """
        best_match: Optional[str] = None
        best_confidence: float = 0.0

        # Iterate through all provider signatures
        for signature_fields, (pattern_name, confidence) in self.signature_to_provider.items():
            # Check if this signature has any wildcard patterns
            has_wildcards = any(field.endswith(".*") for field in signature_fields)
            if not has_wildcards:
                continue  # Skip non-wildcard signatures (handled by exact match)

            # Calculate overlap between signature and normalized keys
            signature_set = set(signature_fields)
            matched_count = len(signature_set & normalized_keys)

            # Calculate match confidence
            match_ratio = matched_count / len(signature_fields) if signature_fields else 0.0
            if match_ratio >= 0.8:  # At least 80% match (allows for minor variations)
                adjusted_confidence = confidence * match_ratio
                
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "✅ Wildcard signature match: %s (confidence: %.2f, matched: %d/%d, ratio: %.2f)",
                    pattern_name,
                    adjusted_confidence,
                    matched_count,
                    len(signature_fields),
                    match_ratio,
                )

                if adjusted_confidence > best_confidence:
                    best_match = pattern_name
                    best_confidence = adjusted_confidence

        return best_match if best_match else "unknown"

    def _find_best_subset_match(self, attribute_keys: FrozenSet[str], attributes: Optional[Dict[str, Any]] = None) -> str:
        """
        O(log n) subset match fallback using size-based bucketing with specificity ranking.

        Performance: O(log n) where n = number of providers, due to early termination

        Algorithm:
        1. Group signatures by size (largest to smallest = most specific first)
        2. Only check signatures <= attribute set size
        3. Within same size, collect all matches and rank by specificity
        4. Use value-based detection as tiebreaker for same-size matches

        Args:
            attribute_keys: Frozenset of attribute keys to match against
            attributes: Full attribute dict for value-based tiebreaking (optional)

        Returns:
            Pattern name or 'unknown'
        """
        best_match: Optional[str] = None
        best_confidence: float = 0.0
        best_size: int = 0

        # Get unique signature sizes, sorted largest to smallest (most specific first)
        signature_sizes = sorted(
            set(len(sig) for sig in self.signature_to_provider.keys()), reverse=True
        )

        safe_log(
            self.tracer_instance,
            "debug",
            "Subset matching: checking %d size buckets (most specific first)",
            len(signature_sizes),
        )

        # Iterate through size buckets (O(log n) due to early termination)
        for size in signature_sizes:
            # Skip signatures larger than attribute set (can't be subset)
            if size > len(attribute_keys):
                continue

            # Collect all matches for this size bucket
            size_bucket_matches = []

            # Check only signatures of this size
            for signature, (
                pattern_name,
                base_confidence,
            ) in self.signature_to_provider.items():
                if len(signature) != size:
                    continue

                # Check if signature is subset of attributes (O(1) for frozenset)
                if signature.issubset(attribute_keys):
                    # Calculate match confidence based on coverage
                    coverage = len(signature) / len(attribute_keys)
                    confidence = coverage * base_confidence

                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "  Subset match candidate: %s (size: %d, confidence: %.2f, coverage: %.2f)",
                        pattern_name,
                        size,
                        confidence,
                        coverage,
                    )

                    size_bucket_matches.append((pattern_name, confidence, size))

            # Process matches for this size bucket
            if size_bucket_matches:
                # If we have attributes, use value-based detection as tiebreaker
                if attributes and len(size_bucket_matches) > 1:
                    value_based_provider = self._detect_provider_by_values(attributes)
                    
                    if value_based_provider != "unknown":
                        # Filter matches that match the value-based provider
                        matching_patterns = [
                            (name, conf, sz) for name, conf, sz in size_bucket_matches
                            if value_based_provider in name
                        ]
                        
                        if matching_patterns:
                            safe_log(
                                self.tracer_instance,
                                "debug",
                                "  Using value-based tiebreaker: provider=%s",
                                value_based_provider,
                            )
                            size_bucket_matches = matching_patterns

                # Sort by: 1) size (desc), 2) confidence (desc)
                size_bucket_matches.sort(key=lambda x: (x[2], x[1]), reverse=True)
                
                # Take the best match from this bucket
                pattern_name, confidence, match_size = size_bucket_matches[0]
                
                # Update best match if this is better (larger signature = more specific)
                if match_size > best_size or (match_size == best_size and confidence > best_confidence):
                    best_match = pattern_name
                    best_confidence = confidence
                    best_size = match_size

                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "  New best match: %s (size: %d, confidence: %.2f)",
                        best_match,
                        best_size,
                        best_confidence,
                    )

                # Early termination: found a match in the largest possible bucket
                if best_size == size and best_confidence > 0.8:
                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "  High confidence match in largest bucket, early termination",
                    )
                    break

        if best_match:
            safe_log(
                self.tracer_instance,
                "debug",
                "✅ Best subset match: %s (confidence: %.2f)",
                best_match,
                best_confidence,
            )
            return best_match
        else:
            safe_log(
                self.tracer_instance,
                "debug",
                "No subset match found, returning unknown",
            )
            return "unknown"

    def _extract_provider_data(
        self, provider: str, attributes: Dict[str, Any], instrumentor: str = "unknown"
    ) -> Dict[str, Any]:
        """
        O(1) data extraction using compiled extraction functions with two-tier routing.

        Performance: O(1) - dict lookup + compiled function execution

        Args:
            provider: Detected provider name (e.g., "openai", "anthropic")
            attributes: Span attributes to extract from
            instrumentor: Detected instrumentor (e.g., "traceloop", "openinference")

        Returns:
            HoneyHive schema structure
        """

        if provider not in self.extraction_functions:
            safe_log(
                self.tracer_instance,
                "debug",
                "No extraction function found for provider: %s",
                provider,
            )
            return self._fallback_processing(attributes)

        try:
            extraction_function = self.extraction_functions[provider]
            # Pass instrumentor for two-tier routing
            result = extraction_function(attributes, instrumentor)

            # Ensure result has proper structure
            if not isinstance(result, dict):
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Extraction function for %s returned non-dict: %s",
                    provider,
                    type(result),
                )
                return self._fallback_processing(attributes)

            return result

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                "Extraction function failed for provider %s: %s",
                provider,
                e,
            )
            return self._fallback_processing(attributes)

    def _validate_and_enhance(
        self, data: Dict[str, Any], provider: str
    ) -> Dict[str, Any]:
        """Validate and enhance extracted data."""

        # Ensure all required sections exist
        for section in ["inputs", "outputs", "config", "metadata"]:
            if section not in data:
                data[section] = {}
            elif not isinstance(data[section], dict):
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "Section %s is not a dict, converting",
                    section,
                )
                data[section] = {}

        # Ensure provider is set in metadata
        if "provider" not in data["metadata"]:
            data["metadata"]["provider"] = provider

        # Add processing metadata
        data["metadata"]["processing_engine"] = "universal_llm_discovery_v4"
        # Only set detection_method if not already set (preserve fallback_heuristic from _fallback_processing)
        if "detection_method" not in data["metadata"]:
            data["metadata"]["detection_method"] = "signature_based"
        data["metadata"]["processed_at"] = time.time()

        # Validate against schema rules if available
        if self.validation_rules:
            self._apply_validation_rules(data, provider)

        return data

    def _apply_validation_rules(self, data: Dict[str, Any], provider: str):
        """Apply validation rules to extracted data."""

        try:
            # Get validation rules for HoneyHive schema
            schema_validation = self.validation_rules.get("schema_validation", {})

            for section_name, section_data in data.items():
                if section_name in schema_validation:
                    section_rules = schema_validation[section_name]

                    # Check max fields
                    max_fields = section_rules.get("max_fields", 100)
                    if len(section_data) > max_fields:
                        safe_log(
                            self.tracer_instance,
                            "warning",
                            "Section %s has %d fields, max is %d",
                            section_name,
                            len(section_data),
                            max_fields,
                        )

                    # Check required fields
                    if section_name == "metadata" and section_rules.get(
                        "require_provider"
                    ):
                        if "provider" not in section_data:
                            safe_log(
                                self.tracer_instance,
                                "debug",
                                "Missing required provider field in metadata",
                            )

                    if section_name == "config" and section_rules.get(
                        "require_model_recommended"
                    ):
                        if "model" not in section_data:
                            safe_log(
                                self.tracer_instance,
                                "debug",
                                "Recommended model field missing in config",
                            )

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "debug",
                "Validation rule application failed: %s",
                e,
            )

    def _build_inverted_index_fallback(self) -> Dict[FrozenSet[str], Tuple[str, float]]:
        """
        Build inverted index at runtime for legacy bundles.

        This ensures backward compatibility with bundles compiled before v4.0.1
        that don't include the pre-compiled inverted index.

        Returns:
            Dict mapping signature frozensets to (provider_name, confidence) tuples
        """
        inverted_index: Dict[FrozenSet[str], Tuple[str, float]] = {}

        for provider_name, signatures in self.provider_signatures.items():
            for signature in signatures:
                # Use default confidence of 0.9 for legacy bundles
                confidence = 0.9

                if signature in inverted_index:
                    existing_provider, existing_conf = inverted_index[signature]
                    if confidence > existing_conf:
                        inverted_index[signature] = (provider_name, confidence)
                else:
                    inverted_index[signature] = (provider_name, confidence)

        safe_log(
            self.tracer_instance,
            "debug",
            "Built inverted index at runtime: %d signatures",
            len(inverted_index),
        )

        return inverted_index

    def _fallback_processing(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback processing for unknown providers with graceful degradation."""

        safe_log(
            self.tracer_instance,
            "debug",
            "Using fallback processing for unknown provider",
        )

        # Basic extraction using common patterns
        inputs = {}
        outputs = {}
        config = {}
        metadata = {"provider": "unknown"}

        try:
            # Extract common fields with heuristics - graceful handling
            for key, value in attributes.items():
                try:
                    key_lower = (
                        key.lower() if isinstance(key, str) else str(key).lower()
                    )

                    # Input patterns
                    if any(
                        pattern in key_lower
                        for pattern in [
                            "input",
                            "prompt",
                            "message",
                            "query",
                            "request",
                        ]
                    ):
                        inputs[key] = value

                    # Output patterns
                    elif any(
                        pattern in key_lower
                        for pattern in [
                            "output",
                            "completion",
                            "response",
                            "result",
                            "answer",
                        ]
                    ):
                        outputs[key] = value

                    # Config patterns
                    elif any(
                        pattern in key_lower
                        for pattern in [
                            "model",
                            "temperature",
                            "max_token",
                            "top_p",
                            "parameter",
                        ]
                    ):
                        config[key] = value

                    # Metadata patterns (everything else)
                    else:
                        metadata[key] = value

                except Exception as e:
                    safe_log(
                        self.tracer_instance,
                        "debug",
                        "Failed to process attribute %s: %s",
                        key,
                        e,
                    )
                    # Continue processing other attributes

        except Exception as e:
            safe_log(
                self.tracer_instance, "debug", "Failed to iterate attributes: %s", e
            )

        # Add fallback metadata
        try:
            metadata.update(
                {
                    "processing_engine": "universal_llm_discovery_v4",
                    "detection_method": "fallback_heuristic",
                    "processed_at": time.time(),
                }
            )
        except Exception as e:
            safe_log(
                self.tracer_instance, "debug", "Failed to add fallback metadata: %s", e
            )

        return {
            "inputs": inputs,
            "outputs": outputs,
            "config": config,
            "metadata": metadata,
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""

        stats = self.performance_stats.copy()

        # Calculate processing time statistics
        if stats["processing_times"]:
            times = stats["processing_times"]
            stats["avg_processing_time_ms"] = sum(times) / len(times)
            stats["min_processing_time_ms"] = min(times)
            stats["max_processing_time_ms"] = max(times)
        else:
            stats["avg_processing_time_ms"] = 0
            stats["min_processing_time_ms"] = 0
            stats["max_processing_time_ms"] = 0

        # Calculate provider detection rates
        total_detections = sum(stats["provider_detections"].values())
        if total_detections > 0:
            stats["provider_detection_rates"] = {
                provider: count / total_detections
                for provider, count in stats["provider_detections"].items()
            }
        else:
            stats["provider_detection_rates"] = {}

        # Calculate fallback rate
        if stats["total_processed"] > 0:
            stats["fallback_rate"] = stats["fallback_usage"] / stats["total_processed"]
        else:
            stats["fallback_rate"] = 0

        return stats

    def reset_performance_stats(self):
        """Reset performance statistics."""

        self.performance_stats = {
            "total_processed": 0,
            "provider_detections": {},
            "fallback_usage": 0,
            "processing_times": [],
            "errors": 0,
        }

    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers."""

        return list(self.provider_signatures.keys())

    def get_provider_signatures(self, provider: str) -> Optional[List[FrozenSet[str]]]:
        """Get signature patterns for a specific provider."""

        return self.provider_signatures.get(provider)

    def validate_attributes_for_provider(
        self, attributes: Dict[str, Any], provider: str
    ) -> bool:
        """Check if attributes match a specific provider's signatures."""

        if provider not in self.provider_signatures:
            return False

        attribute_keys = frozenset(attributes.keys())

        for signature in self.provider_signatures[provider]:
            if signature.issubset(attribute_keys):
                return True

        return False

    def get_bundle_metadata(self) -> Dict[str, Any]:
        """Get bundle build metadata with graceful degradation."""

        try:
            if self.bundle_loader:
                return self.bundle_loader.get_build_metadata()
            else:
                safe_log(
                    self.tracer_instance,
                    "debug",
                    "No bundle loader available for metadata",
                )
                return {}
        except Exception as e:
            safe_log(
                self.tracer_instance, "debug", "Failed to get bundle metadata: %s", e
            )
            return {}

    def reload_bundle(self):
        """Reload the provider bundle (useful for development)."""

        safe_log(self.tracer_instance, "info", "Reloading provider bundle...")

        try:
            # Clear cached bundle in loader if available
            if self.bundle_loader:
                self.bundle_loader._cached_bundle = None
                self.bundle_loader._cached_functions = {}

            # Reload bundle
            self._load_bundle()

            safe_log(
                self.tracer_instance, "info", "Provider bundle reloaded successfully"
            )

        except Exception as e:
            safe_log(
                self.tracer_instance,
                "warning",
                "Failed to reload provider bundle: %s",
                e,
            )
