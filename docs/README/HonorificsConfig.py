import hydra
from hydra import compose, initialize, initialize_config_store
from hydra.core.config_store import ConfigStore
from omegaconf import DictConfig, OmegaConf
from dataclasses import dataclass, field
from typing import List, Optional
import os

# ======================== CONFIGURATION DATACLASSES ========================

@dataclass
class HonorificsConfig:
    """Configuration for various types of honorifics"""
    before_honorifics: List[str] = field(default_factory=lambda: [
        "الشيخ", "الإمام", "الحافظ", "القاضي", "السيد", "العلامة",
        "الفقيه", "المحدث", "المجتهد", "المفسر", "الولي", "المقرئ"
    ])
    
    after_honorifics: List[str] = field(default_factory=lambda: [
        "صلى الله عليه وسلم",  # SAW - Prophet
        "عليه السلام",        # AS - Peace be upon him
        "رضي الله عنه",       # RA (male) - Companions
        "رضي الله عنها",      # RA (female) - Companions
        "رضي الله عنهم",      # RA (plural) - Companions
        "رحمه الله",          # RH (male) - Scholars
        "رحمها الله",         # RH (female) - Scholars
        "رحمهم الله",         # RH (plural) - Scholars
        "رحمة الله عليه",     # May Allah have mercy on him
        "رحمة الله عليها",    # May Allah have mercy on her
        "أجزل الله مثوبته",   # May Allah reward him abundantly
        "تقبله الله",         # May Allah accept him
        "غفر الله له",        # May Allah forgive him
        "عفا الله عنه",       # May Allah pardon him
        "تغمده الله برحمته",  # May Allah cover him with mercy
    ])
    
    prophet_honorifics: List[str] = field(default_factory=lambda: [
        "صلى الله عليه وسلم", "عليه الصلاة والسلام", "صلى الله عليه وسلم"
    ])
    
    companion_honorifics: List[str] = field(default_factory=lambda: [
        "رضي الله عنه", "رضي الله عنها", "رضي الله عنهم",
        "رضي الله عنهما", "رضوان الله عليه", "رضوان الله عليها"
    ])
    
    scholar_honorifics: List[str] = field(default_factory=lambda: [
        "رحمه الله", "رحمها الله", "رحمهم الله", "رحمة الله عليه",
        "رحمة الله عليها", "أجزل الله مثوبته", "تغمده الله برحمته",
        "عفا الله عنه", "غفر الله له"
    ])

@dataclass
class TitlesConfig:
    """Configuration for titles and references"""
    prophet_titles: List[str] = field(default_factory=lambda: [
        "النبي", "نبيه", "رسول الله", "الرسول", "خاتم النبيين",
        "سيد المرسلين", "الرسول الكريم", "النبي الكريم"
    ])
    
    allah_references: List[str] = field(default_factory=lambda: [
        "الله", "اللهم", "سبحانه وتعالى", "عز وجل", "تبارك وتعالى",
        "جل جلاله", "سبحانه", "المولى عز وجل"
    ])
    
    special_titles: List[str] = field(default_factory=lambda: [
        "النبي صلى الله عليه وسلم",
        "نبيه صلى الله عليه وسلم",
        "رسول الله صلى الله عليه وسلم",
        "الخليفة الراشد",
        "أمير المؤمنين",
        "رضي الله عن الصحابة أجمعين"
    ])

@dataclass
class LocationsConfig:
    """Configuration for locations and places"""
    cities: List[str] = field(default_factory=lambda: [
        "المدينة", "مكة", "البصرة", "الكوفة", "بغداد", "دمشق",
        "القاهرة", "الفسطاط", "واسط", "الري", "نيسابور", "هراة"
    ])

@dataclass
class NamesConfig:
    """Configuration for common names"""
    common_names: List[str] = field(default_factory=lambda: [
        "محمد", "أحمد", "علي", "حسن", "حسين", "عمر", "عثمان",
        "أبو", "عبد", "عبدالله", "عبدالرحمن", "إبراهيم", "يوسف"
    ])

@dataclass
class ArabicNERConfig:
    """Main configuration class for Arabic NER patterns and honorifics"""
    honorifics: HonorificsConfig = field(default_factory=HonorificsConfig)
    titles: TitlesConfig = field(default_factory=TitlesConfig)
    locations: LocationsConfig = field(default_factory=LocationsConfig)
    names: NamesConfig = field(default_factory=NamesConfig)
    
    # Model parameters
    model_name: str = "arabic-ner-model"
    max_sequence_length: int = 512
    batch_size: int = 32
    learning_rate: float = 2e-5
    
    # Processing parameters
    case_sensitive: bool = True
    remove_diacritics: bool = False
    normalize_text: bool = True

# ======================== HYDRA INTEGRATION CLASS ========================

class HydraArabicNERConfig:
    """Hydra-powered Arabic NER Configuration Manager"""
    
    def __init__(self, config_path: str = "conf", config_name: str = "config"):
        """
        Initialize Hydra configuration
        
        Args:
            config_path (str): Path to configuration directory
            config_name (str): Name of the main config file (without .yaml)
        """
        self.config_path = config_path
        self.config_name = config_name
        self._config = None
        self._setup_config_store()
    
    def _setup_config_store(self):
        """Register structured configs with Hydra's ConfigStore"""
        cs = ConfigStore.instance()
        cs.store(name="base_config", node=ArabicNERConfig)
        cs.store(group="honorifics", name="default", node=HonorificsConfig)
        cs.store(group="titles", name="default", node=TitlesConfig)
        cs.store(group="locations", name="default", node=LocationsConfig)
        cs.store(group="names", name="default", node=NamesConfig)
    
    def load_config(self, overrides: Optional[List[str]] = None) -> DictConfig:
        """
        Load configuration using Hydra
        
        Args:
            overrides (List[str], optional): Configuration overrides
            
        Returns:
            DictConfig: Loaded configuration
        """
        if overrides is None:
            overrides = []
            
        with initialize(version_base=None, config_path=self.config_path):
            cfg = compose(config_name=self.config_name, overrides=overrides)
            self._config = cfg
            return cfg
    
    def load_config_from_file(self, config_file: str, overrides: Optional[List[str]] = None) -> DictConfig:
        """
        Load configuration from specific file
        
        Args:
            config_file (str): Path to config file
            overrides (List[str], optional): Configuration overrides
            
        Returns:
            DictConfig: Loaded configuration
        """
        if overrides is None:
            overrides = []
            
        config_dir = os.path.dirname(config_file)
        config_name = os.path.basename(config_file).replace('.yaml', '')
        
        with initialize(version_base=None, config_path=config_dir):
            cfg = compose(config_name=config_name, overrides=overrides)
            self._config = cfg
            return cfg
    
    @property
    def config(self) -> DictConfig:
        """Get current configuration"""
        if self._config is None:
            return self.load_config()
        return self._config
    
    def get_honorifics(self) -> List[str]:
        """Get all honorifics combined"""
        cfg = self.config
        all_honorifics = []
        all_honorifics.extend(cfg.honorifics.before_honorifics)
        all_honorifics.extend(cfg.honorifics.after_honorifics)
        all_honorifics.extend(cfg.honorifics.prophet_honorifics)
        all_honorifics.extend(cfg.honorifics.companion_honorifics)
        all_honorifics.extend(cfg.honorifics.scholar_honorifics)
        return all_honorifics
    
    def get_all_patterns(self) -> dict:
        """Get all patterns as dictionary"""
        cfg = self.config
        return {
            'before_honorifics': cfg.honorifics.before_honorifics,
            'after_honorifics': cfg.honorifics.after_honorifics,
            'prophet_titles': cfg.titles.prophet_titles,
            'prophet_honorifics': cfg.honorifics.prophet_honorifics,
            'companion_honorifics': cfg.honorifics.companion_honorifics,
            'scholar_honorifics': cfg.honorifics.scholar_honorifics,
            'allah_references': cfg.titles.allah_references,
            'cities': cfg.locations.cities,
            'common_names': cfg.names.common_names,
            'special_titles': cfg.titles.special_titles
        }
    
    def print_config(self):
        """Print current configuration in a readable format"""
        print(OmegaConf.to_yaml(self.config))
    
    def save_config(self, output_path: str):
        """Save current configuration to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            OmegaConf.save(config=self.config, f=f)
    
    def get_config_summary(self) -> dict:
        """Get summary of configuration with counts"""
        cfg = self.config
        return {
            'before_honorifics': len(cfg.honorifics.before_honorifics),
            'after_honorifics': len(cfg.honorifics.after_honorifics),
            'prophet_titles': len(cfg.titles.prophet_titles),
            'prophet_honorifics': len(cfg.honorifics.prophet_honorifics),
            'companion_honorifics': len(cfg.honorifics.companion_honorifics),
            'scholar_honorifics': len(cfg.honorifics.scholar_honorifics),
            'allah_references': len(cfg.titles.allah_references),
            'cities': len(cfg.locations.cities),
            'common_names': len(cfg.names.common_names),
            'special_titles': len(cfg.titles.special_titles),
            'model_parameters': {
                'model_name': cfg.model_name,
                'max_sequence_length': cfg.max_sequence_length,
                'batch_size': cfg.batch_size,
                'learning_rate': cfg.learning_rate
            }
        }

# ======================== HYDRA APP DECORATOR EXAMPLE ========================

@hydra.main(version_base=None, config_path="conf", config_name="config")
def run_arabic_ner(cfg: DictConfig) -> None:
    """
    Example Hydra app for Arabic NER
    
    Args:
        cfg (DictConfig): Hydra configuration
    """
    print("=== Arabic NER Configuration ===")
    print(f"Model: {cfg.model_name}")
    print(f"Batch size: {cfg.batch_size}")
    print(f"Learning rate: {cfg.learning_rate}")
    
    print(f"\nBefore honorifics count: {len(cfg.honorifics.before_honorifics)}")
    print(f"Cities count: {len(cfg.locations.cities)}")
    
    # Example: Access specific configuration
    print(f"\nFirst 3 prophet titles: {cfg.titles.prophet_titles[:3]}")
    print(f"First 3 cities: {cfg.locations.cities[:3]}")

# ======================== USAGE EXAMPLES ========================

if __name__ == "__main__":
    # Example 1: Using HydraArabicNERConfig class
    print("=== Using HydraArabicNERConfig Class ===")
    
    # Initialize config manager
    config_manager = HydraArabicNERConfig()
    
    # Load default configuration
    cfg = config_manager.load_config()
    
    # Print configuration summary
    print("Configuration Summary:")
    summary = config_manager.get_config_summary()
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Example 2: Load with overrides
    print("\n=== Using Configuration Overrides ===")
    overrides = [
        "batch_size=64",
        "learning_rate=1e-4",
        "model_name=custom-arabic-ner"
    ]
    
    cfg_override = config_manager.load_config(overrides=overrides)
    print(f"Override - Model: {cfg_override.model_name}")
    print(f"Override - Batch size: {cfg_override.batch_size}")
    print(f"Override - Learning rate: {cfg_override.learning_rate}")
    
    # Example 3: Get all honorifics
    print(f"\nTotal honorifics count: {len(config_manager.get_honorifics())}")
    
    # Example 4: Save configuration
    print("\n=== Saving Configuration ===")
    try:
        config_manager.save_config("output_config.yaml")
        print("Configuration saved to output_config.yaml")
    except Exception as e:
        print(f"Error saving config: {e}")
    
    # Note: To run the Hydra app, uncomment the following line:
    # run_arabic_ner()