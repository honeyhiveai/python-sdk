#!/usr/bin/env python3
"""
Provider Bundle Validation System for Universal LLM Discovery Engine v4.0

Validates compiled provider bundles for correctness and performance:
1. Bundle structure validation
2. Provider signature validation  
3. Extraction function validation
4. Performance characteristic validation
5. Cross-provider consistency validation
"""

import pickle
import json
import logging
import argparse
import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Set, FrozenSet, Optional
from dataclasses import asdict

# Import the CompiledProviderBundle class
try:
    from compile_providers import CompiledProviderBundle
except ImportError:
    # If running as script, try to import from same directory
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from compile_providers import CompiledProviderBundle

logger = logging.getLogger(__name__)

class BundleValidator:
    """Validate compiled provider bundles for correctness and performance."""
    
    def __init__(self, bundle_path: Path):
        """Initialize bundle validator."""
        self.bundle_path = bundle_path
        self.bundle_metadata_path = bundle_path.parent / "bundle_metadata.json"
        self.bundle = None
        self.metadata = None
        
        # Validation results
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_info = []
        
        # Performance metrics
        self.performance_metrics = {}
        
    def validate_bundle(self) -> bool:
        """Main validation entry point."""
        
        logger.info("Starting comprehensive bundle validation...")
        start_time = time.time()
        
        try:
            # Load bundle and metadata
            self._load_bundle()
            self._load_metadata()
            
            # Run validation checks
            self._validate_bundle_structure()
            self._validate_provider_signatures()
            self._validate_extraction_functions()
            self._validate_field_mappings()
            self._validate_transform_registry()
            self._validate_performance_characteristics()
            self._validate_cross_provider_consistency()
            
            # Calculate validation time
            validation_time = time.time() - start_time
            self.performance_metrics['validation_time'] = validation_time
            
            # Report results
            self._report_validation_results()
            
            # Return success if no errors
            return len(self.validation_errors) == 0
            
        except Exception as e:
            logger.error(f"Bundle validation failed with exception: {e}")
            self.validation_errors.append(f"Validation exception: {e}")
            return False
    
    def _load_bundle(self):
        """Load the compiled bundle."""
        
        if not self.bundle_path.exists():
            raise FileNotFoundError(f"Bundle file not found: {self.bundle_path}")
        
        try:
            with open(self.bundle_path, 'rb') as f:
                self.bundle = pickle.load(f)
            
            logger.debug(f"Loaded bundle from: {self.bundle_path}")
            
        except Exception as e:
            raise ValueError(f"Failed to load bundle: {e}")
    
    def _load_metadata(self):
        """Load bundle metadata if available."""
        
        if self.bundle_metadata_path.exists():
            try:
                with open(self.bundle_metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                
                logger.debug(f"Loaded metadata from: {self.bundle_metadata_path}")
                
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                self.metadata = {}
        else:
            logger.warning("No metadata file found")
            self.metadata = {}
    
    def _validate_bundle_structure(self):
        """Validate the basic bundle structure."""
        
        logger.info("Validating bundle structure...")
        
        # Check required attributes
        required_attrs = [
            'provider_signatures',
            'extraction_functions', 
            'field_mappings',
            'transform_registry',
            'validation_rules',
            'build_metadata'
        ]
        
        for attr in required_attrs:
            if not hasattr(self.bundle, attr):
                self.validation_errors.append(f"Bundle missing required attribute: {attr}")
            elif getattr(self.bundle, attr) is None:
                self.validation_errors.append(f"Bundle attribute is None: {attr}")
        
        # Check bundle is not empty
        if hasattr(self.bundle, 'provider_signatures'):
            if not self.bundle.provider_signatures:
                self.validation_errors.append("Bundle contains no provider signatures")
            else:
                self.validation_info.append(f"Bundle contains {len(self.bundle.provider_signatures)} providers")
        
        # Check build metadata
        if hasattr(self.bundle, 'build_metadata'):
            metadata = self.bundle.build_metadata
            
            if not isinstance(metadata, dict):
                self.validation_errors.append("Build metadata must be a dictionary")
            else:
                required_metadata = ['version', 'build_timestamp', 'providers_count']
                for key in required_metadata:
                    if key not in metadata:
                        self.validation_warnings.append(f"Missing build metadata: {key}")
    
    def _validate_provider_signatures(self):
        """Validate provider signature patterns."""
        
        logger.info("Validating provider signatures...")
        
        if not hasattr(self.bundle, 'provider_signatures'):
            return
        
        signatures = self.bundle.provider_signatures
        all_signatures = set()
        
        for provider_name, provider_signatures in signatures.items():
            # Validate provider has signatures
            if not provider_signatures:
                self.validation_errors.append(f"Provider {provider_name} has no signatures")
                continue
            
            if not isinstance(provider_signatures, list):
                self.validation_errors.append(f"Provider {provider_name} signatures must be a list")
                continue
            
            # Validate each signature
            for i, signature in enumerate(provider_signatures):
                if not isinstance(signature, frozenset):
                    self.validation_errors.append(f"Provider {provider_name} signature {i} must be a frozenset")
                    continue
                
                # Check signature size
                if len(signature) < 2:
                    self.validation_warnings.append(
                        f"Provider {provider_name} signature {i} has < 2 fields: {signature} (may cause false positives)"
                    )
                
                if len(signature) > 10:
                    self.validation_warnings.append(
                        f"Provider {provider_name} signature {i} has > 10 fields: {len(signature)} (may be overly specific)"
                    )
                
                # Check for signature uniqueness across all providers
                signature_str = frozenset_to_string(signature)
                if signature_str in all_signatures:
                    self.validation_errors.append(
                        f"Duplicate signature found: {signature_str} (provider {provider_name})"
                    )
                else:
                    all_signatures.add(signature_str)
                
                # Check field name patterns
                for field in signature:
                    if not isinstance(field, str):
                        self.validation_errors.append(f"Signature field must be string: {field}")
                    elif len(field) == 0:
                        self.validation_errors.append("Signature field cannot be empty")
                    elif len(field) > 64:
                        self.validation_warnings.append(f"Long signature field: {field}")
        
        # Calculate signature statistics
        total_signatures = sum(len(sigs) for sigs in signatures.values())
        self.performance_metrics['total_signatures'] = total_signatures
        self.validation_info.append(f"Total signatures across all providers: {total_signatures}")
    
    def _validate_extraction_functions(self):
        """Validate extraction function code."""
        
        logger.info("Validating extraction functions...")
        
        if not hasattr(self.bundle, 'extraction_functions'):
            return
        
        functions = self.bundle.extraction_functions
        
        for provider_name, function_code in functions.items():
            # Validate function code is string
            if not isinstance(function_code, str):
                self.validation_errors.append(f"Extraction function for {provider_name} must be string")
                continue
            
            if len(function_code) == 0:
                self.validation_errors.append(f"Extraction function for {provider_name} is empty")
                continue
            
            # Validate function syntax
            try:
                compile(function_code, f"<{provider_name}_extraction>", "exec")
                self.validation_info.append(f"Extraction function syntax valid for {provider_name}")
                
            except SyntaxError as e:
                self.validation_errors.append(
                    f"Invalid extraction function syntax for {provider_name}: {e}"
                )
            
            # Check function size
            function_size = len(function_code)
            self.performance_metrics[f'{provider_name}_function_size'] = function_size
            
            if function_size > 10000:  # 10KB
                self.validation_warnings.append(
                    f"Large extraction function for {provider_name}: {function_size} bytes"
                )
            
            # Validate function name pattern
            expected_function_name = f"extract_{provider_name}_data"
            if expected_function_name not in function_code:
                self.validation_warnings.append(
                    f"Expected function name {expected_function_name} not found in {provider_name} function"
                )
    
    def _validate_field_mappings(self):
        """Validate field mappings for HoneyHive schema compliance."""
        
        logger.info("Validating field mappings...")
        
        if not hasattr(self.bundle, 'field_mappings'):
            return
        
        mappings = self.bundle.field_mappings
        required_sections = ['inputs', 'outputs', 'config', 'metadata']
        
        for provider_name, provider_mappings in mappings.items():
            if not isinstance(provider_mappings, dict):
                self.validation_errors.append(f"Field mappings for {provider_name} must be dict")
                continue
            
            # Check required sections
            for section in required_sections:
                if section not in provider_mappings:
                    self.validation_errors.append(
                        f"Provider {provider_name} missing required section: {section}"
                    )
                else:
                    section_data = provider_mappings[section]
                    if not isinstance(section_data, dict):
                        self.validation_errors.append(
                            f"Provider {provider_name} section {section} must be dict"
                        )
            
            # Validate metadata section has provider field
            metadata_section = provider_mappings.get('metadata', {})
            if 'provider' not in metadata_section:
                self.validation_errors.append(
                    f"Provider {provider_name} metadata section must include 'provider' field"
                )
            
            # Check field mapping structure
            for section_name, section_data in provider_mappings.items():
                if isinstance(section_data, dict):
                    for field_name, field_config in section_data.items():
                        if isinstance(field_config, dict):
                            if 'source_rule' not in field_config:
                                self.validation_warnings.append(
                                    f"Provider {provider_name}.{section_name}.{field_name} missing source_rule"
                                )
    
    def _validate_transform_registry(self):
        """Validate transform registry."""
        
        logger.info("Validating transform registry...")
        
        if not hasattr(self.bundle, 'transform_registry'):
            return
        
        registry = self.bundle.transform_registry
        
        for provider_name, transforms in registry.items():
            if not isinstance(transforms, dict):
                self.validation_errors.append(f"Transform registry for {provider_name} must be dict")
                continue
            
            for transform_name, transform_config in transforms.items():
                if not isinstance(transform_config, dict):
                    self.validation_warnings.append(
                        f"Transform {provider_name}.{transform_name} config must be dict"
                    )
                    continue
                
                # Check required transform fields
                required_fields = ['function_type', 'implementation', 'description']
                for field in required_fields:
                    if field not in transform_config:
                        self.validation_warnings.append(
                            f"Transform {provider_name}.{transform_name} missing {field}"
                        )
    
    def _validate_performance_characteristics(self):
        """Validate performance characteristics meet requirements."""
        
        logger.info("Validating performance characteristics...")
        
        # Test bundle loading time
        start_time = time.time()
        
        # Simulate bundle loading
        try:
            with open(self.bundle_path, 'rb') as f:
                test_bundle = pickle.load(f)
            
            load_time = (time.time() - start_time) * 1000  # Convert to ms
            self.performance_metrics['bundle_load_time_ms'] = load_time
            
            # Check against requirements
            if load_time > 3.0:  # 3ms requirement
                self.validation_warnings.append(
                    f"Bundle load time {load_time:.2f}ms exceeds 3ms requirement"
                )
            else:
                self.validation_info.append(f"Bundle load time: {load_time:.2f}ms (✓)")
                
        except Exception as e:
            self.validation_errors.append(f"Failed to test bundle loading: {e}")
        
        # Test bundle size
        bundle_size = self.bundle_path.stat().st_size
        self.performance_metrics['bundle_size_bytes'] = bundle_size
        
        if bundle_size > 1048576:  # 1MB
            self.validation_warnings.append(
                f"Bundle size {bundle_size} bytes exceeds 1MB recommendation"
            )
        else:
            self.validation_info.append(f"Bundle size: {bundle_size} bytes (✓)")
        
        # Test signature detection performance
        if hasattr(self.bundle, 'provider_signatures'):
            self._test_signature_detection_performance()
    
    def _test_signature_detection_performance(self):
        """Test provider signature detection performance."""
        
        signatures = self.bundle.provider_signatures
        
        # Create test attributes
        test_attributes = {
            'llm.input_messages': [],
            'llm.output_messages': [],
            'llm.model_name': 'test-model',
            'llm.token_count_prompt': 10,
            'llm.token_count_completion': 20
        }
        
        attribute_keys = frozenset(test_attributes.keys())
        
        # Time signature detection
        start_time = time.perf_counter()
        
        # Run detection multiple times for accurate measurement
        iterations = 1000
        for _ in range(iterations):
            for provider_name, provider_signatures in signatures.items():
                for signature in provider_signatures:
                    match = signature.issubset(attribute_keys)
        
        end_time = time.perf_counter()
        
        # Calculate per-detection time
        total_detections = iterations * sum(len(sigs) for sigs in signatures.values())
        avg_detection_time = ((end_time - start_time) / total_detections) * 1000  # Convert to ms
        
        self.performance_metrics['avg_detection_time_ms'] = avg_detection_time
        
        # Check against requirements
        if avg_detection_time > 0.01:  # 0.01ms requirement
            self.validation_warnings.append(
                f"Average detection time {avg_detection_time:.4f}ms exceeds 0.01ms requirement"
            )
        else:
            self.validation_info.append(f"Average detection time: {avg_detection_time:.4f}ms (✓)")
    
    def _validate_cross_provider_consistency(self):
        """Validate consistency across providers."""
        
        logger.info("Validating cross-provider consistency...")
        
        if not hasattr(self.bundle, 'provider_signatures') or not hasattr(self.bundle, 'field_mappings'):
            return
        
        # Check that all providers with signatures have field mappings
        signature_providers = set(self.bundle.provider_signatures.keys())
        mapping_providers = set(self.bundle.field_mappings.keys())
        
        missing_mappings = signature_providers - mapping_providers
        if missing_mappings:
            self.validation_errors.append(
                f"Providers with signatures but no field mappings: {missing_mappings}"
            )
        
        missing_signatures = mapping_providers - signature_providers
        if missing_signatures:
            self.validation_errors.append(
                f"Providers with field mappings but no signatures: {missing_signatures}"
            )
        
        # Check extraction functions consistency
        if hasattr(self.bundle, 'extraction_functions'):
            function_providers = set(self.bundle.extraction_functions.keys())
            
            missing_functions = signature_providers - function_providers
            if missing_functions:
                self.validation_errors.append(
                    f"Providers with signatures but no extraction functions: {missing_functions}"
                )
    
    def _report_validation_results(self):
        """Report validation results."""
        
        logger.info("=" * 60)
        logger.info("BUNDLE VALIDATION RESULTS")
        logger.info("=" * 60)
        
        # Summary
        total_issues = len(self.validation_errors) + len(self.validation_warnings)
        logger.info(f"Total Issues: {total_issues}")
        logger.info(f"  Errors: {len(self.validation_errors)}")
        logger.info(f"  Warnings: {len(self.validation_warnings)}")
        logger.info(f"  Info: {len(self.validation_info)}")
        
        # Performance metrics
        if self.performance_metrics:
            logger.info("\nPerformance Metrics:")
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    logger.info(f"  {metric}: {value:.4f}")
                else:
                    logger.info(f"  {metric}: {value}")
        
        # Errors
        if self.validation_errors:
            logger.error("\nERRORS:")
            for i, error in enumerate(self.validation_errors, 1):
                logger.error(f"  {i}. {error}")
        
        # Warnings
        if self.validation_warnings:
            logger.warning("\nWARNINGS:")
            for i, warning in enumerate(self.validation_warnings, 1):
                logger.warning(f"  {i}. {warning}")
        
        # Info
        if self.validation_info:
            logger.info("\nINFORMATION:")
            for i, info in enumerate(self.validation_info, 1):
                logger.info(f"  {i}. {info}")
        
        # Final result
        if len(self.validation_errors) == 0:
            logger.info("\n✅ BUNDLE VALIDATION PASSED")
        else:
            logger.error("\n❌ BUNDLE VALIDATION FAILED")
        
        logger.info("=" * 60)
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get structured validation report."""
        
        return {
            'success': len(self.validation_errors) == 0,
            'summary': {
                'total_issues': len(self.validation_errors) + len(self.validation_warnings),
                'errors': len(self.validation_errors),
                'warnings': len(self.validation_warnings),
                'info_items': len(self.validation_info)
            },
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'info': self.validation_info,
            'performance_metrics': self.performance_metrics,
            'bundle_path': str(self.bundle_path),
            'validation_timestamp': time.time()
        }

def frozenset_to_string(fs: FrozenSet[str]) -> str:
    """Convert frozenset to string for comparison."""
    return '|'.join(sorted(fs))

def main():
    """Main entry point for bundle validation."""
    
    parser = argparse.ArgumentParser(
        description="Validate compiled provider bundle for Universal LLM Discovery Engine v4.0"
    )
    parser.add_argument(
        "bundle_path",
        nargs="?",
        type=Path,
        help="Path to compiled bundle file (default: auto-detect)"
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for validation results"
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Output file for validation results"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Determine bundle path
    if args.bundle_path:
        bundle_path = args.bundle_path
    else:
        # Auto-detect bundle path
        default_path = Path(__file__).parent.parent / "src" / "honeyhive" / "tracer" / "processing" / "semantic_conventions" / "compiled_providers.pkl"
        if default_path.exists():
            bundle_path = default_path
        else:
            logger.error("No bundle path provided and default bundle not found")
            return 1
    
    if not bundle_path.exists():
        logger.error(f"Bundle file not found: {bundle_path}")
        return 1
    
    try:
        # Run validation
        validator = BundleValidator(bundle_path)
        success = validator.validate_bundle()
        
        # Output results
        if args.output_format == "json":
            report = validator.get_validation_report()
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"Validation report written to: {args.output_file}")
            else:
                print(json.dumps(report, indent=2))
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Validation failed with exception: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
