#!/usr/bin/env python3
"""
Dependency Scanner - Analyzes your project to find actual dependencies
"""
import ast
import os
import sys
from pathlib import Path
from collections import defaultdict
import subprocess
import pkg_resources

def get_installed_packages():
    """Get currently installed packages with versions"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True)
        packages = {}
        for line in result.stdout.strip().split('\n'):
            if '==' in line:
                name, version = line.split('==')
                packages[name.lower()] = version
        return packages
    except:
        return {}

def is_standard_library(module_name):
    """Check if a module is part of Python's standard library"""
    stdlib_modules = {
        'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 'collections',
        'itertools', 'functools', 'operator', 'copy', 'pickle', 're', 'math',
        'random', 'time', 'urllib', 'http', 'email', 'html', 'xml', 'csv',
        'configparser', 'argparse', 'logging', 'unittest', 'threading',
        'multiprocessing', 'subprocess', 'shutil', 'glob', 'fnmatch',
        'tempfile', 'gzip', 'zipfile', 'tarfile', 'sqlite3', 'socket',
        'ssl', 'hashlib', 'hmac', 'secrets', 'uuid', 'base64', 'binascii',
        'struct', 'codecs', 'locale', 'gettext', 'calendar', 'collections',
        'heapq', 'bisect', 'array', 'weakref', 'types', 'io', 'warnings',
        'contextlib', 'abc', 'numbers', 'decimal', 'fractions', 'statistics',
        'enum', 'dataclasses', 'asyncio', 'concurrent', 'queue'
    }
    return module_name in stdlib_modules

def analyze_file(filepath):
    """Analyze a Python file for imports"""
    imports = set()
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if not is_standard_library(module):
                        imports.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if not is_standard_library(module):
                        imports.add(module)
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
    
    return imports

def scan_project(root_dir='.'):
    """Scan entire project for dependencies"""
    all_imports = set()
    file_imports = defaultdict(set)
    
    # Scan all Python files
    for py_file in Path(root_dir).rglob("*.py"):
        # Skip external modules and virtual environments
        if any(skip in str(py_file) for skip in ['external_modules', 'venv', '.venv', '__pycache__']):
            continue
            
        imports = analyze_file(py_file)
        all_imports.update(imports)
        if imports:
            file_imports[str(py_file)] = imports
    
    return all_imports, file_imports

def map_import_to_package(import_name):
    """Map import names to actual package names"""
    # Common mappings
    mapping = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'sklearn': 'scikit-learn',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'dateutil': 'python-dateutil',
        'pkg_resources': 'setuptools',
        'jwt': 'PyJWT',
        'bs4': 'beautifulsoup4',
        'requests_oauthlib': 'requests-oauthlib',
        'openai': 'openai',
        'anthropic': 'anthropic',
    }
    
    return mapping.get(import_name, import_name)

def get_package_version(package_name, installed_packages):
    """Get version of installed package"""
    package_lower = package_name.lower()
    
    # Try exact match first
    if package_lower in installed_packages:
        return installed_packages[package_lower]
    
    # Try alternative names
    alternatives = [
        package_name.replace('-', '_'),
        package_name.replace('_', '-'),
        package_name.lower().replace('-', '_'),
        package_name.lower().replace('_', '-')
    ]
    
    for alt in alternatives:
        if alt in installed_packages:
            return installed_packages[alt]
    
    return "unknown"

def main():
    print("🔍 Scanning your project for dependencies...\n")
    
    # Get installed packages
    installed_packages = get_installed_packages()
    
    # Scan project
    all_imports, file_imports = scan_project()
    
    # Map to package names and get versions
    dependencies = {}
    for import_name in sorted(all_imports):
        package_name = map_import_to_package(import_name)
        version = get_package_version(package_name, installed_packages)
        dependencies[package_name] = version
    
    # Print results
    print("📦 DISCOVERED DEPENDENCIES:")
    print("=" * 50)
    
    for package, version in sorted(dependencies.items()):
        if version != "unknown":
            print(f"{package}>={version}")
        else:
            print(f"{package}  # Version unknown - not installed")
    
    print(f"\n📊 SUMMARY:")
    print(f"   • Found {len(dependencies)} third-party dependencies")
    print(f"   • Scanned {len(file_imports)} Python files")
    
    # Print file-by-file breakdown
    print(f"\n📁 DEPENDENCIES BY FILE:")
    print("=" * 50)
    
    for filepath, imports in sorted(file_imports.items()):
        print(f"\n{filepath}:")
        for imp in sorted(imports):
            package = map_import_to_package(imp)
            version = get_package_version(package, installed_packages)
            status = f"({version})" if version != "unknown" else "(not installed)"
            print(f"  • {package} {status}")
    
    # Generate requirements.txt
    print(f"\n📝 GENERATING requirements.txt...")
    requirements = []
    for package, version in sorted(dependencies.items()):
        if version != "unknown":
            requirements.append(f"{package}>={version}")
        else:
            requirements.append(f"# {package}  # Version unknown")
    
    with open("requirements-discovered.txt", "w") as f:
        f.write("# Auto-generated requirements from project scan\n")
        f.write("# Generated by dependency scanner\n\n")
        f.write("\n".join(requirements))
    
    print(f"✅ Saved to: requirements-discovered.txt")
    
    # Categorize dependencies
    print(f"\n🏷️  DEPENDENCY CATEGORIES:")
    print("=" * 50)
    
    categories = {
        'Web Framework': ['fastapi', 'uvicorn', 'starlette', 'django', 'flask'],
        'Data Science': ['pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn'],
        'Machine Learning': ['torch', 'tensorflow', 'transformers', 'scikit-learn', 'xgboost'],
        'Database': ['sqlalchemy', 'pymongo', 'psycopg2', 'mysql-connector-python'],
        'Configuration': ['pydantic', 'pyyaml', 'python-dotenv', 'configparser'],
        'CLI/UI': ['typer', 'click', 'rich', 'colorama'],
        'HTTP/API': ['requests', 'httpx', 'aiohttp'],
        'Testing': ['pytest', 'unittest', 'mock'],
        'Utilities': ['loguru', 'python-dateutil', 'pathlib', 'typing-extensions']
    }
    
    for category, packages in categories.items():
        found = [pkg for pkg in packages if pkg in dependencies]
        if found:
            print(f"\n{category}:")
            for pkg in found:
                version = dependencies[pkg]
                print(f"  • {pkg} {version if version != 'unknown' else ''}")

if __name__ == "__main__":
    main()