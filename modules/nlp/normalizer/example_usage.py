"""
Example usage of the Arabic Text Normalization system
"""

import logging
from arabic_normalizer import ArabicNormalizationConfig, ArabicTextNormalizer, load_config_from_yaml

# Setup logging
logging.basicConfig(level=logging.INFO)

def example_usage():
    """Demonstrate different ways to use the Arabic normalizer"""
    
    print("=== Arabic Text Normalization Examples ===\n")
    
    # Method 1: Load from YAML file
    print("1. Loading configuration from YAML...")
    try:
        config = load_config_from_yaml("arabic_config.yaml")
        normalizer = ArabicTextNormalizer(config)
        
        # Test cases with different script types
        test_cases = [
            ("Persian text with numbers", "سلام! من ۱۲۳ سال دارم و در ایران زندگی می‌کنم."),
            ("Urdu text", "آپ کیسے ہیں؟ میں ٹھیک ہوں، شکریہ!"),
            ("Arabic with diacritics", "اَلْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِینَ"),
            ("Pashto text", "ښه راغلاست! زه د افغانستان څخه یم."),
            ("Mixed scripts", "Kurdish: ڕۆژی باش! Persian: روز خوب! Arabic: يوم جيد!"),
            ("Text with extra spaces", "متن     با    فاصله‌های    اضافی"),
            ("Numbers mixed", "سال ۱۴۰۳ میلادی برابر با ١٤٤٥ هجری است"),
        ]
        
        for description, text in test_cases:
            normalized = normalizer.clean_text(text)
            print(f"\n{description}:")
            print(f"  Original:   {text}")
            print(f"  Normalized: {normalized}")
            
    except Exception as e:
        print(f"Error loading configuration: {e}")
    
    print("\n" + "="*60)
    
    # Method 2: Create configuration programmatically
    print("\n2. Creating configuration programmatically...")
    
    # Simple configuration for demonstration
    simple_config = ArabicNormalizationConfig(
        pipeline_order=["persian_to_arabic", "diacritics", "numbers_normalization"],
        persian_to_arabic={"پ": "ب", "چ": "ج", "ژ": "ز", "گ": "ك"},
        diacritics={"َ": "", "ِ": "", "ُ": "", "ً": "", "ٍ": "", "ٌ": ""},
        numbers_normalization={"۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5"}
    )
    
    simple_normalizer = ArabicTextNormalizer(simple_config)
    
    test_text = "این متن فارسی با اَعراب و اعداد ۱۲۳ است."
    result = simple_normalizer.clean_text(test_text)
    
    print(f"Simple config test:")
    print(f"  Original:   {test_text}")
    print(f"  Normalized: {result}")
    
    print("\n" + "="*60)
    
    # Method 3: Configuration validation demo
    print("\n3. Configuration validation demo...")
    
    try:
        # This should fail validation
        invalid_config = ArabicNormalizationConfig(
            pipeline_order=["invalid_step", "another_invalid_step"],
            persian_to_arabic={"ا": "ب"}  # Valid mapping
        )
    except Exception as e:
        print(f"Validation correctly caught invalid config: {e}")
    
    print("\n4. Configuration statistics...")
    config = load_config_from_yaml("arabic_config.yaml")
    
    total_mappings = 0
    for step in config.pipeline_order:
        mapping = config.get_mapping(step)
        count = len(mapping)
        total_mappings += count
        if count > 0:
            print(f"  {step}: {count} character mappings")
    
    print(f"\nTotal character mappings: {total_mappings}")
    print(f"Pipeline steps: {len(config.pipeline_order)}")


def benchmark_performance():
    """Simple performance test"""
    import time
    
    print("\n=== Performance Benchmark ===")
    
    config = load_config_from_yaml("arabic_config.yaml")
    normalizer = ArabicTextNormalizer(config)
    
    # Large test text
    test_text = "سلام علیکم دوستان! " * 1000  # Repeat 1000 times
    
    start_time = time.time()
    normalized = normalizer.clean_text(test_text)
    end_time = time.time()
    
    print(f"Processed {len(test_text)} characters in {end_time - start_time:.4f} seconds")
    print(f"Rate: {len(test_text) / (end_time - start_time):.0f} characters/second")


if __name__ == "__main__":
    example_usage()
    benchmark_performance()


# requirements.txt content:
"""
hydra-core>=1.3.0
pydantic>=2.0.0
omegaconf>=2.3.0
"""

# To run the examples:
"""
1. Save the YAML config as 'arabic_config.yaml'
2. Save the Python code as 'arabic_normalizer.py'
3. Save this file as 'example_usage.py'
4. Install requirements: pip install hydra-core pydantic omegaconf
5. Run: python example_usage.py

Or use with Hydra directly:
python arabic_normalizer.py
"""