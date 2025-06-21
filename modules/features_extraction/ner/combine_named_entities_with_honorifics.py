# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 18:58:45 2025

@author: m
"""

from typing import List, Dict, Set, Tuple
import re

# ======================== CONFIGURATION SECTION ========================
# This section contains all the patterns and honorifics for easy modification

class ArabicNERConfig:
    """Configuration class for Arabic NER patterns and honorifics"""
    
    # Before-name honorifics
    BEFORE_HONORIFICS = [
        "الشيخ", "الإمام", "الحافظ", "القاضي", "السيد", "العلامة", 
        "الفقيه", "المحدث", "المجتهد", "المفسر", "الولي", "المقرئ"
    ]
    
    # After-name honorifics
    AFTER_HONORIFICS = [
        "صلى الله عليه وسلم",  # SAW - Prophet
        "عليه السلام",        # AS - Peace be upon him
        "ﷺ",                   # SAW symbol
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
        "تغمده الله برحمته"  # May Allah cover him with mercy
    ]
    
    # Prophet titles and references
    PROPHET_TITLES = [
        "النبي", "نبيه", "رسول الله", "الرسول", "خاتم النبيين", 
        "سيد المرسلين", "الرسول الكريم", "النبي الكريم"
        
    ]
    
    # Prophet honorifics (specific to Prophet)
    PROPHET_HONORIFICS = [
        "صلى الله عليه وسلم", "عليه الصلاة والسلام", "ﷺ", "عليه السلام",
        "صلى الله عليه وآله وسلم", "صلى الله عليه وسلم وآله", "صلى الله عليه وسلم وصحبه",
        "صلى الله عليه وسلم وصحابته", "صلى الله عليه وسلم وآله وصحبه",
        "صلى الله عليه وسلم وآله وصحابته", "صلى الله عليه وسلم وآله وصحبه أجمعين",
        "صلى الله عليه وسلم وآله وصحبه أجمعين", "صلى الله عليه وسلم وآله وصحابته أجمعين",
        "صلى الله عليه وسلم وآله وصحابته الكرام", "صلى الله عليه وسلم وآله وصحابته الغر الميامين"
        "صلى الله عليه وسلم وآله وصحابته الطيبين الطاهرين", "صلى الله عليه وسلم وآله وصحابته أجمعين",
        "صلى الله عليه وسلم وآله وصحابته الكرام", "صلى الله عليه وسلم وآله وصحابته الغر الميامين",
        "صلى الله عليه وسلم وآله وصحابته الطيبين الطاهرين", "صلى الله عليه وسلم وآله وصحابته أجمعين"
        
    ]
    
    # Companion honorifics
    COMPANION_HONORIFICS = [
        "رضي الله عنه", "رضي الله عنها", "رضي الله عنهم", 
        "رضي الله عنهما", "رضوان الله عليه", "رضوان الله عليها"
    ]
    
    # Scholar honorifics
    SCHOLAR_HONORIFICS = [
        "رحمه الله", "رحمها الله", "رحمهم الله", "رحمة الله عليه",
        "رحمة الله عليها", "أجزل الله مثوبته", "تغمده الله برحمته",
        "عفا الله عنه", "غفر الله له", "تقبل الله منه",
        "تقبل الله منها", "تقبل الله منهم", "تقبل الله منا ومنكم",
        "تقبل الله عمله", "تقبل الله عملها", "تقبل الله أعمالهم"
    ]
    
    # Allah references
    ALLAH_REFERENCES = [
        "الله", "اللهم", "سبحانه وتعالى", "عز وجل", "تبارك وتعالى",
        "جل جلاله", "سبحانه", "المولى عز وجل"
    ]
    
    # Common Arabic cities
    CITIES = [
        "المدينة", "مكة", "البصرة", "الكوفة", "بغداد", "دمشق", 
        "القاهرة", "الفسطاط", "واسط", "الري", "نيسابور", "هراة",
        "القدس", "القدس الشريف", "المدينة المنورة", "مكة المكرمة"
    ]
    
    # Common Arabic first names for fallback patterns
    COMMON_NAMES = [
        "محمد", "أحمد", "علي", "حسن", "حسين", "عمر", "عثمان", 
        "أبو", "عبد", "عبدالله", "عبدالرحمن", "إبراهيم", "يوسف"
    ]
    
    # Special referable titles
    SPECIAL_TITLES = [
        "النبي صلى الله عليه وسلم",
        "نبيه صلى الله عليه وسلم", 
        "رسول الله صلى الله عليه وسلم",
        "الخليفة الراشد",
        "أمير المؤمنين",
        "رضي الله عن الصحابة أجمعين"
    ]

def keywords_to_regex(keywords):
    """
    Convert list of keywords to regex alternation pattern.
    Sorts by length (longest first) and handles spaces flexibly.
    
    Args:
        keywords: List of keyword strings
    
    Returns:
        String: Regex pattern with | alternation
    """
    # Sort by length descending, escape regex chars, make spaces flexible
    escaped = [re.escape(k).replace(r'\ ', r'\s*') for k in sorted(keywords, key=len, reverse=True)]
    return '|'.join(escaped)

def build_regex_patterns(config: ArabicNERConfig = None) -> List[Dict]:
    """
    Build regex patterns from configuration - easy to modify!
    """
    if config is None:
        config = ArabicNERConfig()
    
    # Arabic letter pattern for names
    arabic_name_pattern = r'[أابتثجحخدذرزسشصضطظعغفقكلمنهوي]{2,}'
    
    patterns = []
    
    # 1. Prophet references with honorifics
    prophet_titles = keywords_to_regex(config.PROPHET_TITLES)
    prophet_honorifics = keywords_to_regex(config.PROPHET_HONORIFICS)
    patterns.append({
        'pattern': rf'\b({prophet_titles})\s+({prophet_honorifics})',
        'type': 'PROPHET',
        'priority': 10
    })
    
    # 2. Allah references  
    allah_refs = keywords_to_regex(config.ALLAH_REFERENCES)
    patterns.append({
        'pattern': rf'\b({allah_refs})\b',
        'type': 'DEITY', 
        'priority': 9
    })
    
    # 3. Companions with honorifics
    companion_honorifics = keywords_to_regex(config.COMPANION_HONORIFICS)
    patterns.append({
        'pattern': rf'\b({arabic_name_pattern}(?:\s+بن\s+{arabic_name_pattern})*)\s+({companion_honorifics})\b',
        'type': 'COMPANION',
        'priority': 8
    })
    
    # 4. Scholars with honorifics
    scholar_honorifics = keywords_to_regex(config.SCHOLAR_HONORIFICS)  
    patterns.append({
        'pattern': rf'\b({arabic_name_pattern}(?:\s+بن\s+{arabic_name_pattern})*)\s+({scholar_honorifics})\b',
        'type': 'SCHOLAR',
        'priority': 7
    })
    
    # 5. Titled persons (before-honorifics + names)
    before_titles = keywords_to_regex(config.BEFORE_HONORIFICS)
    patterns.append({
        'pattern': rf'\b({before_titles})\s+({arabic_name_pattern}(?:\s+بن\s+{arabic_name_pattern})*)',
        'type': 'TITLED_PERSON',
        'priority': 8
    })
    
    # 6. Cities
    cities = keywords_to_regex(config.CITIES)
    patterns.append({
        'pattern': rf'\b({cities})\b',
        'type': 'CITY',
        'priority': 6
    })
    
    # 7. Names with "بن" pattern
    patterns.append({
        'pattern': rf'\b({arabic_name_pattern})\s+بن\s+({arabic_name_pattern})\b',
        'type': 'PERSON',
        'priority': 5
    })
    
    # 8. Common names + other names
    common_names = keywords_to_regex(config.COMMON_NAMES)
    patterns.append({
        'pattern': rf'\b({common_names})\s+({arabic_name_pattern})\b',
        'type': 'PERSON', 
        'priority': 4
    })
    
    return patterns



def combine_named_entities_with_honorifics(
    tokens: List[str], 
    labels: List[str], 
    config: 'ArabicNERConfig' = None
) -> List[Dict]:
    """
    Combines tokens that are part of the same named entity, with special handling for Arabic honorifics.
    Now uses configurable honorifics for easy modification!
    """
    if config is None:
        config = ArabicNERConfig()
    
    def is_before_honorific(token: str) -> bool:
        """Check if token is a before-name honorific"""
        return token in config.BEFORE_HONORIFICS
    
    def find_after_honorific_sequence(tokens: List[str], start_idx: int) -> tuple:
        """
        Find if there's an after-honorific sequence starting at start_idx
        Returns (honorific_text, length) or (None, 0) if not found
        """
        remaining_tokens = tokens[start_idx:]
        
        # Check each after_honorific pattern
        for honorific in config.AFTER_HONORIFICS:
            honorific_tokens = honorific.split()
            if len(honorific_tokens) <= len(remaining_tokens):
                # Check if tokens match the honorific pattern
                if remaining_tokens[:len(honorific_tokens)] == honorific_tokens:
                    return (honorific, len(honorific_tokens))
        
        return (None, 0)
    
    def should_include_preceding_honorific(tokens: List[str], entity_start: int) -> tuple:
        """
        Check if there's a before-honorific that should be included with the entity
        Returns (honorific_text, honorific_start_idx) or (None, entity_start)
        """
        if entity_start > 0 and is_before_honorific(tokens[entity_start - 1]):
            return (tokens[entity_start - 1], entity_start - 1)
        return (None, entity_start)
    
    combined_entities = []
    current_entity = None
    i = 0
    
    while i < len(tokens):
        token = tokens[i]
        label = labels[i]
        
        # Check if this is the beginning of a new entity
        if label.startswith('B-'):
            # If we were building an entity, add it to our results
            if current_entity:
                combined_entities.append(current_entity)
            
            entity_type = label[2:]  # Remove 'B-' prefix
            
            # Check for preceding honorific
            honorific_before, actual_start = should_include_preceding_honorific(tokens, i)
            
            # Start building the new entity
            entity_text = token
            if honorific_before:
                entity_text = honorific_before + ' ' + token
            
            current_entity = {
                'text': entity_text,
                'type': entity_type,
                'start_idx': actual_start,
                'end_idx': i
            }
        
        # Check if this is inside an entity
        elif label.startswith('I-') and current_entity:
            # Only append if entity type matches
            if label[2:] == current_entity['type']:
                current_entity['text'] += ' ' + token
                current_entity['end_idx'] = i
            else:
                # If entity type doesn't match, finish current entity and start new one
                combined_entities.append(current_entity)
                entity_type = label[2:]
                
                # Check for preceding honorific for the new entity
                honorific_before, actual_start = should_include_preceding_honorific(tokens, i)
                entity_text = token
                if honorific_before:
                    entity_text = honorific_before + ' ' + token
                
                current_entity = {
                    'text': entity_text,
                    'type': entity_type,
                    'start_idx': actual_start,
                    'end_idx': i
                }
        
        # If it's an "O" (outside) tag
        elif label == 'O':
            # If we were building an entity, check for after-honorifics before finalizing
            if current_entity:
                # Look ahead for after-honorifics
                honorific_after, honorific_length = find_after_honorific_sequence(tokens, i)
                
                if honorific_after:
                    # Include the after-honorific in the entity
                    current_entity['text'] += ' ' + honorific_after
                    current_entity['end_idx'] = i + honorific_length - 1
                    # Skip the honorific tokens
                    i += honorific_length - 1
                
                combined_entities.append(current_entity)
                current_entity = None
        
        i += 1
    
    # Don't forget the last entity if we were building one
    if current_entity:
        # Check for trailing after-honorifics
        if current_entity['end_idx'] + 1 < len(tokens):
            honorific_after, honorific_length = find_after_honorific_sequence(
                tokens, current_entity['end_idx'] + 1
            )
            if honorific_after:
                current_entity['text'] += ' ' + honorific_after
                current_entity['end_idx'] += honorific_length
        
        combined_entities.append(current_entity)
    
    return combined_entities

def find_regex_entities(tokens: List[str], labels: List[str], config: ArabicNERConfig = None) -> List[Dict]:
    """
    Use regex patterns to find entities that NER might have missed
    Now uses configurable patterns for easy modification!
    """
    # Rejoin tokens to work with regex
    text = ' '.join(tokens)
    
    # Build patterns from configuration
    regex_patterns = build_regex_patterns(config)
    
    regex_entities = []
    
    for pattern_info in regex_patterns:
        pattern = pattern_info['pattern']
        entity_type = pattern_info['type']
        priority = pattern_info['priority']
        
        for match in re.finditer(pattern, text):
            start_char = match.start()
            end_char = match.end()
            matched_text = match.group().strip()
            
            # Convert character positions to token positions
            start_token_idx = len(text[:start_char].split())
            end_token_idx = start_token_idx + len(matched_text.split()) - 1
            
            # Ensure indices are within bounds
            if start_token_idx < len(tokens) and end_token_idx < len(tokens):
                regex_entities.append({
                    'text': matched_text,
                    'type': entity_type,
                    'start_idx': start_token_idx,
                    'end_idx': end_token_idx,
                    'source': 'regex',
                    'priority': priority
                })
    
    return regex_entities


def merge_ner_and_regex_entities(ner_entities: List[Dict], regex_entities: List[Dict]) -> List[Dict]:
    """
    Merge NER entities with regex-found entities, handling overlaps intelligently
    """
    all_entities = []
    
    # Add NER entities with high priority
    for entity in ner_entities:
        entity['source'] = 'ner'
        entity['priority'] = 10  # NER gets high priority
        all_entities.append(entity)
    
    # Add regex entities
    all_entities.extend(regex_entities)
    
    # Sort by priority (higher first) and then by start position
    all_entities.sort(key=lambda x: (-x['priority'], x['start_idx']))
    
    # Remove overlapping entities (keep higher priority ones)
    final_entities = []
    
    for entity in all_entities:
        # Check for overlap with existing entities
        overlaps = False
        for existing in final_entities:
            # Check if ranges overlap
            if not (entity['end_idx'] < existing['start_idx'] or 
                   entity['start_idx'] > existing['end_idx']):
                overlaps = True
                break
        
        if not overlaps:
            final_entities.append(entity)
    
    # Sort final entities by position
    final_entities.sort(key=lambda x: x['start_idx'])
    
    return final_entities


def post_process_with_referable_titles(entities: List[Dict], original_text: str, config: ArabicNERConfig = None) -> List[Dict]:
    """
    Post-process entities to handle special referable titles and add metadata
    Now uses configurable titles for easy modification!
    """
    if config is None:
        config = ArabicNERConfig()
    
    processed_entities = []
    
    for entity in entities:
        # Check if entity text contains any special titles
        entity['is_special_title'] = False
        entity['title_type'] = None
        
        for title in config.SPECIAL_TITLES:
            if title in entity['text'] or entity['text'] in title:
                entity['is_special_title'] = True
                if any(prophet_title in title for prophet_title in config.PROPHET_TITLES):
                    entity['title_type'] = 'PROPHET'
                elif "الخليفة" in title:
                    entity['title_type'] = 'CALIPH'
                elif "أمير المؤمنين" in title:
                    entity['title_type'] = 'LEADER'
                elif "الصحابة" in title:
                    entity['title_type'] = 'COMPANIONS'
                break
        
        # Add honorific information using config
        all_honorifics = (config.AFTER_HONORIFICS + config.PROPHET_HONORIFICS + 
                         config.COMPANION_HONORIFICS + config.SCHOLAR_HONORIFICS)
        entity['has_honorific'] = any(honorific in entity['text'] for honorific in all_honorifics)
        
        processed_entities.append(entity)
    
    return processed_entities


# Complete pipeline for processing Arabic NER with honorifics and regex backup
def process_arabic_ner_complete(text: str, ner_model, config: ArabicNERConfig = None) -> List[Dict]:
    """
    Complete pipeline for processing Arabic NER with honorifics and regex fallback
    Now uses configurable patterns for easy modification!
    """
    if config is None:
        config = ArabicNERConfig()
    
    # Tokenize
    tokens = text.split()
    
    # Get NER labels
    labels = ner_model.predict_sentence(tokens)
    
    # Combine entities with honorific handling (from NER)
    ner_entities = combine_named_entities_with_honorifics(tokens, labels, config)
    
    # Find additional entities using regex patterns
    regex_entities = find_regex_entities(tokens, labels, config)
    
    # Merge NER and regex entities intelligently
    all_entities = merge_ner_and_regex_entities(ner_entities, regex_entities)
    
    # Post-process for special titles and metadata
    final_entities = post_process_with_referable_titles(all_entities, text, config)
    
    return final_entities


# ======================== EASY CUSTOMIZATION EXAMPLES ========================

def create_custom_config() -> ArabicNERConfig:
    """
    Example of how to create a custom configuration
    Just modify the lists to add/remove honorifics and patterns!
    """
    config = ArabicNERConfig()
    
    # Add more honorifics easily:
    config.AFTER_HONORIFICS.extend([
        "قدس سره",           # Sacred secret (for mystics)
        "نور الله ضريحه",    # May Allah illuminate his tomb
        "طيب الله ثراه",     # May Allah perfume his soil
    ])
    
    # Add more cities:
    config.CITIES.extend([
        "طيبة", "يثرب", "مكة المكرمة", "المدينة المنورة"
    ])
    
    # Add more before-honorifics:
    config.BEFORE_HONORIFICS.extend([
        "الأستاذ", "الدكتور", "الشيخة", "الأستاذة"
    ])
    
    return config


# ======================== TESTING AND DEMONSTRATION ========================

# Test with your example
if __name__ == "__main__":
    # Your example text
    text = "5742 حدثنا محمد بن محبوب حدثنا أبو عوانة عن قتادة عن أنس ح و قال لي خليفة حدثنا يزيد بن زريع حدثنا سعيد عن قتادة عن أنس رضي الله عنه أن رجلا جاء إلى النبي صلى الله عليه وسلم يوم الجمعة وهو يخطب بالمدينة فقال قحط المطر فاستسق ربك فنظر إلى السماء وما نرى من سحاب فاستسقى فنشأ السحاب بعضه إلى بعض ثم مطروا حتى سالت مثاعب المدينة فما زالت إلى الجمعة المقبلة ما تقلع ثم قام ذلك الرجل أو غيره والنبي صلى الله عليه وسلم يخطب فقال غرقنا فادع ربك يحبسها عنا فضحك ثم قال اللهم حوالينا ولا علينا مرتين أو ثلاثا فجعل السحاب يتصدع عن المدينة يمينا وشمالا يمطر ما حوالينا ولا يمطر منها شيء يريهم الله كرامة نبيه صلى الله عليه وسلم وإجابة دعوته"
    
    # Simulate NER model for testing
    class MockNERModel:
        def predict_sentence(self, tokens):
            # Mock labels - in reality, your NER model would provide these
            labels = ['O'] * len(tokens)
            
            # Mock some person entities (incomplete to test regex backup)
            person_positions = {
                'محمد': 'B-PERS',
                'بن': 'I-PERS', 
                'محبوب': 'I-PERS',
                'أبو': 'B-PERS',
                'عوانة': 'I-PERS',
                'قتادة': 'B-PERS',
                'أنس': 'B-PERS',
                'خليفة': 'B-PERS',
                'يزيد': 'B-PERS',
                'زريع': 'I-PERS',
                'سعيد': 'B-PERS'
            }
            
            # Apply mock labels
            for i, token in enumerate(tokens):
                if token in person_positions:
                    labels[i] = person_positions[token]
                elif token == 'المدينة':
                    labels[i] = 'B-LOC'
            
            return labels
    
    # Test with default configuration
    print("=== Testing with Default Configuration ===\n")
    mock_ner = MockNERModel()
    default_entities = process_arabic_ner_complete(text, mock_ner)
    
    print(f"Found {len(default_entities)} entities:")
    for entity in default_entities:
        print(f"   {entity}")
    
    # Test with custom configuration
    print(f"\n=== Testing with Custom Configuration ===\n")
    custom_config = create_custom_config()
    custom_entities = process_arabic_ner_complete(text, mock_ner, custom_config)
    
    print(f"Found {len(custom_entities)} entities with custom config:")
    for entity in custom_entities:
        print(f"   {entity}")
    
    print(f"\n=== Easy Modification Examples ===")
    print("To add new honorifics, simply modify the ArabicNERConfig class:")
    print("1. Add to AFTER_HONORIFICS: config.AFTER_HONORIFICS.append('new_honorific')")
    print("2. Add to CITIES: config.CITIES.extend(['new_city1', 'new_city2'])")
    print("3. Add to BEFORE_HONORIFICS: config.BEFORE_HONORIFICS.append('new_title')")
    print("4. The regex patterns will automatically use your new additions!")
    
    # Test the complete pipeline components separately
    print(f"\n=== Component Testing ===")
    
    # Test original function
    tokens = text.split()
    labels = mock_ner.predict_sentence(tokens)
    
    print("\n1. Original NER entities:")
    ner_only = combine_named_entities_with_honorifics(tokens, labels)
    for entity in ner_only:
        print(f"   {entity}")
    
    print(f"\n2. Regex-found entities:")
    regex_only = find_regex_entities(tokens, labels)
    for entity in regex_only:
        print(f"   {entity}")
    
    print(f"\n3. Complete pipeline results:")
    complete_entities = process_arabic_ner_complete(text, mock_ner)
    for entity in complete_entities:
        print(f"   {entity}")
    
    print(f"\n=== Summary ===")
    print(f"NER only found: {len(ner_only)} entities")
    print(f"Regex found: {len(regex_only)} additional entities")  
    print(f"Complete pipeline: {len(complete_entities)} total entities")
    
    # Show special religious references found
    religious_refs = [e for e in complete_entities if e.get('type') in ['PROPHET', 'DEITY']]
    print(f"\nReligious references found: {len(religious_refs)}")
    for ref in religious_refs:
        print(f"   - {ref['text']} ({ref['type']})")
    
    # Show entities with honorifics
    honorific_entities = [e for e in complete_entities if e.get('has_honorific', False)]
    print(f"\nEntities with honorifics found: {len(honorific_entities)}")
    for entity in honorific_entities:
        print(f"   - {entity['text']} ({entity['type']})")