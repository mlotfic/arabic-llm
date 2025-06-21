"""
Arabic Text Normalization Configuration with Hydra and Pydantic
Loads YAML configuration and validates it using Pydantic models.
"""

import re
import logging
from typing import Dict, List, Optional
from pathlib import Path

import hydra
from hydra import compose, initialize
from omegaconf import DictConfig, OmegaConf
from pydantic import BaseModel, Field, validator


class ProcessingConfig(BaseModel):
    """Processing options configuration"""
    normalize_whitespace: bool = True
    strip_whitespace: bool = True
    case_sensitive: bool = True


class ArabicNormalizationConfig(BaseModel):
    """Main configuration model for Arabic text normalization"""
    
    # Pipeline execution order
    pipeline_order: List[str] = Field(..., description="Order of normalization steps")
    
    # Character mappings
    persian_to_arabic: Dict[str, str] = Field(default_factory=dict)
    urdu_to_arabic: Dict[str, str] = Field(default_factory=dict)
    pashto_to_arabic: Dict[str, str] = Field(default_factory=dict)
    kurdish_to_arabic: Dict[str, str] = Field(default_factory=dict)
    uyghur_to_arabic: Dict[str, str] = Field(default_factory=dict)
    sindhi_to_arabic: Dict[str, str] = Field(default_factory=dict)
    malay_to_arabic: Dict[str, str] = Field(default_factory=dict)
    arabic_variants: Dict[str, str] = Field(default_factory=dict)
    other_safe_to_arabic: Dict[str, str] = Field(default_factory=dict)
    punctuation_normalization: Dict[str, str] = Field(default_factory=dict)
    numbers_normalization: Dict[str, str] = Field(default_factory=dict)
    diacritics: Dict[str, str] = Field(default_factory=dict)
    quranic_marks: Dict[str, str] = Field(default_factory=dict)
    tatweel: Dict[str, str] = Field(default_factory=dict)
    zero_width_chars: Dict[str, str] = Field(default_factory=dict)
    
    # Processing options
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    
    @validator('pipeline_order')
    def validate_pipeline_order(cls, v):
        """Ensure all pipeline steps are valid"""
        valid_steps = {
            'persian_to_arabic', 'urdu_to_arabic', 'pashto_to_arabic',
            'kurdish_to_arabic', 'uyghur_to_arabic', 'sindhi_to_arabic',
            'malay_to_arabic', 'arabic_variants', 'other_safe_to_arabic',
            'punctuation_normalization', 'numbers_normalization',
            'diacritics', 'quranic_marks', 'tatweel', 'zero_width_chars'
        }
        
        invalid_steps = set(v) - valid_steps
        if invalid_steps:
            raise ValueError(f"Invalid pipeline steps: {invalid_steps}")
        
        return v
    
    def get_mapping(self, step_name: str) -> Dict[str, str]:
        """Get character mapping for a specific step"""
        return getattr(self, step_name, {})
    
    def get_all_mappings(self) -> List[Dict[str, str]]:
        """Get all character mappings in pipeline order"""
        return [self.get_mapping(step) for step in self.pipeline_order]


class ArabicTextNormalizer:
    """Arabic text normalizer using configuration"""
    
    def __init__(self, config: ArabicNormalizationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def map_to_standard_arabic(self, text: str, mapping: Dict[str, str]) -> str:
        """Apply character mapping to text"""
        if not mapping:
            return text
            
        # Apply character mapping
        for src, tgt in mapping.items():
            if src in text:
                self.logger.debug(f"Replacing '{src}' with '{tgt}'")
                text = text.replace(src, tgt)
        
        return text
    
    def post_process_text(self, text: str) -> str:
        """Apply post-processing options"""
        if self.config.processing.normalize_whitespace:
            # Normalize multiple spaces to single space
            text = re.sub(r'\s+', ' ', text)
        
        if self.config.processing.strip_whitespace:
            # Strip leading/trailing whitespace
            text = text.strip()
        
        return text
    
    def clean_text(self, text: str) -> str:
        """Clean text using all configured mappings in order"""
        if not text:
            return text
        
        self.logger.info(f"Starting text normalization: '{text[:50]}...'")
        
        # Apply each mapping in pipeline order
        for step_name in self.config.pipeline_order:
            mapping = self.config.get_mapping(step_name)
            if mapping:
                old_text = text
                text = self.map_to_standard_arabic(text, mapping)
                if old_text != text:
                    self.logger.debug(f"Step '{step_name}' changed text")
        
        # Apply post-processing
        text = self.post_process_text(text)
        
        self.logger.info(f"Normalization complete: '{text[:50]}...'")
        return text


def load_config_from_yaml(config_path: str = "config.yaml") -> ArabicNormalizationConfig:
    """Load and validate configuration from YAML file"""
    try:
        # Initialize Hydra with the config directory
        config_dir = Path(config_path).parent.absolute()
        config_name = Path(config_path).stem
        
        with initialize(version_base=None, config_path=str(config_dir)):
            # Load configuration
            cfg = compose(config_name=config_name)
            
            # Convert OmegaConf to dict for Pydantic
            config_dict = OmegaConf.to_container(cfg, resolve=True)
            
            # Validate with Pydantic
            config = ArabicNormalizationConfig(**config_dict)
            
            logging.info("Configuration loaded and validated successfully")
            return config
            
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        raise


@hydra.main(version_base=None, config_path=".", config_name="arabic_config")
def main(cfg: DictConfig) -> None:
    """Main function using Hydra decorator"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Convert OmegaConf to Pydantic model
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        config = ArabicNormalizationConfig(**config_dict)
        
        # Create normalizer
        normalizer = ArabicTextNormalizer(config)
        
        # Example usage
        test_texts = [
            "سلام علیکم دوستان",  # Persian/Urdu mixed
            "اَلْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِینَ",  # Arabic with diacritics
            "۱۲۳۴۵ پیسے",  # Persian numbers
            "ګرانو ملګرو،   ښه راغلاست"  # Pashto with extra spaces
        ]
        
        print("\n=== Arabic Text Normalization Demo ===")
        for i, text in enumerate(test_texts, 1):
            normalized = normalizer.clean_text(text)
            print(f"\n{i}. Original:   {text}")
            print(f"   Normalized: {normalized}")
        
        # Print configuration summary
        print(f"\n=== Configuration Summary ===")
        print(f"Pipeline steps: {len(config.pipeline_order)}")
        print(f"Total mappings: {sum(len(config.get_mapping(step)) for step in config.pipeline_order)}")
        print(f"Processing options: {config.processing}")
        
    except Exception as e:
        logging.error(f"Application error: {e}")
        raise


# Alternative function to load config without Hydra decorator
def load_and_normalize(config_path: str, text: str) -> str:
    """Convenience function to load config and normalize text"""
    config = load_config_from_yaml(config_path)
    normalizer = ArabicTextNormalizer(config)
    return normalizer.clean_text(text)


if __name__ == "__main__":
    main()