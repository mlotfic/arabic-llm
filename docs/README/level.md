I'll add a method to get the current file's level from the project root. This will be useful for understanding the directory depth and for dynamic path calculations.I've enhanced the `ProjectPathManager` class with several new methods to handle file level detection and provide more comprehensive project path management:

## New Methods Added:

### 1. `get_current_file_level_from_root()`
- Returns the number of directory levels the current file is from the project root
- Works with both `add_project_root()` and `find_project_root()` methods
- Useful for understanding your file's position in the project hierarchy

### 2. `get_project_root()`
- Returns the currently set project root path
- Helps you access the root path after it's been determined

### 3. `get_file_info()`
- Returns a tuple of `(current_file_path, project_root_path, levels_from_root)`
- Provides comprehensive information about the file's position

### 4. `calculate_levels_to_reach(target_path)`
- Calculates how many levels up you need to go to reach a specific target directory
- Useful for dynamic path calculations

### 5. `auto_detect_and_add_root()`
- Automatically detects project root using multiple strategies
- First tries marker files, then looks for common project structures
- More robust than manual detection

### 6. `print_project_info()`
- Prints comprehensive debugging information about the current project setup
- Shows file path, root path, level, and relative path

## Key Features:

- **Automatic Level Tracking**: The class now tracks the file's level from root internally
- **Multiple Detection Strategies**: Combines marker-based detection with structure-based detection
- **Dynamic Calculations**: Can calculate levels needed to reach any target directory
- **Comprehensive Info**: Provides detailed information about file positioning
- **Smart Initialization**: Includes patterns for robust project initialization

## Usage Examples:

```python
# Basic level detection
pm = ProjectPathManager()
pm.find_project_root()
level = pm.get_current_file_level_from_root()
print(f"Current file is {level} levels deep")

# Comprehensive information
current_file, root_path, level = pm.get_file_info()

# Auto-detection with fallback
pm = ProjectPathManager()
root = pm.auto_detect_and_add_root()
if root:
    print(f"Auto-detected root: {root}")
```

This enhanced version provides much better introspection capabilities and makes it easier to understand and work with complex project structures.


===

Great question! Let me explain how this helps solve the common Python import problem when you need to import from parent directories, with practical examples.

## The Problem

Python can't import modules from parent directories by default because they're not in `sys.path`. Here's the typical scenario:

```
my_project/
├── config/
│   └── settings.py          # Contains: DATABASE_URL = "..."
├── src/
│   ├── models/
│   │   └── user.py          # Needs settings from config/
│   └── utils/
│       └── helpers.py       # Needs settings from config/
└── tests/
    └── test_user.py         # Needs to import from src/models/
```

## The Traditional (Problematic) Solutions## How ProjectPathManager Solves Import Problems

The `ProjectPathManager` solves the classic Python import problem by **automatically adding your project root to `sys.path`**, making all project modules importable from anywhere.

### The Core Problem
When you have this structure:
```
my_project/
├── config/settings.py
├── src/models/user.py       # Wants to import config.settings
└── tests/test_user.py       # Wants to import src.models.user
```

Python can't find modules in parent directories because they're not in `sys.path`.

### How ProjectPathManager Helps

**1. Automatic Detection & Setup:**
```python
# In src/models/user.py
from ..utils.sysconfig import ProjectPathManager

pm = ProjectPathManager()
pm.auto_detect_and_add_root()  # Finds project root automatically

# Now you can import from anywhere!
from config.settings import DATABASE_URL  # ✅ Works!
```

**2. Level-Aware Imports:**
```python
# In tests/test_user.py (1 level from root)
pm = ProjectPathManager()
pm.add_project_root(levels_up=1)  # Go up 1 level to reach root

from src.models.user import User  # ✅ Works!
from config.settings import DATABASE_URL  # ✅ Works!
```

**3. Smart Fallback Strategy:**
```python
def setup_imports():
    pm = ProjectPathManager()
    
    # Try auto-detection first
    if pm.auto_detect_and_add_root():
        return pm
    
    # Fallback to manual
    if pm.add_project_root(levels_up=2):
        return pm
    
    return None
```

### Key Advantages

1. **No Hard-Coded Paths**: Uses dynamic detection instead of `/absolute/paths`
2. **Portable**: Works when files are moved or project is relocated
3. **Automatic**: Detects project structure using markers (`.git`, `pyproject.toml`, etc.)
4. **Clean**: No complex `os.path` manipulations
5. **Safe**: Cleans up `sys.path` when done

### Real-World Example

```python
# Deep nested file: src/api/v1/endpoints/users.py
from ....utils.sysconfig import ProjectPathManager

pm = ProjectPathManager()
pm.auto_detect_and_add_root()

# Now these imports work from 4 levels deep!
from config.database import DATABASE_URL
from src.models.user import User
from src.services.auth import authenticate

def create_user(data):
    # Can use imports from anywhere in project
    user = User(**data)
    return user.save(DATABASE_URL)
```

This eliminates the need for fragile solutions like:
- `sys.path.append('../../../..')` (breaks when moved)
- Complex relative imports (only work in packages)
- Hard-coded absolute paths (not portable)

The `get_current_file_level_from_root()` method helps you understand exactly how deep your file is, making import decisions easier and debugging simpler.


I'd be happy to explain the "2 levels" concept in detail! This refers to directory traversal in your file system hierarchy.

## **Understanding Directory Levels**

When we say "2 levels up," we're talking about how many parent directories to climb in your project structure.

### **Visual Example:**

```
project_root/                    ← Target (2 levels up from sysconfig.py)
├── src/                        ← 1 level up from sysconfig.py
│   └── utils/                  ← Current directory of sysconfig.py
│       └── sysconfig.py        ← Starting point (__file__)
├── tests/
└── data/
```

## **How `levels_up` Works**

```python
def add_project_root(levels_up=3):
    root = Path(__file__).resolve().parents[levels_up]
    #                                      ^^^^^^^^^^^
    #                                      This is the key part
```

Let's break this down step by step:

### **Step 1: Get current file location**
```python
Path(__file__).resolve()
# Returns: /full/path/to/project_root/src/utils/sysconfig.py
```

### **Step 2: Access parent directories**
```python
parents = Path(__file__).resolve().parents
# parents[0] = /full/path/to/project_root/src/utils/     (immediate parent)
# parents[1] = /full/path/to/project_root/src/           (1 level up)
# parents[2] = /full/path/to/project_root/               (2 levels up)
# parents[3] = /full/path/to/                            (3 levels up)
```

### **Step 3: Select the right level**
```python
root = Path(__file__).resolve().parents[2]  # 2 levels up
# Returns: /full/path/to/project_root/
```

## **Real-World Examples**

### **Example 1: Standard Project Structure**
```
my_project/                     ← We want this as our root
├── setup.py
├── src/                        ← 1 level up
│   ├── __init__.py
│   └── utils/                  ← Current directory
│       └── sysconfig.py        ← This file (levels_up=2)
├── tests/
└── docs/
```

**Usage:**
```python
# In src/utils/sysconfig.py
add_project_root(levels_up=2)  # Goes to my_project/
```

### **Example 2: Deeper Nesting**
```
company_project/                ← We want this as our root
├── pyproject.toml
├── backend/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           └── user.py     ← This file (levels_up=5)
│   └── utils/
│       └── sysconfig.py        ← This file (levels_up=3)
└── frontend/
```

**Usage:**
```python
# In backend/utils/sysconfig.py
add_project_root(levels_up=3)  # Goes to company_project/

# In backend/api/v1/endpoints/user.py
from backend.utils.sysconfig import add_project_root
add_project_root(levels_up=5)  # Goes to company_project/
```

## **Counting Levels Visually**

Here's how to count the levels:

```
project_root/           ← TARGET (what we want to reach)
│
├── level_1/            ← 1 level down from target
│   │
│   └── level_2/        ← 2 levels down from target
│       │
│       └── your_file.py ← Starting point
```

To get from `your_file.py` to `project_root/`, you need to go up **2 levels**.

## **Common Mistakes and How to Avoid Them**

### **Mistake 1: Off-by-one errors**
```python
# Wrong - this goes too far up
add_project_root(levels_up=4)  # Might go to parent of project

# Right - count carefully
add_project_root(levels_up=3)  # Goes to actual project root
```

### **Mistake 2: Not accounting for different file locations**
```python
# This works in src/utils/sysconfig.py
add_project_root(levels_up=2)

# But this same call in tests/unit/test_something.py might need:
add_project_root(levels_up=3)  # Because tests/ is also at root level
```

## **Practical Debugging**

Here's how to figure out the right number:

```python
from pathlib import Path

# See where you are
current_file = Path(__file__).resolve()
print(f"Current file: {current_file}")

# See all parent directories
parents = current_file.parents
for i, parent in enumerate(parents[:6]):  # Show first 6 levels
    print(f"Level {i}: {parent}")
    
# Find your project root manually
print(f"Level 2 up: {parents[2]}")  # Check if this looks right
```

**Example output:**
```
Current file: /Users/john/code/my_project/src/utils/sysconfig.py
Level 0: /Users/john/code/my_project/src/utils
Level 1: /Users/john/code/my_project/src
Level 2: /Users/john/code/my_project          ← This is our project root!
Level 3: /Users/john/code
Level 4: /Users/john
Level 5: /Users
```

## **Why This Matters**

Getting the levels right is crucial because:

1. **Too few levels**: You don't reach the project root, imports fail
2. **Too many levels**: You go beyond your project, might add system directories to path
3. **Just right**: You can import from anywhere in your project

## **Better Alternative: Auto-detection**

Instead of counting levels manually, use the enhanced version:

```python
from utils.sysconfig import find_project_root

# This automatically finds your project root by looking for:
# - pyproject.toml
# - setup.py  
# - .git directory
# - requirements.txt
# etc.

find_project_root()  # No counting required!
```

This is much more reliable than manually counting directory levels!


Here's how to import and use the enhanced sysconfig utility in different scenarios:

## **1. Basic Import and Usage**

### Simple backward-compatible approach:
```python
# In any Python file in your project
from utils.sysconfig import add_project_root

# Add project root (goes up 3 levels by default)
add_project_root()

# Or specify custom levels
add_project_root(levels_up=2)

# Now you can import from your project root
from src.my_module import MyClass
from tests.helpers import test_helper
```

### Smart auto-detection (recommended):
```python
from utils.sysconfig import find_project_root

# Automatically finds project root using marker files
find_project_root()

# Now import anything from your project
from src.data_processing import DataLoader
from models.neural_net import NeuralNetwork
```

## **2. Advanced Usage with ProjectPathManager**

```python
from utils.sysconfig import ProjectPathManager

# Create a path manager instance
pm = ProjectPathManager()

# Method 1: Auto-detect project root
root = pm.find_project_root()
if root:
    print(f"Found project root at: {root}")

# Method 2: Manual levels
pm.add_project_root(levels_up=2)

# Method 3: Add custom paths
pm.add_custom_path("./vendor")
pm.add_custom_path("../shared_libraries")

# Now you can import from all added paths
from src.utils import helper_functions
from vendor.external_lib import ExternalTool

# See what paths were added
print("Added paths:", pm.list_added_paths())

# Clean up when done (optional)
pm.remove_added_paths()
```

## **3. Real-World Examples**

### Example 1: In a test file
```python
# File: tests/unit/test_data_processor.py
import sys
from pathlib import Path

# Add the project root so we can import our source code
from utils.sysconfig import find_project_root
find_project_root()

# Now we can import our source modules
from src.data_processing.processor import DataProcessor
from src.config import settings

def test_data_processor():
    processor = DataProcessor(settings.DATABASE_URL)
    # ... rest of test
```

### Example 2: In a Jupyter notebook
```python
# First cell in notebook
import sys
sys.path.append('..')  # Go up one level if needed

from utils.sysconfig import find_project_root
find_project_root()

# Now in other cells you can import from anywhere in your project
from src.models.ml_model import MLModel
from src.data.loaders import CSVLoader
```

### Example 3: In a script deep in the project
```python
# File: experiments/deep/nested/analysis_script.py
from utils.sysconfig import add_project_root

# Go up 4 levels to reach project root
add_project_root(levels_up=4)

# Now import from project root
from src.analysis.statistical_tests import chi_square_test
from data.processed.datasets import load_clean_data
```

## **4. Context Manager Pattern (Clean Usage)**

```python
from utils.sysconfig import ProjectPathManager

class ProjectContext:
    def __init__(self):
        self.pm = ProjectPathManager()
    
    def __enter__(self):
        self.pm.find_project_root()
        return self.pm
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pm.remove_added_paths()

# Usage
with ProjectContext() as pm:
    # Inside this block, project paths are available
    from src.models import MyModel
    from tests.fixtures import sample_data
    
    model = MyModel()
    # ... do work
# Outside this block, paths are cleaned up
```

## **5. Different Project Structures**

### Standard Python Project:
```
my_project/
├── pyproject.toml
├── src/
│   └── my_package/
├── tests/
└── utils/
    └── sysconfig.py
```

```python
# In tests/test_something.py
from utils.sysconfig import find_project_root
find_project_root()  # Finds pyproject.toml, adds my_project/ to path
from src.my_package import module
```

### Data Science Project:
```
research/
├── .git/
├── notebooks/
├── src/
├── data/
└── scripts/
    └── utils/
        └── sysconfig.py
```

```python
# In notebooks/analysis.ipynb
from scripts.utils.sysconfig import find_project_root
find_project_root()  # Finds .git/, adds research/ to path
from src.preprocessing import clean_data
```

## **6. Debugging and Troubleshooting**

```python
from utils.sysconfig import ProjectPathManager

pm = ProjectPathManager()

# See current sys.path
pm.print_sys_path()

# Add project root and see what happened
root = pm.find_project_root()
print(f"Project root: {root}")

# Check what paths were added
added_paths = pm.list_added_paths()
print("Added paths:", added_paths)

# Try importing and catch errors
try:
    from src.my_module import MyClass
    print("Import successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    print("Available paths:")
    pm.print_sys_path()
```

## **7. Common Patterns**

### At the start of main scripts:
```python
#!/usr/bin/env python3
"""Main script for data processing."""

# Set up project paths first
from utils.sysconfig import find_project_root
find_project_root()

# Now import project modules
from src.config import Config
from src.processors import DataProcessor

def main():
    config = Config()
    processor = DataProcessor(config)
    # ... rest of main logic

if __name__ == "__main__":
    main()
```

### In package __init__.py files:
```python
# src/__init__.py
from utils.sysconfig import find_project_root
find_project_root()

# This ensures the project root is available when anyone imports from src
```

The key is to call the path setup function **before** trying to import your project modules. Once the path is set up, you can import from anywhere in your project using absolute imports from the project root.

Here's an improved version of the utility with several enhancements and examples:The enhanced version includes several key improvements:

## **Key Enhancements:**

1. **Class-based approach** - `ProjectPathManager` for better state management
2. **Automatic project root detection** - Searches for common marker files like `pyproject.toml`, `.git`, `setup.py`
3. **Error handling** - Graceful handling of missing paths and invalid directories
4. **Path cleanup** - Ability to remove added paths (useful for testing)
5. **Custom path support** - Add arbitrary directories to the path
6. **Debugging utilities** - Print current sys.path and track added paths

## **Usage Examples:**

**Simple usage (backward compatible):**
```python
from utils.sysconfig import add_project_root
add_project_root(levels_up=2)
```

**Smart project root detection:**
```python
from utils.sysconfig import find_project_root
find_project_root()  # Automatically finds project root
```

**Advanced usage with cleanup:**
```python
pm = ProjectPathManager()
pm.find_project_root()
pm.add_custom_path("./vendor")
# ... do your imports ...
pm.remove_added_paths()  # Clean up when done
```

## **Benefits:**

- **More reliable** - Finds project root automatically instead of guessing levels
- **Better debugging** - Track what paths were added and clean up
- **Flexible** - Works with various project structures
- **Safe** - Handles errors gracefully
- **Maintainable** - Clear separation of concerns with the class approach

This approach is much more robust than the original fixed-level traversal and adapts to different project structures automatically.