# config/paths.py
import os

# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# DATA_RAW = os.path.join(PROJECT_ROOT, 'data', 'raw')
# DATA_PROCESSED = os.path.join(PROJECT_ROOT, 'data', 'processed')
# DATA_INTERIM = os.path.join(PROJECT_ROOT, 'data', 'interim')
# DATA_EXTERNAL = os.path.join(PROJECT_ROOT, 'data', 'external')

# config/paths.py
"""
Enhanced project path configuration using ProjectPathManager.
Provides robust, portable, and feature-rich path management.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Union
from dataclasses import dataclass

# Import our enhanced path manager
# Assuming sysconfig.py is in utils/ or config/ directory
try:
    from utils.sysconfig import ProjectPathManager
except ImportError:
    try:
        from .sysconfig import ProjectPathManager
    except ImportError:
        # Fallback: create a minimal version if not available
        class ProjectPathManager:
            def find_project_root(self):
                return Path(__file__).resolve().parent.parent


@dataclass
class ProjectPaths:
    """Data class to hold all project paths with validation."""
    
    # Core directories
    root: Path
    config: Path
    src: Path
    data: Path
    tests: Path
    docs: Path
    scripts: Path
    
    # Data subdirectories
    data_raw: Path
    data_processed: Path
    data_interim: Path
    data_external: Path
    data_models: Path
    data_features: Path
    
    # Output directories
    outputs: Path
    reports: Path
    figures: Path
    logs: Path
    
    # Cache and temporary
    cache: Path
    temp: Path
    
    def __post_init__(self):
        """Validate and create directories if needed."""
        # Convert strings to Path objects if necessary
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, str):
                setattr(self, field_name, Path(field_value))
    
    def create_directories(self, ignore_errors: bool = True) -> List[Path]:
        """Create all directories that don't exist."""
        created = []
        
        for field_name, path in self.__dict__.items():
            if isinstance(path, Path):
                try:
                    if not path.exists():
                        path.mkdir(parents=True, exist_ok=True)
                        created.append(path)
                        print(f"✓ Created directory: {path}")
                except Exception as e:
                    if not ignore_errors:
                        raise
                    print(f"⚠ Could not create {path}: {e}")
        
        return created
    
    def validate_paths(self) -> Dict[str, bool]:
        """Validate that all paths exist."""
        validation = {}
        
        for field_name, path in self.__dict__.items():
            if isinstance(path, Path):
                validation[field_name] = path.exists()
        
        return validation
    
    def get_relative_paths(self) -> Dict[str, str]:
        """Get all paths relative to project root."""
        relative_paths = {}
        
        for field_name, path in self.__dict__.items():
            if isinstance(path, Path) and field_name != 'root':
                try:
                    relative_paths[field_name] = str(path.relative_to(self.root))
                except ValueError:
                    # Path is outside project root
                    relative_paths[field_name] = str(path)
        
        return relative_paths
    
    def print_structure(self):
        """Print the project directory structure."""
        print("📁 Project Directory Structure:")
        print(f"Root: {self.root}")
        
        relative_paths = self.get_relative_paths()
        validation = self.validate_paths()
        
        for name, rel_path in sorted(relative_paths.items()):
            exists_marker = "✓" if validation.get(name, False) else "✗"
            print(f"  {exists_marker} {name}: {rel_path}")


class PathManager:
    """Enhanced path manager that combines ProjectPathManager with structured paths."""
    
    def __init__(self, auto_setup: bool = True):
        self.pm = ProjectPathManager()
        self._paths: Optional[ProjectPaths] = None
        
        if auto_setup:
            self.setup_project_root()
    
    def setup_project_root(self) -> Optional[Path]:
        """Setup project root using multiple strategies."""
        # Strategy 1: Auto-detection
        root = self.pm.auto_detect_and_add_root()
        if root:
            print(f"✓ Auto-detected project root: {root}")
            return root
        
        # Strategy 2: Find by markers
        root = self.pm.find_project_root([
            'pyproject.toml', 'setup.py', '.git', 'requirements.txt',
            'Pipfile', 'poetry.lock', 'environment.yml', 'Makefile'
        ])
        if root:
            print(f"✓ Found project root by markers: {root}")
            return root
        
        # Strategy 3: Manual detection (config file is typically 1 level down)
        root = self.pm.add_project_root(levels_up=1)
        if root:
            print(f"✓ Set project root manually: {root}")
            return root
        
        print("⚠ Could not determine project root")
        return None
    
    def get_project_root(self) -> Path:
        """Get the project root path."""
        if hasattr(self.pm, '_project_root') and self.pm._project_root:
            return self.pm._project_root
        
        # Fallback to traditional method
        return Path(__file__).resolve().parent.parent
    
    def get_paths(self, create_dirs: bool = False) -> ProjectPaths:
        """Get structured project paths."""
        if self._paths is None:
            self._paths = self._create_project_paths()
        
        if create_dirs:
            self._paths.create_directories()
        
        return self._paths
    
    def _create_project_paths(self) -> ProjectPaths:
        """Create ProjectPaths instance with all standard directories."""
        root = self.get_project_root()
        
        return ProjectPaths(
            # Core directories
            root=root,
            config=root / 'config',
            src=root / 'src',
            data=root / 'data',
            tests=root / 'tests',
            docs=root / 'docs',
            scripts=root / 'scripts',
            
            # Data subdirectories
            data_raw=root / 'data' / 'raw',
            data_processed=root / 'data' / 'processed',
            data_interim=root / 'data' / 'interim',
            data_external=root / 'data' / 'external',
            data_models=root / 'data' / 'models',
            data_features=root / 'data' / 'features',
            
            # Output directories
            outputs=root / 'outputs',
            reports=root / 'reports',
            figures=root / 'figures',
            logs=root / 'logs',
            
            # Cache and temporary
            cache=root / '.cache',
            temp=root / 'temp',
        )
    
    def add_custom_paths(self, **custom_paths) -> ProjectPaths:
        """Add custom paths to the project structure."""
        paths = self.get_paths()
        root = paths.root
        
        for name, path_str in custom_paths.items():
            if isinstance(path_str, str):
                # Convert relative paths to absolute
                if not os.path.isabs(path_str):
                    custom_path = root / path_str
                else:
                    custom_path = Path(path_str)
            else:
                custom_path = Path(path_str)
            
            setattr(paths, name, custom_path)
            print(f"✓ Added custom path {name}: {custom_path}")
        
        return paths
    
    def setup_data_science_structure(self) -> ProjectPaths:
        """Setup paths optimized for data science projects."""
        paths = self.get_paths()
        
        # Add data science specific paths
        self.add_custom_paths(
            notebooks=root / 'notebooks',
            experiments=root / 'experiments',
            models=root / 'models',
            checkpoints=root / 'checkpoints',
            data_samples=root / 'data' / 'samples',
            data_labels=root / 'data' / 'labels',
            data_predictions=root / 'data' / 'predictions',
            plots=root / 'plots',
            tensorboard=root / 'runs',
        )
        
        return paths
    
    def setup_web_project_structure(self) -> ProjectPaths:
        """Setup paths optimized for web development projects."""
        paths = self.get_paths()
        
        # Add web development specific paths
        self.add_custom_paths(
            static=root / 'static',
            templates=root / 'templates',
            media=root / 'media',
            assets=root / 'assets',
            migrations=root / 'migrations',
            locale=root / 'locale',
            fixtures=root / 'fixtures',
        )
        
        return paths
    
    def get_file_level_info(self) -> Dict[str, Union[int, Path]]:
        """Get information about current file's position."""
        return {
            'current_file': Path(__file__).resolve(),
            'project_root': self.get_project_root(),
            'file_level': self.pm.get_current_file_level_from_root(),
            'relative_path': Path(__file__).resolve().relative_to(self.get_project_root())
        }


# ============================================================================
# BACKWARD COMPATIBILITY - Traditional approach enhanced
# ============================================================================

# Initialize the enhanced path manager
_path_manager = PathManager()

# Get project paths
PROJECT_PATHS = _path_manager.get_paths(create_dirs=False)

# Traditional variables for backward compatibility
PROJECT_ROOT = str(PROJECT_PATHS.root)
DATA_RAW = str(PROJECT_PATHS.data_raw)
DATA_PROCESSED = str(PROJECT_PATHS.data_processed)
DATA_INTERIM = str(PROJECT_PATHS.data_interim)
DATA_EXTERNAL = str(PROJECT_PATHS.data_external)

# Enhanced variables (using Path objects)
PATHS = PROJECT_PATHS

# Additional commonly used paths
CONFIG_DIR = str(PROJECT_PATHS.config)
SRC_DIR = str(PROJECT_PATHS.src)
TESTS_DIR = str(PROJECT_PATHS.tests)
DOCS_DIR = str(PROJECT_PATHS.docs)
LOGS_DIR = str(PROJECT_PATHS.logs)
OUTPUTS_DIR = str(PROJECT_PATHS.outputs)

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_data_path(filename: str, data_type: str = 'raw') -> Path:
    """Get path to a data file in specified data directory."""
    data_dirs = {
        'raw': PROJECT_PATHS.data_raw,
        'processed': PROJECT_PATHS.data_processed,
        'interim': PROJECT_PATHS.data_interim,
        'external': PROJECT_PATHS.data_external,
        'models': PROJECT_PATHS.data_models,
        'features': PROJECT_PATHS.data_features,
    }
    
    if data_type not in data_dirs:
        raise ValueError(f"Invalid data_type. Choose from: {list(data_dirs.keys())}")
    
    return data_dirs[data_type] / filename

def get_output_path(filename: str, output_type: str = 'outputs') -> Path:
    """Get path to an output file in specified output directory."""
    output_dirs = {
        'outputs': PROJECT_PATHS.outputs,
        'reports': PROJECT_PATHS.reports,
        'figures': PROJECT_PATHS.figures,
        'logs': PROJECT_PATHS.logs,
    }
    
    if output_type not in output_dirs:
        raise ValueError(f"Invalid output_type. Choose from: {list(output_dirs.keys())}")
    
    return output_dirs[output_type] / filename

def create_project_directories():
    """Create all project directories."""
    created = PROJECT_PATHS.create_directories()
    if created:
        print(f"Created {len(created)} directories")
    else:
        print("All directories already exist")

def validate_project_structure() -> bool:
    """Validate that essential project directories exist."""
    validation = PROJECT_PATHS.validate_paths()
    
    essential_dirs = ['root', 'data', 'data_raw', 'data_processed']
    missing = [name for name in essential_dirs if not validation.get(name, False)]
    
    if missing:
        print(f"⚠ Missing essential directories: {missing}")
        return False
    
    print("✓ Project structure validation passed")
    return True

def print_project_info():
    """Print comprehensive project information."""
    print("=" * 60)
    print("PROJECT INFORMATION")
    print("=" * 60)
    
    # File level information
    info = _path_manager.get_file_level_info()
    print(f"Current file: {info['current_file'].name}")
    print(f"Project root: {info['project_root']}")
    print(f"File level from root: {info['file_level']}")
    print(f"Relative path: {info['relative_path']}")
    print()
    
    # Directory structure
    PROJECT_PATHS.print_structure()
    print()
    
    # Validation status
    validate_project_structure()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("Enhanced Project Path Configuration")
    print("=" * 50)
    
    # Example 1: Basic usage (backward compatible)
    print("\n1. Traditional usage (backward compatible):")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"DATA_RAW: {DATA_RAW}")
    print(f"DATA_PROCESSED: {DATA_PROCESSED}")
    
    # Example 2: Enhanced usage with Path objects
    print("\n2. Enhanced usage with Path objects:")
    print(f"Raw data dir: {PATHS.data_raw}")
    print(f"Processed data dir: {PATHS.data_processed}")
    print(f"Reports dir: {PATHS.reports}")
    
    # Example 3: Convenience functions
    print("\n3. Using convenience functions:")
    raw_file = get_data_path('dataset.csv', 'raw')
    processed_file = get_data_path('clean_dataset.pkl', 'processed')
    report_file = get_output_path('analysis_report.html', 'reports')
    
    print(f"Raw file path: {raw_file}")
    print(f"Processed file path: {processed_file}")
    print(f"Report file path: {report_file}")
    
    # Example 4: Project information
    print("\n4. Project information:")
    print_project_info()
    
    # Example 5: Create directories
    print("\n5. Creating project directories:")
    create_project_directories()
    
    # Example 6: Data science project setup
    print("\n6. Data science project setup:")
    ds_paths = _path_manager.setup_data_science_structure()
    print("Data science directories configured")
    
    # Example 7: Custom paths
    print("\n7. Adding custom paths:")
    custom_paths = _path_manager.add_custom_paths(
        custom_data='data/custom',
        experiments='experiments',
        results='results/latest'
    )
    print("Custom paths added")


# ============================================================================
# MIGRATION GUIDE FROM TRADITIONAL APPROACH
# ============================================================================

"""
MIGRATION GUIDE: From traditional os.path to enhanced PathManager

OLD WAY (your current approach):
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    DATA_RAW = os.path.join(PROJECT_ROOT, 'data', 'raw')

NEW WAY (enhanced):
    from config.paths import PATHS, get_data_path
    
    # Path objects (recommended)
    raw_data_dir = PATHS.data_raw
    
    # Specific file paths
    dataset_path = get_data_path('dataset.csv', 'raw')
    
    # Still backward compatible
    DATA_RAW = str(PATHS.data_raw)  # Same as your old variable

BENEFITS OF NEW APPROACH:
✅ Automatic project root detection
✅ Path validation and directory creation
✅ Cross-platform compatibility (Path objects)
✅ Type hints and IDE support
✅ Extensible for different project types
✅ Backward compatible with existing code
✅ Better error handling
✅ Project structure introspection

SIMPLE MIGRATION STEPS:
1. Replace your current config/paths.py with this enhanced version
2. Your existing code using DATA_RAW, etc. will still work
3. Gradually migrate to using PATHS.data_raw for new code
4. Use convenience functions like get_data_path() for file operations
"""