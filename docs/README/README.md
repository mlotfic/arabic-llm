# 🅊️ Hadith NLP Config Project Boilerplate

This is a practical, production-ready starter template for managing configuration-driven Hadith NLP or classical Arabic data annotation pipelines. It uses Pydantic models, YAML config files, and supports modular design for multi-agent NLP workflows.

---

## 📁 Project Structure

```
.
├── config/
│   ├── hadith/
│   │   ├── grading_keywords.yaml
│   │   ├── matn_defects.yaml
│   │   └── entity_roles.yaml
│   ├── model/
│   │   ├── bert.yaml
│   │   └── random_forest.yaml
│   ├── paths/
│   │   └── data.yaml
│   ├── pipeline/
│   │   └── steps.yaml
│
├── generate_yaml_skeletons.py    # 🔧 YAML config bootstrapper
├── config_loader.py              # ✅ Pydantic-based loader
├── models.py                     # 🔐 Validation schema
├── api.py                        # 🚀 FastAPI app exposing configs
├── main.py                       # 🧪 Sample usage
├── TurathAnnotator/              # 🧠 Annotation service
│   ├── annotator.py
│   ├── main.py
│   ├── data/
│   │   ├── external/
│   │   ├── interim/
│   │   ├── processed/
│   │   └── raw/
│   ├── ETL/
│   ├── models/
│   │   └── ollama/
│   ├── schemas/
│   └── src/
│       ├── annotators/
│       └── scorers/
├── TurathIngestor/               # 📥 Data ingestion service
│   ├── db_loader.py
│   ├── main.py
│   ├── data/
│   ├── ETL/
│   ├── schemas/
│   └── src/
│
├── modules/                      # ⚙️ Core shared modules
│   ├── annotators/
│   ├── db/
│   ├── parsing/
│   ├── regex/
│   │   └── patterns.py
│   ├── scorers/
│   └── utils/
│
├── data/                         # 📊 Central data folder
│   ├── db/
│   │   ├── external/
│   │   ├── interim/
│   │   └── processed/
│
├── configs/                      # ⚙️ Project configs
│   ├── grading_schema.yml
│   └── sources.yml
│
├── docs/                         # 📚 Documentation
├── external_modules/             # 🧩 Third-party code
├── notebooks/                    # 📓 Jupyter notebooks
├── reports/                      # 📑 Reports and generated output
└── README.md
```

---

## ⚙️ Setup

```bash
pip install pydantic pyyaml fastapi uvicorn
python generate_yaml_skeletons.py
```

---

## ✅ Usage Example

```python
from config_loader import load_grading_config
cfg = load_grading_config("config/hadith/grading_keywords.yaml")
print(cfg.authenticity.__root__["sahih"].keywords)
```

---

## 🔥 FastAPI Example (`api.py`)

```python
from fastapi import FastAPI
from config_loader import load_grading_config

app = FastAPI()

@app.get("/grading")
def get_grading():
    config = load_grading_config("config/hadith/grading_keywords.yaml")
    return config.dict()
```

Run it with:

```bash
uvicorn api:app --reload
```

Then visit: [http://localhost:8000/grading](http://localhost:8000/grading)

---

## 🧠 Design Best Practices

### ✅ Domain-Specific YAMLs

* `grading_keywords.yaml`: Tagging authenticity, isnaad status
* `matn_defects.yaml`: Detect and score matn-related issues
* `entity_roles.yaml`: Role tagging for narrator/critic/compiler

### 💼 Naming Conventions

Use `domain_purpose.yaml` (e.g. `hadith_grading.yaml`) to avoid collisions and clarify intent.

### 🖊️ Validation with Pydantic

Schema-based models ensure correctness and IDE autocompletion:

```python
class GradingItem(BaseModel):
    score: int
    keywords: List[str]
```

### 🚧 Generate Config Skeletons

```bash
python generate_yaml_skeletons.py
```

This auto-creates your config scaffolding with common defaults.

---

## 📊 Extend the System

* Add more YAMLs in `config/`
* Add corresponding models in `models.py`
* Update `config_loader.py` to support new types
* Add new FastAPI endpoints in `api.py`

---

## 🚀 Use Cases

* Hadith grading classifier
* Narrator graph visualizer
* Chain scoring tools
* Book OCR to structure pipelines
* Named entity linking for classical texts

---

## ✨ Summary Principle

> Treat your YAMLs like API contracts. Modular, validated, reusable.

This structure is scalable to any domain: Arabic contracts, medical text, poetry tagging, legal NLP, etc.

---

