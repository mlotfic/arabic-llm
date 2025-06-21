# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 22:55:20 2025

@author: m
"""
from QuranDetectorAnnotater import qMatcherAnnotater, term

# Simple Quranic Text Formatter
# Find Quranic verses in text and format them properly

import re


def format_verse(match):
    """Convert a single match to formatted verse string."""
    verses = match.get('verses', [])
    if not verses:
        return ""
    
    verse_text = ' ۞ '.join(verses)
    verse_num = match['aya_start']
    surah_name = match['aya_name']
    
    return f"﴾{verse_text}﴿ - «Quran:{surah_name}:{verse_num}»"


def replace_verses_in_text(original_text, matches):
    """Replace Quranic verses in text with formatted versions."""
    if not matches:
        return original_text
    
    result = original_text
    
    # Create formatted versions of all verses
    formatted_verses = []
    for match in matches:
        formatted = format_verse(match)
        if formatted:
            formatted_verses.append(formatted)
    
    if not formatted_verses:
        return original_text
    
    # Look for the Quranic text block to replace
    # Pattern: text between ﴿ and the end (could be incomplete)
    quranic_pattern = r'﴿[^﴾]*[﴾…]*'
    
    # Find Quranic blocks in the text
    quranic_blocks = re.findall(quranic_pattern, result)
    
    # Replace the first/longest block with all formatted verses
    if quranic_blocks:
        # Sort by length (longest first) to get the most complete block
        longest_block = max(quranic_blocks, key=len)
        
        # Join all formatted verses with a space
        replacement = ' '.join(formatted_verses)
        
        # Replace the block
        result = result.replace(longest_block, replacement, 1)
    
    return result


def process_quranic_text(text, matcher):
    """
    Main function: Find verses and create formatted output.
    
    Returns:
        - original_text: The input text
        - modified_text: Text with verses replaced
        - verse_list: List of formatted verses found
    """
    print("🔍 Searching for Quranic verses...")
    
    # Find verses
    matches = matcher.matchAll(text)
    
    if not matches:
        print("❌ No Quranic verses found")
        return text, text, []
    
    print(f"✅ Found {len(matches)} verse(s)")
    
    # Create formatted verse list
    verse_list = []
    for match in matches:
        formatted = format_verse(match)
        if formatted:
            verse_list.append(formatted)
    
    # Replace verses in original text
    modified_text = replace_verses_in_text(text, matches)
    
    return text, modified_text, verse_list


def display_results(original_text, modified_text, verse_list):
    """Display the results in a clean, readable format."""
    
    print("\n" + "="*60)
    print("📜 ORIGINAL TEXT")
    print("="*60)
    print(original_text)
    
    print("\n" + "="*60)
    print("📋 VERSES FOUND")
    print("="*60)
    if verse_list:
        for i, verse in enumerate(verse_list, 1):
            print(f"{i}. {verse}")
    else:
        print("No verses found")
    
    print("\n" + "="*60)
    print("✨ TEXT WITH FORMATTED VERSES")
    print("="*60)
    print(modified_text)
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Verses found: {len(verse_list)}")
    print(f"Original length: {len(original_text)} characters")
    print(f"Modified length: {len(modified_text)} characters")
    
    if original_text != modified_text:
        print("✅ Text was successfully modified")
    else:
        print("⚠️  No changes made to text")


# Example usage
if __name__ == "__main__":
    # You need to have qMatcherAnnotater imported/available
    qAn = qMatcherAnnotater()
    
    # Sample text
    sample_text = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"
    
    print("🚀 Quranic Text Formatter")
    print("=" * 60)
    
    # Uncomment these lines when you have qMatcherAnnotater available:
    original, modified, verses = process_quranic_text(sample_text, qAn)
    display_results(original, modified, verses)
    
    # For demonstration without the matcher:
    print("Sample text:")
    print(sample_text)
    print("\nTo use this tool:")
    print("1. Import/initialize qMatcherAnnotater as 'qAn'")
    print("2. Call: original, modified, verses = process_quranic_text(your_text, qAn)")
    print("3. Call: display_results(original, modified, verses)")


# Quick usage function
def quick_format(text, matcher):
    """One-line function to get formatted text."""
    _, modified, _ = process_quranic_text(text, matcher)
    return modified