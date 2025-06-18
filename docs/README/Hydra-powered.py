#!/usr/bin/env python3
"""
Arabic NER with Hydra Configuration - Usage Examples
This file demonstrates various ways to use the Hydra-powered Arabic NER configuration
"""

import hydra
from hydra import compose, initialize_config_store
from omegaconf import DictConfig, OmegaConf
from arabic_ner_config import HydraArabicNERConfig, ArabicNERConfig
import argparse
import sys
from pathlib import Path

# ==================== EXAMPLE 1: Simple Configuration Loading ====================

def example_basic_usage():
    """Basic usage example"""
    print("=== Example 1: Basic Configuration Loading ===")
    
    # Initialize the config manager
    config_manager = HydraArabicNERConfig()
    
    # Load default configuration
    cfg = config_manager.load_config()
    
    # Access configuration values
    print(f"Model name: {cfg.model_name}")
    print(f"Batch size: {cfg.batch_size}")
    print(f"Number of before honorifics: {len(cfg.honorifics.before_honorifics)}")
    print(f"Number of cities: {len(cfg.locations.cities)}")
    
    # Get all honorifics
    all_honorifics = config_manager.get_honorifics()
    print(f"Total honorifics: {len(all_honorifics)}")
    
    return cfg

# ==================== EXAMPLE 2: Configuration Overrides ====================

def example_config_overrides():
    """Example using configuration overrides"""
    print("\n=== Example 2: Configuration Overrides ===")
    
    config_manager = HydraArabicNERConfig()
    
    # Override configuration parameters
    overrides = [
        "model_name=custom-arabic-bert",
        "batch_size=64", 
        "learning_rate=1e-4",
        "max_sequence_length=256",
        "case_sensitive=false"
    ]
    
    cfg = config_manager.load_config(overrides=overrides)
    
    print(f"Overridden model name: {cfg.model_name}")
    print(f"Overridden batch size: {cfg.batch_size}")
    print(f"Overridden learning rate: {cfg.learning_rate}")
    print(f"Case sensitive: {cfg.case_sensitive}")
    
    return cfg

# ==================== EXAMPLE 3: Different Configuration Compositions ====================

def example_config_composition():
    """Example using different configuration compositions"""
    print("\n=== Example 3: Configuration Composition ===")
    
    config_manager = HydraArabicNERConfig()
    
    # Use different config groups
    overrides = [
        "honorifics=minimal",  # Use minimal honorifics
        "titles=basic",        # Use basic titles (if available)
        "batch_size=16",
        "model_name=lightweight-arabic-ner"
    ]
    
    try:
        cfg = config_manager.load_config(overrides=overrides)
        print(f"Composed config - Model: {cfg.model_name}")
        print(f"Before honorifics count: {len(cfg.honorifics.before_honorifics)}")
        print(f"Sample before honorifics: {cfg.honorifics.before_honorifics[:3]}")
    except Exception as e:
        print(f"Error in composition (might need to create the config files): {e}")
    
    return cfg

# ==================== EXAMPLE 4: Hydra App with Command Line Interface ====================

@hydra.main(version_base=None, config_path="conf", config_name="config")
def arabic_ner_train(cfg: DictConfig) -> None:
    """
    Example training script using Hydra
    
    Usage:
        python usage_examples.py model_name=my-model batch_size=32
    """
    print("\n=== Example 4: Hydra Training App ===")
    print("Configuration:")
    print(OmegaConf.to_yaml(cfg))
    
    # Simulate training process
    print(f"\nStarting training with:")
    print(f"  Model: {cfg.model_name}")
    print(f"  Batch size: {cfg.batch_size}")
    print(f"  Learning rate: {cfg.learning_rate}")
    print(f"  Max sequence length: {cfg.max_sequence_length}")
    
    # Access Arabic-specific configurations
    print(f"\nArabic NER specifics:")
    print(f"  Before honorifics: {len(cfg.honorifics.before_honorifics)}")
    print(f"  Prophet titles: {len(cfg.titles.prophet_titles)}")
    print(f"  Cities: {len(cfg.locations.cities)}")
    
    # Example processing
    honorifics_list = (cfg.honorifics.before_honorifics + 
                      cfg.honorifics.after_honorifics)
    print(f"  Total honorifics for processing: {len(honorifics_list)}")
    
    print("\n✅ Training simulation completed!")

# ==================== EXAMPLE 5: Dynamic Configuration Modification ====================

def example_dynamic_modification():
    """Example of dynamically modifying configuration"""
    print("\n=== Example 5: Dynamic Configuration Modification ===")
    
    config_manager = HydraArabicNERConfig()
    cfg = config_manager.load_config()
    
    # Print original config
    print("Original batch size:", cfg.batch_size)
    print("Original cities count:", len(cfg.locations.cities))
    
    # Modify configuration dynamically
    with open(cfg):  # This makes cfg mutable
        cfg.batch_size = 128
        cfg.model_name = "dynamically-modified-model"
        
        # Add new cities
        cfg.locations.cities.append("الرياض")
        cfg.locations.cities.append("الدوحة")
        cfg.locations.cities.append("الكويت")
    
    print("Modified batch size:", cfg.batch_size)
    print("Modified model name:", cfg.model_name)
    print("Modified cities count:", len(cfg.locations.cities))
    print("New cities:", cfg.locations.cities[-3:])

# ==================== EXAMPLE 6: Configuration Validation and Error Handling ====================

def example_validation_and_errors():
    """Example showing configuration validation and error handling"""
    print("\n=== Example 6: Configuration Validation ===")
    
    config_manager = HydraArabicNERConfig()
    
    # Test with invalid overrides
    invalid_overrides = [
        "batch_size=invalid_number",  # This should cause an error
    ]
    
    try:
        cfg = config_manager.load_config(overrides=invalid_overrides)
    except Exception as e:
        print(f"Expected error with invalid override: {e}")
    
    # Test with valid overrides
    valid_overrides = [
        "batch_size=32",
        "learning_rate=0.001"
    ]
    
    try:
        cfg = config_manager.load_config(overrides=valid_overrides)
        print("✅ Valid configuration loaded successfully")
        print(f"Batch size: {cfg.batch_size}")
        print(f"Learning rate: {cfg.learning_rate}")
        
        # Validate configuration values
        assert cfg.batch_size > 0, "Batch size must be positive"
        assert cfg.learning_rate > 0, "Learning rate must be positive" 
        assert len(cfg.honorifics.before_honorifics) > 0, "Must have before honorifics"
        
        print("✅ Configuration validation passed")
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")

# ==================== EXAMPLE 7: Multi-Environment Configuration ====================

def example_multi_environment():
    """Example showing different configurations for different environments"""
    print("\n=== Example 7: Multi-Environment Configuration ===")
    
    environments = {
        "development": [
            "batch_size=8",
            "model_name=dev-arabic-ner",
            "max_sequence_length=128"
        ],
        "testing": [
            "batch_size=16", 
            "model_name=test-arabic-ner",
            "max_sequence_length=256"
        ],
        "production": [
            "batch_size=64",
            "model_name=prod-arabic-ner-v1.0",
            "max_sequence_length=512"
        ]
    }
    
    config_manager = HydraArabicNERConfig()
    
    for env_name, overrides in environments.items():
        print(f"\n--- {env_name.upper()} Environment ---")
        cfg = config_manager.load_config(overrides=overrides)
        
        print(f"Model: {cfg.model_name}")
        print(f"Batch size: {cfg.batch_size}")
        print(f"Max sequence length: {cfg.max_sequence_length}")
        
        # Environment-specific logic
        if env_name == "development":
            print("🔧 Development mode: Enhanced logging enabled")
        elif env_name == "production":
            print("🚀 Production mode: Optimized for performance")

# ==================== EXAMPLE 8: Configuration Export and Import ====================

def example_export_import():
    """Example showing how to export and import configurations"""
    print("\n=== Example 8: Configuration Export/Import ===")
    
    config_manager = HydraArabicNERConfig()
    
    # Load and modify configuration
    overrides = [
        "model_name=exported-model",
        "batch_size=48",
        "learning_rate=5e-5"
    ]
    
    cfg = config_manager.load_config(overrides=overrides)
    
    # Export configuration
    export_path = "exported_config.yaml"
    try:
        config_manager.save_config(export_path)
        print(f"✅ Configuration exported to {export_path}")
        
        # Read the exported file to show its contents
        with open(export_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Exported config preview:\n{content[:500]}...")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

# ==================== EXAMPLE 9: Configuration Merging ====================

def example_config_merging():
    """Example showing configuration merging from multiple sources"""
    print("\n=== Example 9: Configuration Merging ===")
    
    # Base configuration
    base_overrides = [
        "model_name=base-model",
        "batch_size=32"
    ]
    
    # Experiment-specific overrides
    experiment_overrides = [
        "learning_rate=1e-4",
        "max_sequence_length=384"
    ]
    
    # User-specific overrides
    user_overrides = [
        "batch_size=16",  # This will override the base batch_size
        "case_sensitive=false"
    ]
    
    # Merge all overrides (later ones take precedence)
    all_overrides = base_overrides + experiment_overrides + user_overrides
    
    config_manager = HydraArabicNERConfig()
    cfg = config_manager.load_config(overrides=all_overrides)
    
    print("Merged configuration:")
    print(f"  Model name: {cfg.model_name}")  # from base
    print(f"  Batch size: {cfg.batch_size}")  # from user (overridden)
    print(f"  Learning rate: {cfg.learning_rate}")  # from experiment
    print(f"  Max sequence length: {cfg.max_sequence_length}")  # from experiment
    print(f"  Case sensitive: {cfg.case_sensitive}")  # from user

# ==================== EXAMPLE 10: Advanced Pattern Matching ====================

def example_pattern_matching():
    """Example showing how to use the configuration for NER pattern matching"""
    print("\n=== Example 10: NER Pattern Matching ===")
    
    config_manager = HydraArabicNERConfig()
    cfg = config_manager.load_config()
    
    # Sample Arabic text
    sample_text = "قال الشيخ محمد رحمه الله في مدينة بغداد أن النبي صلى الله عليه وسلم"
    
    print(f"Sample text: {sample_text}")
    print("\nPattern matching results:")
    
    # Check for before honorifics
    found_before_honorifics = []
    for honorific in cfg.honorifics.before_honorifics:
        if honorific in sample_text:
            found_before_honorifics.append(honorific)
    
    print(f"Before honorifics found: {found_before_honorifics}")
    
    # Check for after honorifics
    found_after_honorifics = []
    for honorific in cfg.honorifics.after_honorifics:
        if honorific in sample_text:
            found_after_honorifics.append(honorific)
    
    print(f"After honorifics found: {found_after_honorifics}")
    
    # Check for cities
    found_cities = []
    for city in cfg.locations.cities:
        if city in sample_text:
            found_cities.append(city)
    
    print(f"Cities found: {found_cities}")
    
    # Check for prophet titles
    found_prophet_titles = []
    for title in cfg.titles.prophet_titles:
        if title in sample_text:
            found_prophet_titles.append(title)
    
    print(f"Prophet titles found: {found_prophet_titles}")

# ==================== MAIN EXECUTION ====================

def main():
    """Main function to run all examples"""
    print("🚀 Arabic NER Hydra Configuration Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_usage()
        example_config_overrides()
        example_config_composition()
        example_dynamic_modification()
        example_validation_and_errors()
        example_multi_environment()
        example_export_import()
        example_config_merging()
        example_pattern_matching()
        
        print("\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()

# ==================== COMMAND LINE INTERFACE ====================

def cli_interface():
    """Command line interface for the examples"""
    parser = argparse.ArgumentParser(description="Arabic NER Hydra Configuration Examples")
    parser.add_argument("--example", type=str, choices=[
        "basic", "overrides", "composition", "dynamic", "validation",
        "multi-env", "export", "merging", "patterns", "all"
    ], default="all", help="Which example to run")
    
    parser.add_argument("--config-path", type=str, default="conf",
                       help="Path to configuration directory")
    parser.add_argument("--config-name", type=str, default="config",
                       help="Name of the main configuration file")
    
    args = parser.parse_args()
    
    # Map example names to functions
    examples = {
        "basic": example_basic_usage,
        "overrides": example_config_overrides,
        "composition": example_config_composition,
        "dynamic": example_dynamic_modification,
        "validation": example_validation_and_errors,
        "multi-env": example_multi_environment,
        "export": example_export_import,
        "merging": example_config_merging,
        "patterns": example_pattern_matching,
        "all": main
    }
    
    if args.example in examples:
        examples[args.example]()
    else:
        print(f"Unknown example: {args.example}")
        parser.print_help()

# ==================== HYDRA MULTIRUN EXAMPLE ====================

@hydra.main(version_base=None, config_path="conf", config_name="config")
def multirun_experiment(cfg: DictConfig) -> float:
    """
    Example multirun experiment for hyperparameter tuning
    
    Usage:
        python usage_examples.py --multirun batch_size=16,32,64 learning_rate=1e-4,2e-4,3e-4
    """
    print(f"\n🧪 Running experiment with:")
    print(f"  Batch size: {cfg.batch_size}")
    print(f"  Learning rate: {cfg.learning_rate}")
    print(f"  Model: {cfg.model_name}")
    
    # Simulate training and return a metric
    import random
    import time
    
    time.sleep(1)  # Simulate training time
    
    # Simulate performance based on hyperparameters
    performance = random.uniform(0.7, 0.95)
    
    # Adjust performance based on hyperparameters (simplified)
    if cfg.batch_size == 32:
        performance += 0.02
    if cfg.learning_rate == 2e-4:
        performance += 0.01
    
    print(f"  📊 Performance: {performance:.4f}")
    
    return performance

# ==================== USAGE INSTRUCTIONS ====================

usage_instructions = """
🚀 Arabic NER with Hydra - Usage Instructions

1. Basic Usage:
   python usage_examples.py

2. Run specific example:
   python usage_examples.py --example basic
   python usage_examples.py --example overrides

3. Run with Hydra app:
   python usage_examples.py model_name=my-model batch_size=64

4. Run multirun experiment:
   python usage_examples.py --multirun batch_size=16,32,64 learning_rate=1e-4,2e-4

5. Configuration file structure:
   conf/
   ├── config.yaml              # Main config
   ├── honorifics/
   │   ├── default.yaml         # Default honorifics
   │   └── minimal.yaml         # Minimal honorifics
   ├── titles/
   │   └── default.yaml         # Default titles
   ├── locations/
   │   └── default.yaml         # Default locations
   └── names/
       └── default.yaml         # Default names

6. Override examples:
   - model_name=custom-model
   - batch_size=128
   - honorifics=minimal
   - learning_rate=1e-3
   - case_sensitive=false

7. Environment variables:
   export HYDRA_FULL_ERROR=1    # Show full error traces
"""

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help-usage":
        print(usage_instructions)
    elif len(sys.argv) > 1 and (sys.argv[1].startswith("--multirun") or any("=" in arg for arg in sys.argv[1:])):
        # This is a Hydra command, let Hydra handle it
        arabic_ner_train()
    else:
        # Run CLI interface
        cli_interface()