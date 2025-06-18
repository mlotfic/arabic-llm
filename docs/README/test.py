from utils.sysconfig import add_project_root, ProjectPathManager
add_project_root()

# 
from external_modules.some_tool import my_function


print("=== ProjectPathManager Examples ===\n")


pm = ProjectPathManager()

# Example 2: Finding root by markers
print("\n2. Finding project root by markers:")
project_root = pm.find_project_root(['pyproject.toml', '.git', 'setup.py'])

# Example 4: Show current state
print("\n4. Current added paths:")
added_paths = pm.list_added_paths()
for path in added_paths:
    print(f"  - {path}")


# Example 1: Basic usage with levels
print("1. Adding project root by going up 2 levels:")
root1 = pm.add_project_root(levels_up=2)



# Example 3: Adding custom paths
print("\n3. Adding custom paths:")
pm.add_custom_path("./src")
pm.add_custom_path("./tests")


# Example 5: Print full sys.path
print("\n5. Full sys.path (first 5 entries):")
pm.print_sys_path()

# Example 6: Cleanup
print("\n6. Cleaning up added paths:")
pm.remove_added_paths()

print("\n=== Advanced Usage Examples ===")

# Example 7: Context manager style usage
print("\n7. Context manager pattern:")
class PathContextManager:
    def __init__(self, levels_up=3):
        self.pm = ProjectPathManager()
        self.levels_up = levels_up
        
    def __enter__(self):
        self.pm.add_project_root(self.levels_up)
        return self.pm
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pm.remove_added_paths()

with PathContextManager(levels_up=2) as pm:
    print("  Inside context: paths added")
    # Your imports would go here
    # from src.module import something
print("  Outside context: paths cleaned up")

# Example 8: Multiple project roots
print("\n8. Managing multiple project roots:")
pm_multi = ProjectPathManager()

# Add different roots for different purposes
pm_multi.add_project_root(levels_up=1)  # Current project
pm_multi.add_custom_path("../shared_modules")  # Shared code
pm_multi.add_custom_path("./vendor")  # Third-party code

print("  Multiple roots added:")
for path in pm_multi.list_added_paths():
    print(f"    - {path}")

pm_multi.remove_added_paths()




from utils.paths import resolve_path

data_path = resolve_path('data', 'raw.csv')


from utils.load_config import load_config
config = load_config()
print(config['db']['host'])


import yaml
from pathlib import Path

def load_yaml(name, folder='config'):
    path = Path(__file__).resolve().parents[1] / folder / name
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

grading = load_yaml('grading_keywords.yaml')
print(grading['authenticity']['sahih']['keywords'])

# run.py or script/temp.py
from utils.config_loader import load_config

config = load_config('default.yaml', 'dev.yaml')
print("Log directory:", config['paths']['log_dir'])
'''
🧪 Bonus: Auto-load via ENV
Update loader:

python
import os
# utils/config_loader.py
override_file = os.getenv("CONFIG_ENV", "dev.yaml")


Now you can control it like:

bash
# Set environment variable before running
CONFIG_ENV=prod.yaml python run.py

echo "config/secrets.yaml" >> .gitignore
echo "config/local.yaml" >> .gitignore


'''

config = load_config('default.yaml', 'dev.yaml')
keywords = load_yaml_file(Path('config/hadith/grading_keywords.yaml'))

from pydantic import BaseModel
from pathlib import Path
import yaml

class Paths(BaseModel):
    input_dir: str
    log_dir: str

class AppConfig(BaseModel):
    name: str
    version: str

class Settings(BaseModel):
    app: AppConfig
    paths: Paths

def load_config(path='config/settings.yaml') -> Settings:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return Settings(**data)

config = load_config()
print(config.paths.input_dir)  # autocompletion!


import os

# 🔹 1. Project Root from Any File
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 🔹 2. Get Path to a File in a Sibling Folder
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw.csv')

# 🔹 3. Canonical Path to Current Script
HERE = os.path.abspath(os.path.dirname(__file__))


# 🔹 4. Universal Root Path Resolver (One-liner function)
get_root = lambda level=1: os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * level)))
ROOT = get_root(2)  # Go up 2 levels

# 🔹 5. Safe Add to sys.path if Not Already
import sys; sys.path.insert(0, ROOT) if ROOT not in sys.path else None
# ➡️ Prevents duplicate pollution.


# 🔹 6. Cross-platform File Resolver
from pathlib import Path
DATA_FILE = Path(__file__).resolve().parent.parent / 'data' / 'raw.csv'
# ➡️ Cleaner than os.path.join, works across platforms, supports chaining.



# 🔹 7. Current Working Directory (CWD) Safe Resolver
FILE_FROM_CWD = os.path.abspath(os.path.join(os.getcwd(), 'data', 'file.csv'))
# ➡️ Use only if you want the path relative to where the script is executed, not where it lives.


# main.py
from models import load_grading_config

config = load_grading_config()
print(config.authenticity.__root__['sahih'].keywords)
print(config.isnaad_status.__root__['munqati'].score)


from pydantic import root_validator

class GradingKeywords(BaseModel):
    authenticity: GradingCategory
    isnaad_status: GradingCategory
    maten_defects: GradingCategory


class GradingItem(BaseModel):
    score: int
    keywords: List[str]

    @root_validator
    def check_keywords(cls, values):
        if not values['keywords']:
            raise ValueError("Each grading must have at least one keyword.")
        return values
