# Arabic NER with Hydra Configuration - Complete Setup Guide

## 🎯 Overview

This guide shows how to use Hydra for managing Arabic Named Entity Recognition (NER) configurations. Hydra provides powerful features like:

- **Configuration Composition**: Mix and match different config files
- **Command-line Overrides**: Change parameters without editing files
- **Multi-run Support**: Run experiments with different parameter combinations
- **Structured Configs**: Type-safe configurations with validation
- **Environment Management**: Different configs for dev/test/prod

## 📦 Installation

```bash
# Install required packages
pip install hydra-core omegaconf

# Optional: For advanced features
pip install hydra-colorlog hydra-joblib-launcher
```

## 📁 Project Structure

```
arabic_ner_project/
├── arabic_ner_config.py      # Main configuration classes
├── usage_examples.py         # Usage examples and CLI
├── conf/                     # Hydra configuration directory
│   ├── config.yaml          # Main configuration file
│   ├── config_small.yaml    # Alternative configuration
│   ├── honorifics/          # Honorifics configurations
│   │   ├── default.yaml
│   │   └── minimal.yaml
│   ├── titles/              # Titles configurations
│   │   └── default.yaml
│   ├── locations/           # Locations configurations
│   │   └── default.yaml
│   └── names/               # Names configurations
│       └── default.yaml
├── outputs/                 # Hydra outputs (auto-created)
└── .hydra/                  # Hydra metadata (auto-created)
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from arabic_ner_config import HydraArabicNERConfig

# Initialize configuration manager
config_manager = HydraArabicNERConfig()

# Load default configuration
cfg = config_manager.load_config()

# Access configuration values
print(f"Model: {cfg.model_name}")
print(f"Batch size: {cfg.batch_size}")
print(f"Honorifics count: {len(cfg.honorifics.before_honorifics)}")
```

### 2. Command Line Usage

```bash
# Run with default configuration
python usage_examples.py

# Override specific parameters
python usage_examples.py model_name=custom-model batch_size=64

# Use different configuration composition
python usage_examples.py honorifics=minimal

# Run specific example
python usage_examples.py --example overrides
```

### 3. Multi-run Experiments

```bash
# Run hyperparameter sweep
python usage_examples.py --multirun batch_size=16,32,64 learning_rate=1e-4,2e-4,3e-4

# This will run 9 experiments (3×3 combinations)
```

## 🔧 Configuration Examples

### Main Configuration (conf/config.yaml)

```yaml
defaults:
  - honorifics: default
  - titles: default
  - locations: default
  - names: default
  - _self_

# Model parameters
model_name: "arabic-ner-model"
max_sequence_length: 512
batch_size: 32
learning_rate: 2e-5

# Processing parameters
case_sensitive: true
remove_diacritics: false
normalize_text: true
```

### Honorifics Configuration (conf/honorifics/default.yaml)

```yaml
before_honorifics:
  - "الشيخ"
  - "الإمام"
  - "الحافظ"
  # ... more honorifics

after_honorifics:
  - "صلى الله عليه وسلم"
  - "رضي الله عنه"
  - "رحمه الله"
  # ... more honorifics
```

## 🎛️ Advanced Features

### 1. Configuration Composition

Create different combinations of configurations:

```bash
# Use minimal honorifics with default everything else
python script.py honorifics=minimal

# Create a lightweight configuration
python script.py honorifics=minimal titles=basic batch_size=16
```

### 2. Environment-Specific Configurations

```python
# Development environment
overrides = [
    "batch_size=8",
    "model_name=dev-arabic-ner",
    "max_sequence_length=128"
]
cfg = config_manager.load_config(overrides=overrides)

# Production environment  
overrides = [
    "batch_size=64",
    "model_name=prod-arabic-ner-v1.0",
    "max_sequence_length=512"
]
cfg = config_manager.load_config(overrides=overrides)
```

### 3. Configuration Validation

```python
def validate_config(cfg):
    """Validate configuration parameters"""
    assert cfg.batch_size > 0, "Batch size must be positive"
    assert cfg.learning_rate > 0, "Learning rate must be positive"
    assert len(cfg.honorifics.before_honorifics) > 0, "Must have honorifics"
    
    # Custom validation logic
    if cfg.model_name.startswith("prod-"):
        assert cfg.batch_size >= 32, "Production models need larger batch size"
```

### 4. Dynamic Configuration Modification

```python
# Load configuration
cfg = config_manager.load_config()

# Modify at runtime
with open(cfg):  # Makes config mutable
    cfg.batch_size = 128
    cfg.locations.cities.append("الرياض")
    cfg.honorifics.scholar_honorifics.append("أكرمه الله")
```

## 📊 Integration with Training Scripts

### Hydra App Decorator

```python
@hydra.main(version_base=None, config_path="conf", config_name="config")
def train_arabic_ner(cfg: DictConfig) -> None:
    """Training script with Hydra configuration"""
    
    # Initialize model with config
    model = ArabicNERModel(
        model_name=cfg.model_name,
        max_length=cfg.max_sequence_length
    )
    
    # Create data loader with honorifics
    honorifics = (cfg.honorifics.before_honorifics + 
                 cfg.honorifics.after_honorifics)
    
    data_loader = create_data_loader(
        batch_size=cfg.batch_size,
        honorifics=honorifics,
        cities=cfg.locations.cities
    )
    
    # Train model
    trainer = Trainer(
        model=model,
        learning_rate=cfg.learning_rate,
        data_loader=data_loader
    )
    
    trainer.train()

if __name__ == "__main__":
    train_arabic_ner()
```

### Usage:

```bash
# Train with default configuration
python train.py

# Override parameters
python train.py model_name=bert-arabic batch_size=64 learning_rate=1e-4

# Use different honorifics set
python train.py honorifics=minimal

# Multi-run for hyperparameter tuning
python train.py --multirun learning_rate=1e-4,2e-4,3e-4 batch_size=16,32,64
```

## 🔍 Debugging and Logging

### Enable Full Error Traces

```bash
export HYDRA_FULL_ERROR=1
python script.py
```

### Configuration Inspection

```python
# Print complete configuration
config_manager.print_config()

# Get configuration summary
summary = config_manager.get_config_summary()
print(summary)

# Save configuration for inspection
config_manager.save_config("debug_config.yaml")
```

## 🌟 Best Practices

### 1. Configuration Organization

- **Group related configurations**: Put similar configs in the same directory
- **Use meaningful names**: `honorifics/scholarly.yaml` vs `honorifics/config1.yaml`
- **Default configurations**: Always provide sensible defaults
- **Documentation**: Comment your YAML files extensively

### 2. Parameter Naming

```yaml
# Good: Clear and descriptive
model_name: "arabic-bert-base"
max_sequence_length: 512
learning_rate: 2e-5

# Avoid: Cryptic abbreviations
mdl: "ab-base"
max_seq: 512
lr: 2e-5
```

### 3. Environment Separation

```yaml
# conf/env/development.yaml
batch_size: 8
model_name: "dev-arabic-ner"
debug: true

# conf/env/production.yaml  
batch_size: 64
model_name: "prod-arabic-ner-v1.0"
debug: false
```

### 4. Version Control

```gitignore
# .gitignore
outputs/          # Hydra output directory
.hydra/          # Hydra metadata
*.log            # Log files
experiments/     # Experiment results

# Keep configuration files
!conf/
!*.yaml
```

## 🚨 Common Issues and Solutions

### 1. Configuration Not Found

```bash
# Error: Config file not found
# Solution: Check config_path and config_name
python script.py --config-path=./conf --config-name=config
```

### 2. Override Syntax Errors

```bash
# Wrong: spaces around =
python script.py batch_size = 32

# Correct: no spaces
python script.py batch_size=32

# Wrong: quotes in command line  
python script.py model_name="my-model"

# Correct: no quotes needed
python script.py model_name=my-model
```

### 3. Configuration Composition Issues

```yaml
# Wrong: Missing _self_ in defaults
defaults:
  - honorifics: default
  - titles: default

# Correct: Include _self_
defaults:
  - honorifics: default
  - titles: default
  - _self_
```

### 4. Type Conversion Problems

```bash
# Hydra automatically converts types
python script.py batch_size=32        # int
python script.py learning_rate=1e-4   # float  
python script.py case_sensitive=true  # bool
python script.py model_name=my-model  # string
```

## 📈 Performance Tips

1. **Lazy Loading**: Hydra loads configs on-demand
2. **Config Caching**: Configurations are cached between runs
3. **Minimal Overrides**: Only override what you need to change
4. **Structured Configs**: Use dataclasses for type safety and performance

## 🔗 Integration Examples

### With Weights & Biases

```python
@hydra.main(version_base=None, config_path="conf", config_name="config")
def train_with_wandb(cfg: DictConfig) -> None:
    import wandb
    
    # Initialize wandb with Hydra config
    wandb.init(
        project="arabic-ner",
        config=OmegaConf.to_container(cfg, resolve=True)
    )
    
    # Training code here
    # ...
```

### With MLflow

```python
@hydra.main(version_base=None, config_path="conf", config_name="config")
def train_with_mlflow(cfg: DictConfig) -> None:
    import mlflow
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params(OmegaConf.to_container(cfg, resolve=True))
        
        # Training code here
        # ...
```

This comprehensive setup gives you a robust, scalable configuration management system for your Arabic NER project using Hydra!