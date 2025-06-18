# turathllm_cookiecutter/

## 📁 Project Root
.
├── turathllm/                        # 📦 Core package code
│   ├── __init__.py
│   ├── annotators/
│   ├── loaders/
│   ├── processors/
│   └── utils/
├── tests/                           # ✅ Unit tests
│   └── test_basic.py
├── scripts/                         # 🛠️ CLI or automation scripts
│   └── run_pipeline.py
├── pyproject.toml                   # 📜 Central config
├── README.md
└── .gitignore

# pyproject.toml

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "turathllm"
version = "0.1.0"
description = "Structuring Arabic heritage texts using LLMs and knowledge graphs."
authors = [
    { name = "m.lotfi", email = "you@example.com" }
]
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlmodel",
    "pydantic>=2.0",
    "camel-tools",
    "jinja2",
    "duckdb",
    "neo4j",
    "beautifulsoup4"
]
requires-python = ">=3.10"

[project.optional-dependencies]
dev = [
    "black",
    "isort",
    "ruff",
    "pytest",
    "mypy"
]

[tool.black]
line-length = 88
target-version = ["py310"]

[tool.isort]
profile = "black"

[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I"]

[tool.pytest.ini_options]
addopts = "-v"
testpaths = ["tests"]

# README.md (example snippet)

# TurathLLM 🕌⚡🐉

A modular system to extract, analyze, and structure classical Arabic texts using LLMs, graphs, and AI pipelines.

## Features
- 🧠 Semantic annotation via Ollama or other local LLMs
- 🔗 Narrator chain graph generation (Neo4j)
- 🧽 Regex & source ingestion to SQLite
- 🧱 Schema-based structured storage
- 🧪 Dev tools preconfigured: Black, Ruff, Pytest

## Getting Started
```bash
git clone turathllm
cd turathllm
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```