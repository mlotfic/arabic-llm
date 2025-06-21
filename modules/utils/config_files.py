import os
from pathlib import Path
from typing import Union, Optional, Dict, Any, Callable
from hydra import initialize_config_dir, compose
from omegaconf import OmegaConf, ValidationError, DictConfig


def get_config_path(project_root, config_folder="./config"):
    """
    Get config path with flexible folder name.
    
    Args:
        project_root: Path to project root directory
        config_folder: Name of config folder (e.g., "config", "configs", "cfg")
    
    Returns:
        tuple: (absolute_path, relative_path) or None if not found
    """
    # Get the current script's directory and resolve the config path
    current_dir = Path.cwd()
    config_path = current_dir / config_folder
    config_path = Path(config_path).resolve()  # Convert to absolute path
    
    print(f"🔍 Looking for {config_folder} in: {current_dir}")
    
    # Check if config directory exists in current directory
    if config_path.exists():
        print(f"✅ {config_folder} directory found: {config_path}")
        return config_path, config_folder  # Return absolute path and relative path
    
    else:
        print(f"❌ {config_folder} not found locally ...")
        print(f"🔍 Checking project root for {config_folder} in: {project_root}")
        """approach using project root from ProjectPathManager"""
        # get project config path
        config_path = project_root / config_folder
        config_path = Path(config_path).resolve()  # Convert to absolute path
        
        # Check if config directory exists in project root
        if config_path.exists():
            print(f"✅ {config_folder} directory found: {config_path}")
            return config_path, os.path.relpath(str(config_path), str(current_dir))  # Return absolute and relative paths
        else:
            print(f"❌ {config_folder} directory not found in {project_root}")
            return None


def load_config_file(
    config_path: Union[str, Path], 
    config_file: str = "config.yaml",
    validation_func: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> Optional[Dict[str, Any]]:
    """
    Load configuration file with proper validation and error handling.
    
    Args:
        config_path: Path to config directory
        config_file: Name of config file (default: "config.yaml")
        validation_func: Optional validation function that takes config dict and returns bool
        
    Returns:
        Dict containing loaded configuration, or None if loading fails
    """
    # Basic input validation
    if not config_path:
        print("❌ config_path cannot be empty")
        return None
    
    if not config_file:
        print("❌ config_file cannot be empty")
        return None
    
    # Clean up config_file name
    config_file = config_file.lstrip("./")
    if not config_file.endswith(('.yaml', '.yml')):
        config_file += '.yaml'
    
    try:
        with initialize_config_dir(config_dir=str(config_path), version_base=None):
            # Remove extension for Hydra config_name
            config_name = config_file.replace('.yaml', '').replace('.yml', '')
            cfg = compose(config_name=config_name)
            
            print("\n✨ Loaded Hydra config:")
            print(f"Config length: {len(OmegaConf.to_yaml(cfg))} characters")
            
            # Convert to dict
            config_dict = OmegaConf.to_container(cfg, resolve=True)
            
            # Apply validation function if provided
            if validation_func:
                try:
                    # Pass config_dict as keyword arguments for Pydantic schema validation
                    return validation_func(**config_dict)
                except Exception as e:
                    print(f"\n🚫 Validation error: {e}")
                    return None            
            else:
                print("\n🚧 Skipping validation.")
                return config_dict
                
    except Exception as e:
        print(f"\n❌ Error loading config: {e}")
        return None


if __name__ == '__main__':
    try:
        # First: Setup project path to enable proper imports
        from utils.sysconfig import ProjectPathManager
        # from utils.config_files import get_config_path, load_config_file
        
        print("🔧 Initializing project path manager...")
        pm = ProjectPathManager()
        project_root = pm.auto_detect_and_add_root()  # Finds pyproject.toml automatically
        print(f"📁 Project root detected: {project_root}")

        
        # Now we can import project modules after path is set up
        from modules.schemas import SurahMappingSchema
        
        # Get config path for data_static folder
        print("\n🔍 Searching for config directory...")
        config_result = get_config_path(project_root, config_folder="./data_static")
        
        if config_result is None:
            print("❌ Config directory not found. Exiting.")
            exit(1)
            
        config_path, config_folder = config_result
        print(f"📂 Using config path: {config_path}")
        
        # Load and validate configuration file
        print("\n📄 Loading configuration file...")
        config_dict = load_config_file(
            config_path=config_path, 
            config_file="surah_mapping.yaml",
            validation_func=SurahMappingSchema
        )
        
        if config_dict is None:
            print("❌ Failed to load configuration. Exiting.")
            exit(1)
            
        # Load and validate configuration file
        print("\n📄 Loading configuration file...")
        config_dict = load_config_file(config_path=config_path, config_file="surah_mapping.yaml")
        
        if config_dict is None:
            print("❌ Failed to load configuration. Exiting.")
            exit(1)
        
        # Create validated Pydantic model instance
        print("\n✅ Creating validated config object...")
        validated_config = SurahMappingSchema(**config_dict)
        print("🎉 Successfully loaded and validated configuration!")
        print(f"📊 Config contains {len(config_dict)} top-level keys")
        
        # Optional: Print some basic info about the loaded config
        if hasattr(validated_config, 'surah_mapping'):
            print(f"📖 Surah mapping entries: {len(validated_config.surah_mapping)}")
            
    except Exception as e:
        print(f"💥 Unexpected error in main execution: {e}")
        import traceback
        traceback.print_exc()
        exit(1)