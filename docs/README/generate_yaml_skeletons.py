import yaml
from pathlib import Path

# Define your skeleton structures here
CONFIG_TEMPLATES = {
    "grading_keywords.yaml": {
        "authenticity": {
            "sahih": {
                "score": 5,
                "keywords": ["صحيح", "authentic"]
            },
            "hasan": {
                "score": 4,
                "keywords": ["حسن", "good"]
            },
            "daif": {
                "score": 2,
                "keywords": ["ضعيف", "weak"]
            }
        },
        "isnaad_status": {
            "muttasil": {
                "score": 5,
                "keywords": ["متصل", "connected"]
            },
            "munqati": {
                "score": 1,
                "keywords": ["منقطع", "broken"]
            }
        }
    },

    "entity_roles.yaml": {
        "narrator": ["rawi", "narrator", "transmitter"],
        "judge": ["authenticator", "critic"],
        "compiler": ["author", "muhaddith"]
    },

    "matn_defects.yaml": {
        "munkar": {
            "description": "Contradicts more authentic reports.",
            "score": 1,
            "keywords": ["منكر", "rejected"]
        },
        "shadh": {
            "description": "Odd narration by a reliable narrator.",
            "score": 2,
            "keywords": ["شاذ", "anomalous"]
        },
        "mudraj": {
            "description": "Interjected statements by narrators.",
            "score": 2,
            "keywords": ["مدرج", "interpolated"]
        }
    }
}


def generate_yaml_files(config_dir="config"):
    Path(config_dir).mkdir(parents=True, exist_ok=True)
    for filename, content in CONFIG_TEMPLATES.items():
        path = Path(config_dir) / filename
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, sort_keys=False, allow_unicode=True)
        print(f"✅ Created: {path}")

if __name__ == "__main__":
    generate_yaml_files()


# pip install pydantic pyyaml
# pip install fastapi uvicorn

# main.py
from config_loader import load_grading_config

cfg = load_grading_config("config/grading_keywords.yaml")

# Example usage:
print(cfg.authenticity.__root__["sahih"].keywords)


class Settings(BaseModel):
    hadith: HadithSettings
    model: ModelSettings
    
class HadithSettings(BaseModel):
    grading_keywords: GradingKeywords
    entity_roles: EntityRoles
    matn_defects: MatnDefects
    
from pydantic import BaseModel
class AppConfig(BaseModel):
    host: str
    port: int


🥇 1. Pydantic (✅ You’re already using it — good choice!)
Best for: Typed config from YAML, JSON, env vars

Key strength: Validation, type hints, auto docs

Example:

python
Copy
Edit
from pydantic import BaseModel
class AppConfig(BaseModel):
    host: str
    port: int
🥈 2. Dynaconf
Best for: Multi-environment configs (dev/staging/prod), layered config

Supports: .toml, .yaml, .json, .env, Python files

Use Case: Want settings.dev.yaml, settings.prod.yaml, etc.

Example:

python
Copy
Edit
from dynaconf import Dynaconf
settings = Dynaconf(settings_files=['settings.yaml'])
print(settings.DEBUG)
🥉 3. Hydra
Best for: Complex ML pipelines, nested configs, CLI overrides

Big in ML community: Used in Facebook AI projects

Supports: YAML composition, config groups

Example:

bash
Copy
Edit
python main.py model=bert optimizer=adam
🛠️ 4. OmegaConf
Built for: Deep merging, dot-access, dynamic overrides

Often used with Hydra

Example:

python
Copy
Edit
from omegaconf import OmegaConf
cfg = OmegaConf.load("config.yaml")
print(cfg.model.name)
🧱 5. ConfigArgParse
Like argparse, but supports .ini, .yaml, .json and CLI

Example:

python
Copy
Edit
import configargparse
p = configargparse.ArgParser(default_config_files=['config.yaml'])
TL;DR – What to Use When
Lib	Use Case	Strengths
pydantic	Typed YAML/JSON/env	Clean schema, validation
dynaconf	Layered environments	Flexible, no boilerplate
hydra	ML/CLI override systems	Config composition, experiments
omegaconf	Merge-heavy hierarchical config	Dot access, works great with Hydra
configargparse	CLI-first with file fallback	Command-line + config hybrid

