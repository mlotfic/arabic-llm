"""
Date Configuration Loader with Pydantic validation and Hydra integration
"""

import re
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator, root_validator
from hydra import compose, initialize
from omegaconf import DictConfig, OmegaConf
import hydra
from hydra.core.config_store import ConfigStore
from dataclasses import dataclass


# Pydantic models for validation
class CalendarConversionConfig(BaseModel):
    """Configuration for calendar conversion factors"""
    gregorian_to_hijri_offset: int = Field(default=622, ge=0)
    gregorian_to_hijri_factor: float = Field(default=0.97, gt=0, le=1)
    hijri_to_gregorian_factor: float = Field(default=0.97, gt=0, le=1)


class DeduplicationConfig(BaseModel):
    """Configuration for date deduplication"""
    tolerance_days: int = Field(default=1, ge=0)
    keep_first_occurrence: bool = Field(default=True)


class KeywordsConfig(BaseModel):
    """Configuration for date keywords"""
    hijri: List[str] = Field(default_factory=list)
    gregorian: List[str] = Field(default_factory=list)
    year_indicators: List[str] = Field(default_factory=list)
    
    @validator('hijri', 'gregorian', 'year_indicators')
    def validate_non_empty(cls, v):
        if not v:
            raise ValueError("Keyword lists cannot be empty")
        return v


class PatternConfig(BaseModel):
    """Configuration for a single date pattern"""
    name: str = Field(..., min_length=1)
    pattern: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    example: str = Field(..., min_length=1)
    priority: int = Field(..., ge=1, le=10)
    match_type: str = Field(..., regex=r'^(year|range|mixed)$')
    hijri_start: Optional[int] = Field(default=None, ge=1)
    gregorian_start: Optional[int] = Field(default=None, ge=1)
    hijri_end: Optional[int] = Field(default=None, ge=1)
    gregorian_end: Optional[int] = Field(default=None, ge=1)
    
    @validator('pattern')
    def validate_pattern(cls, v):
        """Validate that pattern is a valid regex"""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v
    
    @root_validator
    def validate_pattern_config(cls, values):
        """Validate pattern configuration consistency"""
        match_type = values.get('match_type')
        hijri_start = values.get('hijri_start')
        gregorian_start = values.get('gregorian_start')
        hijri_end = values.get('hijri_end')
        gregorian_end = values.get('gregorian_end')
        
        if match_type == 'range':
            # Range patterns should have either start or end defined
            if not any([hijri_start, gregorian_start, hijri_end, gregorian_end]):
                raise ValueError("Range patterns must have at least one date field defined")
        elif match_type == 'year':
            # Year patterns should have start defined
            if not any([hijri_start, gregorian_start]):
                raise ValueError("Year patterns must have at least one start date field defined")
        
        return values


class DateExtractionConfig(BaseModel):
    """Main configuration for date extraction"""
    calendar_conversion: CalendarConversionConfig = Field(default_factory=CalendarConversionConfig)
    deduplication: DeduplicationConfig = Field(default_factory=DeduplicationConfig)
    keywords: KeywordsConfig = Field(default_factory=KeywordsConfig)
    patterns: List[PatternConfig] = Field(default_factory=list)
    
    @validator('patterns')
    def validate_patterns(cls, v):
        if not v:
            raise ValueError("At least one pattern must be defined")
        
        # Check for duplicate pattern names
        names = [p.name for p in v]
        if len(names) != len(set(names)):
            raise ValueError("Pattern names must be unique")
        
        return v
    
    class Config:
        validate_assignment = True


# Hydra configuration dataclass
@dataclass
class HydraDateConfig:
    """Hydra configuration dataclass"""
    calendar_conversion: Dict[str, Union[int, float]]
    deduplication: Dict[str, Union[int, bool]]
    keywords: Dict[str, List[str]]
    patterns: List[Dict[str, Any]]


# Configuration loader class
class DateConfigLoader:
    """Loads and validates date extraction configuration"""
    
    def __init__(self, config_path: str = "conf", config_name: str = "date_config"):
        self.config_path = config_path
        self.config_name = config_name
        self._config: Optional[DateExtractionConfig] = None
        self._raw_config: Optional[DictConfig] = None
    
    def load_config(self) -> DateExtractionConfig:
        """Load and validate configuration from YAML file"""
        try:
            with initialize(config_path=self.config_path, version_base=None):
                cfg = compose(config_name=self.config_name)
                self._raw_config = cfg
                
                # Convert OmegaConf to dict for Pydantic
                config_dict = OmegaConf.to_container(cfg, resolve=True)
                
                # Validate with Pydantic
                self._config = DateExtractionConfig(**config_dict)
                
                return self._config
                
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def get_config(self) -> DateExtractionConfig:
        """Get loaded configuration"""
        if self._config is None:
            raise ValueError("Configuration not loaded. Call load_config() first.")
        return self._config
    
    def get_raw_config(self) -> DictConfig:
        """Get raw Hydra configuration"""
        if self._raw_config is None:
            raise ValueError("Configuration not loaded. Call load_config() first.")
        return self._raw_config


# Utility functions adapted from original code
class DateExtractor:
    """Date extraction utility class using the configuration"""
    
    def __init__(self, config: DateExtractionConfig):
        self.config = config
        self._compiled_patterns = None
        self._build_patterns()
    
    def _build_patterns(self):
        """Build compiled regex patterns from configuration"""
        self._compiled_patterns = []
        
        # Build keyword patterns
        hijri_pattern = self._keywords_to_regex(self.config.keywords.hijri)
        gregorian_pattern = self._keywords_to_regex(self.config.keywords.gregorian)
        year_pattern = self._keywords_to_regex(self.config.keywords.year_indicators)
        
        # Sort patterns by priority
        sorted_patterns = sorted(self.config.patterns, key=lambda x: x.priority)
        
        for pattern_config in sorted_patterns:
            # Replace placeholders in pattern
            pattern_str = pattern_config.pattern
            pattern_str = pattern_str.replace('{hijri_pattern}', hijri_pattern)
            pattern_str = pattern_str.replace('{gregorian_pattern}', gregorian_pattern)
            pattern_str = pattern_str.replace('{year_pattern}', year_pattern)
            
            try:
                compiled_pattern = re.compile(pattern_str, re.UNICODE)
                self._compiled_patterns.append({
                    'compiled': compiled_pattern,
                    'config': pattern_config
                })
            except re.error as e:
                print(f"Warning: Failed to compile pattern '{pattern_config.name}': {e}")
    
    def _keywords_to_regex(self, keywords: List[str]) -> str:
        """Convert list of keywords to regex alternation pattern"""
        # Sort by length descending, escape regex chars, make spaces flexible
        escaped = [re.escape(k).replace(r'\ ', r'\s*') for k in sorted(keywords, key=len, reverse=True)]
        return '|'.join(escaped)
    
    def gregorian_year_to_hijri_year(self, g_year: int) -> int:
        """Convert Gregorian year to Hijri year"""
        return int((g_year - self.config.calendar_conversion.gregorian_to_hijri_offset) / 
                  self.config.calendar_conversion.gregorian_to_hijri_factor)
    
    def hijri_year_to_gregorian_year(self, hijri_year: int) -> int:
        """Convert Hijri year to Gregorian year"""
        return int(hijri_year * self.config.calendar_conversion.hijri_to_gregorian_factor + 
                  self.config.calendar_conversion.gregorian_to_hijri_offset)
    
    def remove_date_duplicates(self, dict_list: List[Dict]) -> List[Dict]:
        """Remove duplicate dictionaries where date ranges are within tolerance"""
        if not dict_list:
            return []
        
        result = []
        tolerance = self.config.deduplication.tolerance_days
        
        for current_dict in dict_list:
            is_duplicate = False
            
            for existing_dict in result:
                # Helper function to safely convert to int
                def safe_int(value):
                    if value is None:
                        return None
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None
                
                # Convert all date values safely
                current_hijri_end = safe_int(current_dict.get("hijri_end"))
                existing_hijri_end = safe_int(existing_dict.get("hijri_end"))
                current_hijri_start = safe_int(current_dict.get("hijri_start"))
                existing_hijri_start = safe_int(existing_dict.get("hijri_start"))
                current_gregorian_start = safe_int(current_dict.get("gregorian_start"))
                existing_gregorian_start = safe_int(existing_dict.get("gregorian_start"))
                current_gregorian_end = safe_int(current_dict.get("gregorian_end"))
                existing_gregorian_end = safe_int(existing_dict.get("gregorian_end"))
                
                # Check if all date fields are within tolerance
                matches = []
                
                if current_hijri_end is not None and existing_hijri_end is not None:
                    matches.append(abs(current_hijri_end - existing_hijri_end) <= tolerance)
                if current_hijri_start is not None and existing_hijri_start is not None:
                    matches.append(abs(current_hijri_start - existing_hijri_start) <= tolerance)
                if current_gregorian_start is not None and existing_gregorian_start is not None:
                    matches.append(abs(current_gregorian_start - existing_gregorian_start) <= tolerance)
                if current_gregorian_end is not None and existing_gregorian_end is not None:
                    matches.append(abs(current_gregorian_end - existing_gregorian_end) <= tolerance)
                
                # If all compared fields match within tolerance, it's a duplicate
                if matches and all(matches):
                    is_duplicate = True
                    break
            
            # Only add if it's not a duplicate
            if not is_duplicate:
                result.append(current_dict)
        
        return result
    
    def extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text using configured patterns"""
        if self._compiled_patterns is None:
            raise ValueError("Patterns not built. Initialize DateExtractor first.")
        
        results = []
        
        for pattern_info in self._compiled_patterns:
            pattern = pattern_info['compiled']
            config = pattern_info['config']
            
            for match in pattern.finditer(text):
                result = {
                    'pattern_name': config.name,
                    'match_type': config.match_type,
                    'text': match.group(0),
                    'start_pos': match.start(),
                    'end_pos': match.end(),
                    'hijri_start': None,
                    'hijri_end': None,
                    'gregorian_start': None,
                    'gregorian_end': None
                }
                
                # Extract groups based on configuration
                groups = match.groups()
                
                if config.hijri_start and len(groups) >= config.hijri_start:
                    try:
                        result['hijri_start'] = int(groups[config.hijri_start - 1])
                    except (ValueError, TypeError):
                        pass
                
                if config.hijri_end and len(groups) >= config.hijri_end:
                    try:
                        result['hijri_end'] = int(groups[config.hijri_end - 1])
                    except (ValueError, TypeError):
                        pass
                
                if config.gregorian_start and len(groups) >= config.gregorian_start:
                    try:
                        result['gregorian_start'] = int(groups[config.gregorian_start - 1])
                    except (ValueError, TypeError):
                        pass
                
                if config.gregorian_end and len(groups) >= config.gregorian_end:
                    try:
                        result['gregorian_end'] = int(groups[config.gregorian_end - 1])
                    except (ValueError, TypeError):
                        pass
                
                results.append(result)
        
        # Remove duplicates if configured
        if self.config.deduplication.keep_first_occurrence:
            results = self.remove_date_duplicates(results)
        
        return results


# Example usage
if __name__ == "__main__":
    # Example of how to use the configuration loader
    try:
        # Load configuration
        loader = DateConfigLoader(config_path=".", config_name="date_config")
        config = loader.load_config()
        
        print("Configuration loaded successfully!")
        print(f"Number of patterns: {len(config.patterns)}")
        print(f"Number of Hijri keywords: {len(config.keywords.hijri)}")
        print(f"Number of Gregorian keywords: {len(config.keywords.gregorian)}")
        
        # Create date extractor
        extractor = DateExtractor(config)
        
        # Example text extraction
        test_text = "في سنة 1445 هـ (2023 م) حدث هذا الأمر من 1440 إلى 1445 هـ"
        results = extractor.extract_dates(test_text)
        
        print(f"\nExtracted {len(results)} date patterns:")
        for result in results:
            print(f"  - {result['pattern_name']}: {result['text']}")
            
    except Exception as e:
        print(f"Error: {e}")


# Hydra app example
@hydra.main(version_base=None, config_path=".", config_name="date_config")
def main(cfg: DictConfig) -> None:
    """Example Hydra app using the date configuration"""
    try:
        # Convert to Pydantic model for validation
        config_dict = OmegaConf.to_container(cfg, resolve=True)
        config = DateExtractionConfig(**config_dict)
        
        print("Hydra configuration loaded and validated!")
        print(f"Conversion offset: {config.calendar_conversion.gregorian_to_hijri_offset}")
        print(f"Tolerance days: {config.deduplication.tolerance_days}")
        
        # Create extractor and test
        extractor = DateExtractor(config)
        test_text = "حوالي 1440 هـ والعام 2023 م"
        results = extractor.extract_dates(test_text)
        
        for result in results:
            print(f"Found: {result['text']} ({result['pattern_name']})")
            
    except Exception as e:
        print(f"Configuration error: {e}")


if __name__ == "__main__":
    # Uncomment to run as Hydra app
    # main()
    pass