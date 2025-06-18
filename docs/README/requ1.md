Here are several ways to get the dependencies for your project:

## **1. Using pip (Recommended)**

### **Install all dependencies at once:**
```bash
# Basic installation with core dependencies
pip install -e .

# Development setup (includes testing, linting, etc.)
pip install -e ".[dev]"

# Full development setup with all optional dependencies
pip install -e ".[all]"

# Just the ML/AI dependencies
pip install -e ".[ml]"
```

### **Install specific dependency groups:**
```bash
pip install -e ".[test]"        # Testing tools
pip install -e ".[docs]"        # Documentation tools  
pip install -e ".[notebook]"    # Jupyter notebooks
pip install -e ".[prod]"        # Production dependencies
```

## **2. Generate requirements.txt files**

### **From pyproject.toml:**
```bash
# Install pip-tools first
pip install pip-tools

# Generate requirements.txt from pyproject.toml
pip-compile pyproject.toml

# Generate dev requirements
pip-compile --extra dev pyproject.toml -o requirements-dev.txt

# Generate production requirements  
pip-compile --extra prod pyproject.toml -o requirements-prod.txt
```

### **Manual requirements.txt creation:**## **3. Step-by-Step Installation Guide**

### **Option A: Clean Installation**
```bash
# 1. Create virtual environment
python -m venv turath-env
source turath-env/bin/activate  # On Windows: turath-env\Scripts\activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install your project
pip install -e ".[dev,test,ml]"
```

### **Option B: Using requirements files**
```bash
# Create the requirements files from the artifact above, then:
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## **4. Dependency Management with Poetry (Alternative)**

### **Convert to Poetry:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialize (if starting fresh)
poetry init

# Install dependencies
poetry install

# Add new dependencies
poetry add fastapi uvicorn pydantic
poetry add --group dev pytest black mypy
```

### **Poetry pyproject.toml (alternative format):**
```toml
[tool.poetry]
name = "turath-platform"
version = "0.1.0"
description = "Islamic text annotation platform"

[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
# ... other dependencies

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.10.0"
# ... other dev dependencies
```

## **5. Docker Approach**

### **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e ".[prod]"

COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Using Docker Compose:**
```yaml
version: '3.8'
services:
  turath-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
```

## **6. Environment-Specific Installation**

### **Development Environment:**
```bash
# Install everything needed for development
pip install -e ".[dev,test,docs,notebook]"

# Set up pre-commit hooks
pre-commit install
```

### **Production Environment:**
```bash
# Minimal production install
pip install -e ".[prod]" --no-dev
```

### **CI/CD Environment:**
```bash
# Testing environment
pip install -e ".[test]"
pytest
```

## **7. Troubleshooting Common Issues**

### **PyTorch Installation Issues:**
```bash
# For CPU-only PyTorch (lighter)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA support (if you have GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### **Arabic Text Processing Issues:**
```bash
# If CAMeL Tools fails
pip install camel-tools --no-deps
pip install requests six

# Alternative Arabic processing
pip install arabic-reshaper python-bidi
```

### **Database Connection Issues:**
```bash
# PostgreSQL
sudo apt-get install libpq-dev  # Ubuntu/Debian
brew install postgresql          # macOS

# Or use pure Python alternative
pip install psycopg2-binary
```

## **8. Verification**

### **Check installation:**
```bash
# Verify key packages
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"

# Test your imports
python -c "from TurathAnnotator.main import app; print('Annotator: OK')"
python -c "from TurathIngestor.main import app; print('Ingestor: OK')"
```

### **Run your services:**
```bash
# Test the annotation service
python -m TurathAnnotator.main

# Test the ingestion service  
python -m TurathIngestor.main

# Test the API
uvicorn api:app --reload
```

## **9. Recommended Installation Sequence**

```bash
# 1. Set up environment
python -m venv turath-env
source turath-env/bin/activate

# 2. Install build tools
pip install --upgrade pip setuptools wheel

# 3. Install your project
pip install -e ".[dev,test]"

# 4. Verify installation
python -c "from utils.sysconfig import find_project_root; find_project_root(); print('Setup complete!')"

# 5. Run tests to verify everything works
pytest tests/ -v
```

This approach ensures all dependencies are properly installed and your project structure is recognized correctly!