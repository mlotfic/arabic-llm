# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 21:33:02 2025

@author: m
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 18:37:54 2025

@author: m
"""

from typing import List, Dict, Set
import re

def combine_named_entities_with_honorifics(tokens: List[str], labels: List[str]) -> List[Dict]:
    """
    Combines tokens that are part of the same named entity, with special handling for Arabic honorifics.
    
    Args:
        tokens: List of tokens from the sentence
        labels: List of corresponding NER labels in BIO format
        
    Returns:
        List of dictionaries, each containing entity text, type and position
    """
    
    # Define honorifics that appear before names
    before_honorifics = [
        "الشيخ", "الإمام", "الحافظ", "القاضي", "السيد", "العلامة", 
        "الفقيه", "المحدث", "المجتهد", "المفسر", "الولي", "المقرئ"
    ]
    
    # Define honorifics that appear after names
    after_honorifics = [
        "صلى الله عليه وسلم",  # SAW
        "عليه السلام",        # AS
        "رضي الله عنه",       # RA (male)
        "رضي الله عنها",      # RA (female)
        "رضي الله عنهم",      # RA (plural)
        "رحمه الله",          # RH (male)
        "رحمها الله",         # RH (female)
        "رحمهم الله",         # RH (plural)
        "أجزل الله مثوبته",   # May Allah reward him
        "تقبله الله",         # May Allah accept him
        "غفر الله له"         # May Allah forgive him
    ]
    
    # Special referable titles (complete phrases)
    referable_titles = [
        "النبي صلى الله عليه وسلم",
        "الخليفة الراشد",
        "أمير المؤمنين",
        "رضي الله عن الصحابة أجمعين",
        "الإمام الفلاني رحمه الله",
        "الشيخ العلامة فلان",
        "قال فلان رحمه الله",
        "المجاهد في سبيل الله"
    ]
    
    def is_before_honorific(token: str) -> bool:
        """Check if token is a before-name honorific"""
        return token in before_honorifics
    
    def find_after_honorific_sequence(tokens: List[str], start_idx: int) -> tuple:
        """
        Find if there's an after-honorific sequence starting at start_idx
        Returns (honorific_text, length) or (None, 0) if not found
        """
        remaining_tokens = tokens[start_idx:]
        
        # Check each after_honorific pattern
        for honorific in after_honorifics:
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


def post_process_with_referable_titles(entities: List[Dict], original_text: str) -> List[Dict]:
    """
    Post-process entities to handle special referable titles that might span multiple entities
    """
    referable_titles = [
        "النبي صلى الله عليه وسلم",
        "الخليفة الراشد",
        "أمير المؤمنين",
        "رضي الله عن الصحابة أجمعين"
    ]
    
    # This is a simplified approach - you might want to implement more sophisticated
    # pattern matching based on your specific needs
    processed_entities = []
    
    for entity in entities:
        # Check if entity text contains any referable titles
        found_title = False
        for title in referable_titles:
            if title in entity['text']:
                # You could modify the entity type or add additional metadata here
                entity['is_referable_title'] = True
                found_title = True
                break
        
        if not found_title:
            entity['is_referable_title'] = False
            
        processed_entities.append(entity)
    
    return processed_entities


# Example usage with your data
def process_arabic_ner(text: str, ner_model):
    """
    Complete pipeline for processing Arabic NER with honorifics
    """
    # Tokenize
    tokens = text.split()
    
    # Get NER labels
    labels = ner_model.predict_sentence(tokens)
    
    # Combine entities with honorific handling
    entities = combine_named_entities_with_honorifics(tokens, labels)
    
    # Post-process for special titles
    entities = post_process_with_referable_titles(entities, text)
    
    return entities


# Test with your example
if __name__ == "__main__":
    # Your example text
    text = "5742 حدثنا محمد بن محبوب حدثنا أبو عوانة عن قتادة عن أنس ح و قال لي خليفة حدثنا يزيد بن زريع حدثنا سعيد عن قتادة عن أنس رضي الله عنه أن رجلا جاء إلى النبي صلى الله عليه وسلم يوم الجمعة وهو يخطب بالمدينة فقال قحط المطر فاستسق ربك فنظر إلى السماء وما نرى من سحاب فاستسقى فنشأ السحاب بعضه إلى بعض ثم مطروا حتى سالت مثاعب المدينة فما زالت إلى الجمعة المقبلة ما تقلع ثم قام ذلك الرجل أو غيره والنبي صلى الله عليه وسلم يخطب فقال غرقنا فادع ربك يحبسها عنا فضحك ثم قال اللهم حوالينا ولا علينا مرتين أو ثلاثا فجعل السحاب يتصدع عن المدينة يمينا وشمالا يمطر ما حوالينا ولا يمطر منها شيء يريهم الله كرامة نبيه صلى الله عليه وسلم وإجابة دعوته"
    
    النبي صلى الله عليه وسلم
نبيه صلى الله عليه وسلم    
    # Simulate your NER model results (you would use your actual model)
    tokens = text.split()
    
    # Mock labels for demonstration - replace with actual NER results
    mock_labels = ['O'] * len(tokens)
    # Add some mock labels for key entities
    person_indices = [2, 3, 4, 6, 7, 9, 11, 16, 18, 19, 20, 22, 24, 26]  # Person name positions
    for idx in person_indices:
        if idx < len(mock_labels):
            mock_labels[idx] = 'B-PERS' if idx not in [3, 4, 7, 19, 20] else 'I-PERS'
    
    # Test the function
    entities = combine_named_entities_with_honorifics(tokens, mock_labels)
    
    print("Enhanced entities with honorifics:")
    for entity in entities:
        print(f"- {entity}")