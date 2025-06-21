# Date Extraction Configuration System

A comprehensive system for extracting Arabic/Islamic dates from text using YAML configuration, Pydantic validation, and Hydra integration.

## Features

- **YAML Configuration**: Easy-to-modify configuration files
- **Pydantic Validation**: Type-safe configuration with validation
- **Hydra Integration**: Professional configuration management
- **Regex Pattern Matching**: Flexible date pattern extraction
- **Calendar Conversion**: Hijri ↔ Gregorian year conversion
- **Deduplication**: Automatic removal of duplicate date extractions
- **Multilingual Support**: Arabic and English date indicators

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install hydra-core>=1.3.0
pip install pydantic>=1.10.0,<2.0.0
pip install omegaconf>=2.3.0
pip install PyYAML>=6.0
```

### 2. File Structure

```
project/
├── date_config.yaml          # Main configuration file
├── date_config_loader.py     # Core configuration loader
├── example_usage.py          # Example usage script
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Usage

### Basic Usage

```python
from date_config_loader import DateConfigLoader, DateExtractor

# Load configuration
loader = DateConfigLoader(config_path=".", config_name="date_config")
config = loader.load_config()

# Create extractor
extractor = DateExtractor(config)

# Extract dates from text
text = "في سنة 1445 هـ (2023 م) حدث هذا الأمر"
results = extractor.extract_dates(text)

for result in results:
    print(f"Found: {result['text']} ({result['pattern_name']})")
```

### Using with Hydra

```python
import hydra
from omegaconf import DictConfig
from date_config_loader import DateExtractionConfig, DateExtractor

@hydra.main(version_base=None, config_path=".", config_name="date_config")
def my_app(cfg: DictConfig) -> None:
    # Convert to Pydantic model
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    config = DateExtractionConfig(**config_dict)
    
    # Use the configuration
    extractor = DateExtractor(config)
    # ... rest of your application
```

### Programmatic Configuration

```python
from date_config_loader import (
    DateExtractionConfig, 
    CalendarConversionConfig,
    KeywordsConfig,
    PatternConfig
)

# Create configuration programmatically
config = DateExtractionConfig(
    calendar_conversion=CalendarConversionConfig(
        gregorian_to_hijri_offset=622,
        gregorian_to_hijri_factor=0.97
    ),
    keywords=KeywordsConfig(
        hijri=["هـ", "هجري", "AH"],
        gregorian=["م", "ميلادي", "AD"]
    ),
    patterns=[
        PatternConfig(
            name="basic_hijri",
            pattern=r'(\d{1,4})\s*(هـ|هجري)',
            description="Basic Hijri pattern",
            example="1445 هـ",
            priority=1,
            match_type="year",
            hijri_start=1
        )
    ]
)
```

## Configuration

### YAML Structure

The configuration file has four main sections:

1. **calendar_conversion**: Settings for Hijri ↔ Gregorian conversion
2. **deduplication**: Settings for removing duplicate extractions
3. **keywords**: Lists of keywords for different calendar types
4. **patterns**: Regex patterns for date extraction

### Pattern Configuration

Each pattern has the following fields:

- `name`: Unique identifier
- `pattern`: Regex pattern (with placeholders)
- `description`: Human-readable description
- `example`: Example text that matches
- `priority`: Processing priority (1 = highest)
- `match_type`: Type of match ("year", "range", "mixed")
- `hijri_start`, `gregorian_start`: Group indices for start dates
- `hijri_end`, `gregorian_end`: Group indices for end dates

### Supported Patterns

The system supports various date patterns:

- **Single dates**: "1445 هـ", "2023 م"
- **Date ranges**: "من 1440 إلى 1445 هـ"
- **Mixed calendars**: "1445 هـ (2023 م)"
- **Approximate dates**: "حوالي 1440 هـ"
- **Before/after**: "قبل 1445 هـ"
- **Flexible year indicators**: "سنة 1445 هـ"

## API Reference

### DateConfigLoader

```python
class DateConfigLoader:
    def __init__(self, config_path: str = "conf", config_name: str = "date_config")
    def load_config(self) -> DateExtractionConfig
    def get_config(self) -> DateExtractionConfig
    def get_raw_config(self) -> DictConfig
```

### DateExtractor

```python
class DateExtractor:
    def __init__(self, config: DateExtractionConfig)
    def extract_dates(self, text: str) -> List[Dict[str, Any]]
    def gregorian_year_to_hijri_year(self, g_year: int) -> int
    def hijri_year_to_gregorian_year(self, hijri_year: int) -> int
    def remove_date_duplicates(self, dict_list: List[Dict]) -> List[Dict]
```

### Result Format

Each extraction result contains:

```python
{
    'pattern_name': str,      # Name of matching pattern
    'match_type': str,        # Type: 'year', 'range', 'mixed'
    'text': str,              # Matched text
    'start_pos': int,         # Start position in text
    'end_pos': int,           # End position in text
    'hijri_start': int,       # Hijri start year (if any)
    'hijri_end': int,         # Hijri end year (if any)
    'gregorian_start': int,   # Gregorian start year (if any)
    'gregorian_end': int      # Gregorian end year (if any)
}
```

## Testing

Run the example script to test the system:

```bash
python example_usage.py
```

This will:
1. Load the configuration
2. Test date extraction on sample texts
3. Test calendar conversion
4. Test deduplication
5. Validate configuration schema

## Customization

### Adding New Keywords

Edit the `keywords` section in `date_config.yaml`:

```yaml
keywords:
  hijri:
    - "هـ"
    - "هجري"
    - "AH"
    - "your_new_keyword"
```

### Adding New Patterns

Add to the `patterns` section:

```yaml
patterns:
  - name: "your_pattern_name"
    pattern: 'your_regex_pattern'
    description: "Description of what it matches"
    example: "Example text"
    priority: 5
    match_type: "year"
    hijri_start: 1
```

### Adjusting Conversion Factors

Modify the `calendar_conversion` section:

```yaml
calendar_conversion:
  gregorian_to_hijri_offset: 622
  gregorian_to_hijri_factor: 0.97
  hijri_to_gregorian_factor: 0.97
```

## Error Handling

The system includes comprehensive error handling:

- **Configuration validation** with Pydantic
- **Regex compilation** error detection
- **Safe type conversion** for extracted numbers
- **Graceful handling** of malformed dates

## Performance Considerations

- Patterns are sorted by priority for efficient matching
- Regex patterns are compiled once and reused
- Deduplication uses configurable tolerance levels
- Large texts are processed efficiently with compiled patterns

## Troubleshooting

### Common Issues

1. **Configuration not loading**: Check YAML syntax and file path
2. **Patterns not matching**: Verify regex syntax and test with simple examples
3. **Import errors**: Ensure all dependencies are installed
4. **Encoding issues**: Ensure text files are saved as UTF-8

### Debug Mode

Enable debug output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Add new patterns to the YAML configuration
2. Test with diverse Arabic texts
3. Validate configuration changes
4. Update documentation

## License

This project is open source. Please ensure proper attribution when using or modifying.