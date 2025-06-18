# Project Structure Details

## Root Directories

### configs
- **grading_schema.yml**: Configuration for grading criteria
- **sources.yml**: Data source configurations

### data
- **db/**: Database related files
  - `external/`: Third-party data
  - `interim/`: Intermediate processed data
  - `processed/`: Final processed datasets

### modules
Core functionality modules:
- **annotators/**: Text annotation components
- **db/**: Database operations
- **parsing/**: Text parsing utilities
- **regex/**: Regular expression patterns
  - `patterns.py`: Defined regex patterns
- **scorers/**: Scoring algorithms
- **utils/**: Helper functions

### TurathAnnotator
Main annotation service:
- **annotator.py**: Core annotation logic
- **main.py**: Entry point
- **data/**: Service-specific data
  - `external/`: External resources
  - `interim/`: Processing stages
  - `processed/`: Final data
  - `raw/`: Original data
- **ETL/**: Extract-Transform-Load pipelines
- **models/**: Machine learning models
  - `ollama/`: Ollama model configurations
- **schemas/**: Data schemas
- **src/**
  - `annotators/`: Annotation implementations
  - `scorers/`: Scoring implementations

### TurathIngestor
Data ingestion service:
- **db_loader.py**: Database loading utilities
- **main.py**: Entry point
- **data/**: Similar structure to TurathAnnotator
- **ETL/**: Data pipeline components
- **schemas/**: Data validation schemas
- **src/**: Core implementation

### Support Directories
- docs: Project documentation
- external_modules: Third-party dependencies
- notebooks: Jupyter notebooks for analysis
- reports: Generated reports and outputs