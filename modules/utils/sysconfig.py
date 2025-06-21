import sys
import os
from pathlib import Path
from typing import Optional, List, Union, Tuple


class ProjectPathManager:
    """Enhanced project path management utility."""
    
    def __init__(self):
        self._added_paths = []
        self._project_root = None
        self._current_file_level = None
    
    def add_project_root(self, levels_up: int = 3) -> Optional[Path]:
        """
        Add project root to sys.path by going up a specified number of levels.
        
        Args:
            levels_up: Number of parent directories to traverse
            
        Returns:
            Path object of the added root, or None if failed
            
        Example:
            >>> pm = ProjectPathManager()
            >>> root = pm.add_project_root(levels_up=2)
            >>> print(f"Added root: {root}")
        """
        try:
            root = Path(__file__).resolve().parents[levels_up]
            self._project_root = root
            self._current_file_level = levels_up
            return self._add_path_to_sys(root)
        except (IndexError, OSError) as e:
            print(f"Warning: Could not add project root {levels_up} levels up: {e}")
            return None
    
    def find_project_root(self, markers: List[str] = None) -> Optional[Path]:
        """
        Find project root by looking for marker files/directories.
        
        Args:
            markers: List of files/dirs that indicate project root
            
        Returns:
            Path to project root or None if not found
            
        Example:
            >>> pm = ProjectPathManager()
            >>> root = pm.find_project_root(['pyproject.toml', '.git', 'setup.py'])
            >>> if root:
            ...     print(f"Project root found at: {root}")
        """
        if markers is None:
            markers = [
                'pyproject.toml', 'setup.py', 'setup.cfg', 
                '.git', '.gitignore', 'requirements.txt',
                'Pipfile', 'poetry.lock', 'Cargo.toml',
                'package.json', 'Makefile'
            ]
        
        current = Path(__file__).resolve()
        
        # Check current directory and parents
        for level, parent in enumerate([current.parent] + list(current.parents)):
            for marker in markers:
                if (parent / marker).exists():
                    self._project_root = parent
                    self._current_file_level = level
                    return self._add_path_to_sys(parent)
        
        print(f"Warning: Project root not found using markers: {markers}")
        return None
    
    def get_current_file_level_from_root(self) -> Optional[int]:
        """
        Get the current file's level/depth from the project root.
        
        Returns:
            Number of levels the current file is from project root, or None if root not set
            
        Example:
            >>> pm = ProjectPathManager()
            >>> pm.find_project_root()
            >>> level = pm.get_current_file_level_from_root()
            >>> print(f"Current file is {level} levels deep from project root")
        """
        if self._current_file_level is not None:
            return self._current_file_level
        
        # If root was not set through add_project_root or find_project_root,
        # try to calculate it now
        if self._project_root is None:
            print("Warning: Project root not set. Use add_project_root() or find_project_root() first.")
            return None
        
        # Calculate level based on current file and known project root
        try:
            current_file = Path(__file__).resolve()
            relative_path = current_file.relative_to(self._project_root)
            # Number of parent directories = number of path parts - 1 (for the file itself)
            level = len(relative_path.parts) - 1
            self._current_file_level = level
            return level
        except ValueError:
            print("Warning: Current file is not within the project root.")
            return None
    
    def get_project_root(self) -> Optional[Path]:
        """
        Get the currently set project root path.
        
        Returns:
            Path to project root or None if not set
            
        Example:
            >>> pm = ProjectPathManager()
            >>> pm.find_project_root()
            >>> root = pm.get_project_root()
            >>> print(f"Project root: {root}")
        """
        return self._project_root
    
    def get_file_info(self) -> Tuple[Optional[Path], Optional[Path], Optional[int]]:
        """
        Get comprehensive information about the current file's position.
        
        Returns:
            Tuple of (current_file_path, project_root_path, levels_from_root)
            
        Example:
            >>> pm = ProjectPathManager()
            >>> pm.find_project_root()
            >>> file_path, root_path, level = pm.get_file_info()
            >>> print(f"File: {file_path}")
            >>> print(f"Root: {root_path}")
            >>> print(f"Level: {level}")
        """
        current_file = Path(__file__).resolve()
        project_root = self.get_project_root()
        level = self.get_current_file_level_from_root()
        
        return current_file, project_root, level
    
    def calculate_levels_to_reach(self, target_path: Union[str, Path]) -> Optional[int]:
        """
        Calculate how many levels up are needed to reach a target directory.
        
        Args:
            target_path: Path to the target directory
            
        Returns:
            Number of levels needed, or None if target is not a parent
            
        Example:
            >>> pm = ProjectPathManager()
            >>> levels = pm.calculate_levels_to_reach("/path/to/project/root")
            >>> if levels is not None:
            ...     pm.add_project_root(levels_up=levels)
        """
        try:
            current_file = Path(__file__).resolve()
            target = Path(target_path).resolve()
            
            # Check if target is a parent of current file
            try:
                relative = current_file.relative_to(target)
                # Number of parent directories in the relative path
                return len(relative.parts) - 1
            except ValueError:
                print(f"Warning: {target} is not a parent directory of current file")
                return None
                
        except (OSError, ValueError) as e:
            print(f"Error calculating levels to {target_path}: {e}")
            return None
    
    def auto_detect_and_add_root(self, max_levels: int = 10) -> Optional[Path]:
        """
        Automatically detect and add project root using multiple strategies.
        
        Args:
            max_levels: Maximum number of parent levels to check
            
        Returns:
            Path to detected project root or None if not found
            
        Example:
            >>> pm = ProjectPathManager()
            >>> root = pm.auto_detect_and_add_root()
            >>> if root:
            ...     print(f"Auto-detected root: {root}")
        """
        # Strategy 1: Try to find by markers first
        root = self.find_project_root()
        if root:
            return root
        
        # Strategy 2: Look for common project structures by going up levels
        common_markers = [
            ['src', 'tests'],  # Common Python project structure
            ['lib', 'bin'],    # Common library structure  
            ['app', 'config'], # Common application structure
            ['.vscode', '.idea'], # IDE project folders
        ]
        
        current = Path(__file__).resolve()
        
        for level in range(1, max_levels + 1):
            try:
                candidate_root = current.parents[level - 1]
                
                # Check if this level contains multiple marker combinations
                for marker_set in common_markers:
                    if all((candidate_root / marker).exists() for marker in marker_set):
                        self._project_root = candidate_root
                        self._current_file_level = level
                        return self._add_path_to_sys(candidate_root)
                        
            except IndexError:
                break
        
        print(f"Warning: Could not auto-detect project root within {max_levels} levels")
        return None
    
    def add_custom_path(self, path: Union[str, Path]) -> Optional[Path]:
        """
        Add a custom path to sys.path.
        
        Args:
            path: Path to add (string or Path object)
            
        Returns:
            Path object if successful, None otherwise
            
        Example:
            >>> pm = ProjectPathManager()
            >>> pm.add_custom_path("/path/to/custom/modules")
        """
        try:
            path_obj = Path(path).resolve()
            if not path_obj.exists():
                print(f"Warning: Path does not exist: {path_obj}")
                return None
            return self._add_path_to_sys(path_obj)
        except (OSError, ValueError) as e:
            print(f"Error adding custom path {path}: {e}")
            return None
    
    def _add_path_to_sys(self, path: Path) -> Path:
        """Internal method to add path to sys.path if not already present."""
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
            self._added_paths.append(path)
            print(f"Added to sys.path: {path}")
        return path
    
    def remove_added_paths(self):
        """Remove all paths that were added by this manager."""
        for path in self._added_paths:
            path_str = str(path)
            if path_str in sys.path:
                sys.path.remove(path_str)
                print(f"Removed from sys.path: {path}")
        self._added_paths.clear()
        # Reset internal state
        self._project_root = None
        self._current_file_level = None
    
    def list_added_paths(self) -> List[Path]:
        """Return list of paths added by this manager."""
        return self._added_paths.copy()
    
    def print_sys_path(self):
        """Print current sys.path for debugging."""
        print("Current sys.path:")
        for i, path in enumerate(sys.path):
            marker = " <-- Added by ProjectPathManager" if Path(path) in self._added_paths else ""
            print(f"  {i}: {path}{marker}")
    
    def print_project_info(self):
        """Print comprehensive project path information."""
        print("=== Project Path Information ===")
        
        current_file, project_root, level = self.get_file_info()
        
        print(f"Current file: {current_file}")
        print(f"Project root: {project_root}")
        print(f"File level from root: {level}")
        
        if project_root and current_file:
            try:
                relative_path = current_file.relative_to(project_root)
                print(f"Relative path: {relative_path}")
            except ValueError:
                print("Relative path: File is outside project root")
        
        print(f"Added paths count: {len(self._added_paths)}")
        if self._added_paths:
            print("Added paths:")
            for path in self._added_paths:
                print(f"  - {path}")


# Convenience functions for backward compatibility and simple usage
def add_project_root(levels_up: int = 3) -> Optional[Path]:
    """Simple function to add project root (backward compatible)."""
    manager = ProjectPathManager()
    return manager.add_project_root(levels_up)


def find_project_root(markers: List[str] = None) -> Optional[Path]:
    """Simple function to find and add project root by markers."""
    manager = ProjectPathManager()
    return manager.find_project_root(markers)


def get_current_file_level() -> Optional[int]:
    """Simple function to get current file level from auto-detected root."""
    manager = ProjectPathManager()
    root = manager.find_project_root()
    if root:
        return manager.get_current_file_level_from_root()
    return None


# Example usage and demonstrations
if __name__ == "__main__":
    print("=== ProjectPathManager Enhanced Examples ===\n")
    
    # Example 1: Basic usage with level detection
    print("1. Adding project root and checking file level:")
    pm = ProjectPathManager()
    root = pm.add_project_root(levels_up=2)
    if root:
        level = pm.get_current_file_level_from_root()
        print(f"   Current file is {level} levels deep from root")
    
    # Example 2: Finding root by markers and getting info
    print("\n2. Finding project root by markers and getting comprehensive info:")
    pm2 = ProjectPathManager()
    root2 = pm2.find_project_root(['pyproject.toml', '.git', 'setup.py'])
    if root2:
        pm2.print_project_info()
    
    # Example 3: Auto-detection
    print("\n3. Auto-detecting project root:")
    pm3 = ProjectPathManager()
    root3 = pm3.auto_detect_and_add_root()
    if root3:
        file_path, root_path, level = pm3.get_file_info()
        print(f"   Auto-detected root: {root_path}")
        print(f"   File level: {level}")
    
    # Example 4: Calculate levels to specific target
    print("\n4. Calculating levels to reach specific paths:")
    pm4 = ProjectPathManager()
    
    # Example targets (these would be real paths in practice)
    example_targets = ["../", "../../", "../../../"]
    
    for target in example_targets:
        levels = pm4.calculate_levels_to_reach(target)
        if levels is not None:
            print(f"   Levels to reach {target}: {levels}")
    
    # Example 5: Working with file information
    print("\n5. Comprehensive file information:")
    pm5 = ProjectPathManager()
    pm5.find_project_root()
    
    current_file, project_root, level = pm5.get_file_info()
    if all([current_file, project_root, level is not None]):
        print(f"   File: {current_file.name}")
        print(f"   Root: {project_root.name}")
        print(f"   Depth: {level} levels")
        
        # Show directory structure
        if level > 0:
            path_parts = current_file.relative_to(project_root).parts[:-1]  # Exclude filename
            print(f"   Directory path: {' → '.join(path_parts)}")
    
    # Example 6: Dynamic level calculation
    print("\n6. Dynamic level calculation example:")
    pm6 = ProjectPathManager()
    
    # Simulate finding root at different levels
    for test_level in range(1, 4):
        try:
            test_root = Path(__file__).resolve().parents[test_level]
            if test_root.exists():
                levels_needed = pm6.calculate_levels_to_reach(test_root)
                print(f"   To reach {test_root.name}: need {levels_needed} levels")
        except IndexError:
            break
    
    # Cleanup
    print("\n7. Cleaning up:")
    for pm in [pm, pm2, pm3, pm4, pm5, pm6]:
        pm.remove_added_paths()
    
    print("\n=== Usage Patterns ===")
    
    # Pattern 1: Smart initialization
    print("\n8. Smart initialization pattern:")
    
    def smart_init_project():
        """Smart way to initialize project paths."""
        pm = ProjectPathManager()
        
        # Try auto-detection first
        root = pm.auto_detect_and_add_root()
        if not root:
            # Fallback to manual detection
            root = pm.find_project_root()
        if not root:
            # Last resort - go up a few levels
            root = pm.add_project_root(levels_up=3)
        
        if root:
            level = pm.get_current_file_level_from_root()
            print(f"  ✓ Initialized project root: {root.name} (level {level})")
            return pm
        else:
            print("  ✗ Could not initialize project root")
            return None
    
    project_manager = smart_init_project()
    if project_manager:
        project_manager.remove_added_paths()


# Extended example project structures this utility handles:

"""
Example Project Structure 3 - Deep Nested Structure:
complex_project/
├── .git/                           # Root marker
├── src/
│   ├── main/
│   │   ├── python/
│   │   │   ├── app/
│   │   │   │   └── core/
│   │   │   │       └── utils/
│   │   │   │           └── sysconfig.py  # Level 6 from root
│   │   │   └── lib/
│   │   └── resources/
│   └── test/
│       └── python/
│           └── integration/
│               └── deep/
│                   └── test_utils.py     # Level 5 from root
├── docs/
└── build/

Usage in sysconfig.py:
    pm = ProjectPathManager()
    pm.find_project_root()  # Finds .git automatically
    level = pm.get_current_file_level_from_root()  # Returns 6
    print(f"I'm {level} levels deep!")

Usage in test_utils.py:
    pm = ProjectPathManager()
    pm.auto_detect_and_add_root()
    current, root, level = pm.get_file_info()
    # level = 5, can now import from src/main/python/
    
Example Project Structure 4 - Multi-language Project:
polyglot_project/
├── package.json                    # Node.js marker
├── pyproject.toml                  # Python marker
├── Cargo.toml                      # Rust marker
├── frontend/
│   ├── src/
│   └── utils/
│       └── path_helper.py          # Level 2 from root
├── backend/
│   ├── python/
│   │   └── services/
│   │       └── deep/
│   │           └── worker.py       # Level 4 from root
│   └── rust/
│       └── src/
└── shared/
    └── config/
        └── settings.py             # Level 2 from root

Usage patterns:
    # Auto-detection works great for multi-language projects
    pm = ProjectPathManager()
    pm.auto_detect_and_add_root()  # Finds multiple markers
    
    # Calculate relative imports dynamically
    level = pm.get_current_file_level_from_root()
    if level >= 2:
        # Can safely import from shared modules
        pass
"""