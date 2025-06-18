Based on your project structure, here's a comprehensive `pyproject.toml` file that's well-suited for your multi-service architecture:This `pyproject.toml` is specifically tailored for your Turath platform with the following key features:

## **Key Highlights:**

### **🏗️ Project Structure Support**
- Recognizes your multi-service architecture (`TurathAnnotator`, `TurathIngestor`)
- Includes shared `modules` package
- Handles your config management system

### **📦 Dependencies**
- **Web Framework**: FastAPI + Uvicorn for your API
- **Configuration**: Pydantic + PyYAML for your config system
- **ML/NLP**: Transformers, PyTorch, scikit-learn for hadith grading
- **Arabic Text**: PyArabic, CAMeL Tools for Arabic processing
- **Database**: SQLAlchemy, MongoDB support
- **Development**: Full testing, linting, formatting setup

### **🚀 CLI Commands**
```bash
# After installation, you can run:
turath-annotator    # Starts the annotation service
turath-ingestor     # Starts the ingestion service  
turath-config       # Manages configurations
```

### **🔧 Development Setup**
```bash
# Install for development
pip install -e ".[dev,test,ml]"

# Install everything
pip install -e ".[all]"

# Production install
pip install -e ".[prod]"
```

### **🎯 Tool Integration**
- **Black**: Code formatting
- **isort**: Import sorting  
- **mypy**: Type checking
- **pytest**: Testing with coverage
- **Ruff**: Fast linting (modern alternative to flake8)

## **Installation & Usage:**

1. **Place this file** in your project root (same level as your services)

2. **Install in development mode:**
```bash
pip install -e ".[dev,test]"
```

3. **Your sysconfig will now work perfectly:**
```python
from utils.sysconfig import find_project_root
find_project_root()  # Will find pyproject.toml and add project root
```

4. **Run development tools:**
```bash
# Format code
black .

# Sort imports  
isort .

# Type check
mypy TurathAnnotator TurathIngestor modules

# Run tests
pytest

# Lint code
ruff check .
```

The configuration recognizes your unique structure and ensures all your services, modules, and configs work together seamlessly!