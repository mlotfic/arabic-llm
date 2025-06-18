# ✅ Cookiecutter-style layout for loading YAML into dicts using Hydra + Pydantic

# 📁 Directory structure
# project/
# ├── conf/
# │   ├── config.yaml
# │   └── surah/
# │       └── mapping.yaml
# ├── data_static/
# │   └── surah_mapping.yaml
# ├── main.py
# └── schemas.py

# ------------------
# conf/config.yaml
# ------------------
defaults:
  - surah/mapping
  - _self_

load_surah: true

# -----------------------------
# conf/surah/mapping.yaml
# -----------------------------
surah_mapping: ${file:data_static/surah_mapping.yaml}

# -----------------------------
# data_static/surah_mapping.yaml
# -----------------------------
الفاتحة: 1
البقرة: 2
آل عمران: 3
النساء: 4
المائدة: 5

# -------------------
# schemas.py
# -------------------
from pydantic import BaseModel, conint
from typing import Dict

class SurahMappingSchema(BaseModel):
    surah_mapping: Dict[str, conint(ge=1, le=114)]

# -------------------
# main.py
# -------------------
from hydra import initialize, compose
from omegaconf import OmegaConf
from pydantic import ValidationError
from schemas import SurahMappingSchema


def main():
    with initialize(config_path="conf", version_base=None):
        cfg = compose(config_name="config.yaml")

        print("\n✨ Loaded Hydra config:")
        print(OmegaConf.to_yaml(cfg))

        if cfg.load_surah and "surah_mapping" in cfg:
            try:
                validated = SurahMappingSchema(**cfg)
                surah_dict = validated.surah_mapping
                print("\n📄 Surah mapping loaded:")
                print(surah_dict)
            except ValidationError as e:
                print("\n🚫 Validation error:", e)
        else:
            print("\n🚧 Skipping surah mapping load.")


if __name__ == "__main__":
    main()
