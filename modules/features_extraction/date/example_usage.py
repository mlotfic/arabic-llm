#!/usr/bin/env python3
"""
Example usage script for the Date Extraction Configuration System
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add the current directory to the path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from date_config_loader import (
    DateConfigLoader, 
    DateExtractor, 
    DateExtractionConfig,
    CalendarConversionConfig,
    DeduplicationConfig,
    KeywordsConfig,
    PatternConfig
)


def create_sample_config_programmatically() -> DateExtractionConfig:
    """Create a sample configuration programmatically for testing"""
    
    # Calendar conversion settings
    calendar_conversion = CalendarConversionConfig(
        gregorian_to_hijri_offset=622,
        gregorian_to_hijri_factor=0.97,
        hijri_to_gregorian_factor=0.97
    )
    
    # Deduplication settings
    deduplication = DeduplicationConfig(
        tolerance_days=1,
        keep_first_occurrence=True
    )
    
    # Keywords
    keywords = KeywordsConfig(
        hijri=["هـ", "هجري", "هجرية", "AH"],
        gregorian=["م", "ميلادي", "ميلادية", "AD", "CE"],
        year_indicators=["سنة", "عام", "في عام", "في سنة"]
    )
    
    # Sample patterns (simplified)
    patterns = [
        PatternConfig(
            name="hijri_basic",
            pattern=r'(\d{1,4})\s*(هـ|هجري|هجرية|AH)',
            description="Basic Hijri year pattern",
            example="1445 هـ",
            priority=1,
            match_type="year",
            hijri_start=1,
            gregorian_start=None,
            hijri_end=None,
            gregorian_end=None
        ),
        PatternConfig(
            name="gregorian_basic",
            pattern=r'(\d{1,4})\s*(م|ميلادي|ميلادية|AD|CE)',
            description="Basic Gregorian year pattern",
            example="2023 م",
            priority=2,
            match_type="year",
            hijri_start=None,
            gregorian_start=1,
            hijri_end=None,
            gregorian_end=None
        )
    ]
    
    return DateExtractionConfig(
        calendar_conversion=calendar_conversion,
        deduplication=deduplication,
        keywords=keywords,
        patterns=patterns
    )


def test_date_extraction():
    """Test the date extraction functionality"""
    
    print("=== Testing Date Extraction ===\n")
    
    # Test texts in Arabic
    test_texts = [
        "في سنة 1445 هـ حدث كذا وكذا",
        "العام 2023 م كان عاماً مهماً",
        "من 1440 هـ إلى 1445 هـ",
        "في الفترة من 2020 م إلى 2023 م",
        "حوالي 1440 هـ (2019 م)",
        "بعد 1445 هـ بدأت الأحداث",
        "خلال عام 2023 م شهدنا تطورات",
        "في هذا العام 1445 هـ"
    ]
    
    try:
        # Method 1: Load from YAML file (if exists)
        if os.path.exists("date_config.yaml"):
            print("Loading configuration from YAML file...")
            loader = DateConfigLoader(config_path=".", config_name="date_config")
            config = loader.load_config()
        else:
            print("YAML file not found. Using programmatic configuration...")
            config = create_sample_config_programmatically()
        
        # Create extractor
        extractor = DateExtractor(config)
        
        print(f"Configuration loaded successfully!")
        print(f"  - Patterns: {len(config.patterns)}")
        print(f"  - Hijri keywords: {len(config.keywords.hijri)}")
        print(f"  - Gregorian keywords: {len(config.keywords.gregorian)}")
        print(f"  - Year indicators: {len(config.keywords.year_indicators)}")
        print(f"  - Tolerance days: {config.deduplication.tolerance_days}")
        print()
        
        # Process each test text
        all_results = []
        for i, text in enumerate(test_texts, 1):
            print(f"Test {i}: {text}")
            results = extractor.extract_dates(text)
            
            if results:
                for result in results:
                    print(f"  ✓ Found: '{result['text']}' ({result['pattern_name']})")
                    if result['hijri_start']:
                        print(f"    Hijri: {result['hijri_start']}")
                    if result['gregorian_start']:
                        print(f"    Gregorian: {result['gregorian_start']}")
                    if result['match_type'] == 'range':
                        if result['hijri_end']:
                            print(f"    Hijri end: {result['hijri_end']}")
                        if result['gregorian_end']:
                            print(f"    Gregorian end: {result['gregorian_end']}")
                all_results.extend(results)
            else:
                print("  ✗ No dates found")
            print()
        
        # Test calendar conversion
        print("=== Testing Calendar Conversion ===")
        print(f"1445 Hijri → {extractor.hijri_year_to_gregorian_year(1445)} Gregorian")
        print(f"2023 Gregorian → {extractor.gregorian_year_to_hijri_year(2023)} Hijri")
        print()
        
        # Test deduplication
        print("=== Testing Deduplication ===")
        print(f"Total extractions before deduplication: {len(all_results)}")
        
        # Create some duplicate test data
        duplicate_test = [
            {"hijri_start": 1445, "gregorian_start": 2023, "hijri_end": None, "gregorian_end": None},
            {"hijri_start": 1445, "gregorian_start": 2023, "hijri_end": None, "gregorian_end": None},  # Exact duplicate
            {"hijri_start": 1446, "gregorian_start": 2024, "hijri_end": None, "gregorian_end": None},  # Within tolerance
            {"hijri_start": 1450, "gregorian_start": 2028, "hijri_end": None, "gregorian_end": None},  # Outside tolerance
        ]
        
        deduplicated = extractor.remove_date_duplicates(duplicate_test)
        print(f"Test data: {len(duplicate_test)} items → {len(deduplicated)} after deduplication")
        
        for item in deduplicated:
            print(f"  Kept: Hijri {item['hijri_start']}, Gregorian {item['gregorian_start']}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


def validate_config_schema():
    """Test configuration validation"""
    
    print("=== Testing Configuration Validation ===\n")
    
    # Test invalid configurations
    test_cases = [
        {
            "name": "Invalid regex pattern",
            "config": {
                "calendar_conversion": {"gregorian_to_hijri_offset": 622, "gregorian_to_hijri_factor": 0.97, "hijri_to_gregorian_factor": 0.97},
                "deduplication": {"tolerance_days": 1, "keep_first_occurrence": True},
                "keywords": {"hijri": ["هـ"], "gregorian": ["م"], "year_indicators": ["سنة"]},
                "patterns": [{
                    "name": "invalid_pattern",
                    "pattern": "([unclosed_group",  # Invalid regex
                    "description": "Test pattern",
                    "example": "test",
                    "priority": 1,
                    "match_type": "year",
                    "hijri_start": 1
                }]
            }
        },
        {
            "name": "Empty keywords",
            "config": {
                "calendar_conversion": {"gregorian_to_hijri_offset": 622, "gregorian_to_hijri_factor": 0.97, "hijri_to_gregorian_factor": 0.97},
                "deduplication": {"tolerance_days": 1, "keep_first_occurrence": True},
                "keywords": {"hijri": [], "gregorian": ["م"], "year_indicators": ["سنة"]},  # Empty hijri keywords
                "patterns": [{
                    "name": "test_pattern",
                    "pattern": r"\d+",
                    "description": "Test pattern",
                    "example": "test",
                    "priority": 1,
                    "match_type": "year",
                    "hijri_start": 1
                }]
            }
        },
        {
            "name": "Invalid match type",
            "config": {
                "calendar_conversion": {"gregorian_to_hijri_offset": 622, "gregorian_to_hijri_factor": 0.97, "hijri_to_gregorian_factor": 0.97},
                "deduplication": {"tolerance_days": 1, "keep_first_occurrence": True},
                "keywords": {"hijri": ["هـ"], "gregorian": ["م"], "year_indicators": ["سنة"]},
                "patterns": [{
                    "name": "invalid_match_type",
                    "pattern": r"\d+",
                    "description": "Test pattern",
                    "example": "test",
                    "priority": 1,
                    "match_type": "invalid_type",  # Invalid match type
                    "hijri_start": 1
                }]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['name']}")
        try:
            config = DateExtractionConfig(**test_case['config'])
            print(f"  ✗ Validation should have failed but didn't")
        except Exception as e:
            print(f"  ✓ Validation failed as expected: {type(e).__name__}")
        print()


def main():
    """Main function to run all tests"""
    print("Date Extraction Configuration System - Test Suite")
    print("=" * 60)
    print()
    
    # Test configuration validation
    validate_config_schema()
    
    # Test date extraction
    test_date_extraction()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    main()