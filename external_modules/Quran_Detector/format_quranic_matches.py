# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 21:51:54 2025

@author: m
"""
from QuranDetectorAnnotater import qMatcherAnnotater,term

# Quranic Text Matcher and Formatter
# This script demonstrates how to use qMatcherAnnotater to find Quranic verses in text
# and format them in a readable way with proper Arabic ornaments

def format_quranic_matches(matches):
    """
    Format Quranic verse matches into a standardized display format.
    
    Args:
        matches (list): List of match dictionaries from qMatcherAnnotater.matchAll()
                       Each match contains: aya_name, verses, errors, startInText, 
                       endInText, aya_start, aya_end
    
    Returns:
        list: Formatted strings in the pattern: ﴾<verse_text>﴿ - «Quran:<sura>:<verse>»
    
    Example:
        ﴾الذين يحملون العرش ومن حوله يسبحون بحمد ربهم﴿ - «Quran:غافر:7»
    """
    formatted = []
    
    for match in matches:
        verses = match.get('verses', [])
        if not verses:
            continue  # Skip empty matches
        
        # Join multiple verse fragments with Arabic separator
        aya_text = ' ۞ '.join(verses)
        
        # Build verse reference (handle single verse vs verse range)
        if match['aya_start'] != match['aya_end']:
            aya_ref = f"{match['aya_start']}:{match['aya_end']}"
        else:
            aya_ref = str(match['aya_start'])
        
        # Format with Arabic ornamental brackets and reference
        result = f"﴾{aya_text}﴿ - «Quran:{match['aya_name']}:{aya_ref}»"
        formatted.append(result)
    
    return formatted


def print_quranic_matches(matches):
    """
    Print formatted Quranic matches in a clean, readable way.
    
    Args:
        matches (list): List of match dictionaries from qMatcherAnnotater.matchAll()
    """
    formatted = format_quranic_matches(matches)
    
    if not formatted:
        print("No Quranic verses found in the text.")
        return
    
    print(f"Found {len(formatted)} Quranic verse(s):")
    print("-" * 50)
    
    for i, line in enumerate(formatted, 1):
        print(f"{i}. {line}")


# Example usage
if __name__ == "__main__":
    # Initialize the Quranic matcher
    qAn = qMatcherAnnotater()
    
    # Sample Arabic text containing Quranic verses
    txt = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"
    
    print("Processing text for Quranic verses...")
    
    # Find all Quranic matches using default parameters
    vs = qAn.matchAll(txt)
    
    # Display results
    print_quranic_matches(vs)
    
    # Alternative: Get formatted list for further processing
    formatted_verses = format_quranic_matches(vs)
    
    print("\nFormatted verses list:")
    for verse in formatted_verses:
        print(f"  {verse}")


# Suggestions for improvement:
# 1. Add error handling for malformed match data
# 2. Consider adding option to include error information in output
# 3. Add support for different output formats (JSON, XML, etc.)
# 4. Implement logging for debugging match quality
# 5. Add configuration options for different Arabic ornaments/separators
# 6. Consider adding verse context (surrounding words) in output
