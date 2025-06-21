"""
Utils package initialization.
Contains utility classes and functions for the TurathLLM project.
"""

from .sysconfig import ProjectPathManager
from .config_files import get_config_path, load_config_file

__version__ = '0.1.0'
__all__ = ['ProjectPathManager']