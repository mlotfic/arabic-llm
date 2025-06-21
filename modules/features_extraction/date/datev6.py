# -*- coding: utf-8 -*-
import sys
import codecs

from pprint import pprint
"""
Created on Thu Jun 12 15:32:35 2025

@author: m
"""

# -*- coding: utf-8 -*-
import sys
import codecs

from pprint import pprint

from dateparser.search import search_dates
from dateparser import DateDataParser
from dateparser.conf import settings


"""
Created on Thu Jun 12 15:32:35 2025

@author: m
"""

# Organized Date Pattern Recognition with Priority Order
# Patterns are ordered from most specific to least specific to avoid conflicts

import re

def gregorian_year_to_hijri_year(g_year: int) -> int:
    return int((g_year - 622) / 0.97)

def hijri_year_to_gregorian_year(hijri_year: int) -> int:
    # Approximate conversion formula
    return int(hijri_year * 0.97 + 622)

def remove_date_duplicates(dict_list):
    """
    Remove duplicate dictionaries where date ranges are within ±1 day of each other.
    Keeps the first occurrence and removes subsequent duplicates.
    """
    if not dict_list:
        return []
    
    result = []
    
    for current_dict in dict_list:
        is_duplicate = False
        
        for existing_dict in result:
            # Helper function to safely convert to int, return None if conversion fails
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
            
            # Check if all date fields are within ±1 day of each other
            # Skip comparison if any value is None
            hijri_end_match = (
                current_hijri_end is not None and existing_hijri_end is not None and
                abs(current_hijri_end - existing_hijri_end) <= 1
            )
            hijri_start_match = (
                current_hijri_start is not None and existing_hijri_start is not None and
                abs(current_hijri_start - existing_hijri_start) <= 1
            )
            gregorian_start_match = (
                current_gregorian_start is not None and existing_gregorian_start is not None and
                abs(current_gregorian_start - existing_gregorian_start) <= 1
            )
            gregorian_end_match = (
                current_gregorian_end is not None and existing_gregorian_end is not None and
                abs(current_gregorian_end - existing_gregorian_end) <= 1
            )
            
            # If all conditions are met, it's a duplicate
            if hijri_end_match and hijri_start_match and gregorian_start_match and gregorian_end_match:
                is_duplicate = True
                break
        
        # Only add if it's not a duplicate
        if not is_duplicate:
            result.append(current_dict)
    
    return result

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


# Example usage
Hijri_keywords = ["هـ","هــ","هـــ","ه","سنة هجرية","هجري","هجرية","السنة الهجرية","بالهجري","بالهجرية","للهجرة","AH","After Hijra"]

# Create the pattern
pattern = keywords_to_regex(Hijri_keywords)
hijri_pattern = rf'\b(?P<hijri_year>\d{{1,4}})\s*(?P<hijri_indicator>{pattern})\b'


# Example usage
gregorian_keywords = ["م", "ميلادي", "ميلادية", "AD", "Anno Domini", "CE", "Common Era", "السنة الميلادية", "بالميلادي", "بالميلادية", "المسيحي", "المسيحية", "الإفرنجي", "الإفرنجية", "الغربي", "الغربية"]

# Create the pattern
pattern = keywords_to_regex(gregorian_keywords)
gregorian_pattern = rf'\b(?P<gregorian_year>\d{{1,4}})\s*(?P<gregorian_indicator>{pattern})\b'

# Example usage
year_keywords = ["سنة", "عام", "في عام", "في سنة", "خلال عام", "خلال سنة", "في السنة", "خلال السنة", "في العام", "خلال العام", "في هذه السنة", "خلال هذه السنة", "في هذا العام", "خلال هذا العام"]

# Create the pattern
pattern = keywords_to_regex(year_keywords)
year_pattern = rf"(?P<year_indicator>{pattern})"

# Define patterns in priority order (most specific first)
patterns = [
    # 1. COMPLEX RANGE PATTERNS (highest priority)
    # Example: "من 1440 هـ إلى 2023 م"
    {
        "pattern": rf'\b(من|منذ)\s+(?P<hijri_group>{hijri_pattern})\s+(إلى|الى|حتى|وحتى|إلي|الي)\s+(?P<gregorian_group>{gregorian_pattern})\b',
        "name": "from_to_hijri_gregorian",
        "description": "Matches a range from Hijri to Gregorian with 'من' and 'إلى'.",
        "example": "من 1440 هـ إلى 2023 م",
        "priority": 1,
        "match_type": "range",
        "hijri_start":  3,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": 7
    },
    # Example: "من 2020 م إلى 1442 هـ"
    {
        "pattern": rf'(من|منذ)\s+(?P<gregorian_group>{gregorian_pattern})\s+(إلى|الى|حتى|وحتى|إلي|الي)\s+(?P<hijri_group>{hijri_pattern})',
        "name": "from_to_gregorian_hijri",
        "description": "Matches a range from Gregorian to Hijri with 'من' and 'إلى'.",
        "example": "من 2020 م إلى 1442 هـ",
        "priority": 1,
        "match_type": "range",
        "hijri_start": None,    
        "gregorian_start": 3,
        "hijri_end": 7,
        "gregorian_end": None
    },

    # 2. MIXED PATTERNS (parenthetical, slash, etc.)
    {
        "pattern": rf'(?P<hijri_group>{hijri_pattern})\s*[\(\[]\s*(?P<gregorian_group>{gregorian_pattern})\s*[\)\]]',
        "name": "parenthetical_hijri_gregorian",
        "description": "Matches Hijri in parentheses with Gregorian.",
        "example": "1445 هـ (2023 م)",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 2,
        "gregorian_start": 5,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(?P<hijri_group>{hijri_pattern})\s*/\s*(?P<gregorian_group>{gregorian_pattern})',
        "name": "slash_hijri_gregorian",
        "description": "Matches Hijri and Gregorian separated by a slash.",
        "example": "1445 هـ/2023 م",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 2,
        "gregorian_start": 5,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(?P<gregorian_group>{gregorian_pattern})\s*[\(\[]\s*(?P<hijri_group>{hijri_pattern})\s*[\)\]]',
        "name": "parenthetical_gregorian_hijri",
        "description": "Matches Gregorian in parentheses with Hijri.",
        "example": "2023 م (1445 هـ)",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 5,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(?P<gregorian_group>{gregorian_pattern})\s*/\s*(?P<hijri_group>{hijri_pattern})',
        "name": "slash_gregorian_hijri",
        "description": "Matches Gregorian and Hijri separated by a slash.",
        "example": "2023 م/1445 هـ",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 5,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(?P<hijri_group>{hijri_pattern})\s*(-|\s*|\\|\(|\[)\s*(?P<gregorian_group>{gregorian_pattern})(\)|\])?',
        "name": "mixed_hijri_gregorian",
        "description": "Matches mixed Hijri and Gregorian with various separators.",
        "example": "1445 هـ - 2023 م",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 1,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": r'(\d{1,4})\s*/\s*(\d{1,4})\s*(هـ/م)',
        "name": "mixed_hijri_gregorian1",
        "description": "Matches mixed Hijri and Gregorian with various separators.",
        "example": "1445/2023 هـ/م",
        "priority": 2,
        "match_type": "mixed",
        "hijri_start": 2,
        "gregorian_start": 6,
        "hijri_end": None,
        "gregorian_end": None
    },

    # 3. RANGE PATTERNS (same calendar system)
    {
        "pattern": rf'(\d{{1,4}})\s*(-|إلى|الى|حتى|وحتى|إلي|الي|\\)\s*(?P<hijri_group>{hijri_pattern})',
        "name": "hijri_range",
        "description": "Matches a range of Hijri years.",
        "example": "1440 - 1445 هـ",
        "priority": 3,
        "match_type": "range",
        "hijri_start": 1,
        "gregorian_start": None,
        "hijri_end": 4,
        "gregorian_end": None                
    },
    {
        "pattern": rf'(\d{{1,4}})\s*(-|إلى|الى|حتى|وحتى|إلي|الي|\\)\s*(?P<gregorian_group>{gregorian_pattern})',
        "name": "gregorian_range",
        "description": "Matches a range of Gregorian years.",
        "example": "2020 - 2023 م",
        "priority": 3,
        "match_type": "range",
        "hijri_start": None,    
        "gregorian_start": 1,
        "hijri_end": None,
        "gregorian_end": 4
    },
    {
        "pattern": rf'(من|منذ)\s+(\d{{1,4}})\s+(إلى|الى|حتى|وحتى|إلي|الي)\s+(?P<hijri_group>{hijri_pattern})',
        "name": "from_to_hijri",
        "description": "Matches a Hijri year range with 'من' and 'إلى'.",
        "example": "من 1440 إلى 1445 هـ",
        "priority": 3,
        "match_type": "range",
        "hijri_start": 2,
        "gregorian_start": None,
        "hijri_end": 5,
        "gregorian_end": None
    },
    {
        "pattern": rf'(من|منذ)\s+(\d{{1,4}})\s+(إلى|الى|حتى|وحتى|إلي|الي)\s+(?P<gregorian_group>{gregorian_pattern})',
        "name": "from_to_gregorian",
        "description": "Matches a Gregorian year range with 'من' and 'إلى'.",
        "example": "من 2020 إلى 2023 م",
        "priority": 3,
        "match_type": "range",
        "hijri_start": None,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": 5
    },

    # 5. APPROXIMATE PATTERNS
    {
        "pattern": rf'(حوالي|نحو|تقريباً|تقريبا|قريب من|حول|في حدود|قرابة)\s+(?P<hijri_group>{hijri_pattern})',
        "name": "approximate_hijri",
        "description": "Matches approximate Hijri years.",
        "example": "حوالي 1440 هـ",
        "priority": 5,
        "match_type": "year",
        "hijri_start": 3,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(حوالي|نحو|تقريباً|تقريبا|قريب من|حول|في حدود|قرابة)\s+(?P<gregorian_group>{gregorian_pattern})',
        "name": "approximate_gregorian",
        "description": "Matches approximate Gregorian years.",
        "example": "حوالي 2020 م",
        "priority": 5,
        "match_type": "year",
        "hijri_start": None,
        "gregorian_start": 3,
        "hijri_end": None,
        "gregorian_end": None  # Added missing value
    },

    # 6. BEFORE/AFTER PATTERNS
    {
        "pattern": rf'(قبل|بعد|منذ|حتى)\s+(?P<hijri_group>{hijri_pattern})',
        "name": "before_after_hijri",
        "description": "Matches Hijri years with 'قبل' or 'بعد'.",
        "example": "قبل 1445 هـ",
        "priority": 6,
        "match_type": "year",
        "hijri_start": 3,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(قبل|بعد|منذ|حتى)\s+(?P<gregorian_group>{gregorian_pattern})',
        "name": "before_after_gregorian",
        "description": "Matches Gregorian years with 'قبل' or 'بعد'.",
        "example": "بعد 2020 م",
        "priority": 6,
        "match_type": "year",
        "hijri_start": None,
        "gregorian_start": 3,
        "hijri_end": None,
        "gregorian_end": None
    },

    # 7. FLEXIBLE YEAR PATTERNS
    {
        "pattern": rf'({year_pattern})\s+(?P<hijri_group>{hijri_pattern})',
        "name": "year_flexible_hijri",
        "description": "Matches Hijri years with flexible year markers.",
        "example": "سنة 1445 هـ",
        "priority": 7,
        "match_type": "year",
        "hijri_start": 4,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'({year_pattern})\s+(?P<gregorian_group>{gregorian_pattern})',
        "name": "year_flexible_gregorian",
        "description": "Matches Gregorian years with flexible year markers.",
        "example": "عام 2023 م",
        "priority": 7,
        "match_type": "year",
        "hijri_start": None,
        "gregorian_start": 4,
        "hijri_end": None,
        "gregorian_end": None
    },

    # 8. BASIC SINGLE DATE PATTERNS (lowest priority)
    {
        "pattern": rf'(?P<hijri_group>{hijri_pattern})',
        "name": "hijri",
        "description": "Matches single Hijri years.",
        "example": "1445 هـ",
        "priority": 8,
        "match_type": "year",
        "hijri_start": 2,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": rf'(?P<gregorian_group>{gregorian_pattern})',
        "name": "gregorian",
        "description": "Matches single Gregorian years.",
        "example": "2023 م",
        "priority": 8,
        "match_type": "year",
        "hijri_start": None,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },

    # 9. FLEXIBLE YEAR WITHOUT EXPLICIT MARKERS (lowest priority)
    {             
        "pattern": rf'({year_pattern})\s+(\d{{1,4}})',
        "name": "year_flexible",
        "description": "Matches years without explicit markers.",
        "example": "سنة 1445",
        "priority": 9,
        "match_type": "year",
        "hijri_start": 3,
        "gregorian_start": None,    
        "hijri_end": None,
        "gregorian_end": None
    }
]

CENTURY_PATTERNS = [
    # 4. CENTURY PATTERNS
    {
        "pattern": r'(القرن\s+)?(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الحادي عشر|الثاني عشر|الثالث عشر|الرابع عشر|الخامس عشر)\s+(الهجري|هـ|ه|الهجرية)',
        "name": "ordinal_century_hijri",
        "description": "Matches ordinal Hijri centuries.",
        "example": "القرن الثالث الهجري",
        "priority": 4,
        "match_type": "century",
        "hijri_start": 2,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None 
    },
    {
        "pattern": r"(القرن\s+)?(الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|الحادي\s+عشر|الثاني\s+عشر|الثالث\s+عشر|الرابع\s+عشر|الخامس\s+عشر|السادس\s+عشر|السابع\s+عشر|الثامن\s+عشر|التاسع\s+عشر|العشرون)\s+(الميلادي|م|المسيحي|الإفرنجي|الغربي)",
        "name": "ordinal_century_gregorian",
        "description": "Matches ordinal Gregorian centuries.",
        "example": "القرن السابع عشر الميلادي",
        "priority": 10,
        "match_type": "century",
        "hijri_start": None,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": r'(القرن\s+)?(\d{1,2})\s*(الهجري|هـ|ه|الهجرية)',
        "name": "century_hijri",
        "description": "Matches numeric Hijri centuries.",
        "example": "القرن 3 الهجري",
        "priority": 10,
        "match_type": "century",
        "hijri_start": 2,
        "gregorian_start": None,
        "hijri_end": None,
        "gregorian_end": None
    },
    {
        "pattern": r'(القرن\s+)?(\d{1,2})\s*(الميلادي|م|المسيحي|الإفرنجي|الغربي)',
        "name": "century_gregorian",
        "description": "Matches numeric Gregorian centuries.",
        "example": "القرن 17 الميلادي",
        "priority": 10,
        "match_type": "century",
        "hijri_start": None,
        "gregorian_start": 2,
        "hijri_end": None,
        "gregorian_end": None
    },
]
         

# r'((?P<year_indicator>خلال\s*هذه\s*السنة|خلال\s*هذا\s*العام|في\s*هذه\s*السنة|في\s*هذا\s*العام|خلال\s*السنة|خلال\s*العام|خلال\s*عام|خلال\s*سنة|في\s*السنة|في\s*العام|في\s*عام|في\s*سنة|سنة|عام))\s+(\d{1,4})'


# for i, d in enumerate(patterns):
#     print(i, d.get("name"))


# # Find index where name == "year_flexible"
# index = next((i for i, d in enumerate(patterns) if d.get("name") == "mixed_hijri_gregorian1"), -1)


# compiled = re.compile(patterns[index]['pattern'], flags=re.IGNORECASE | re.UNICODE)
# remaining_text = patterns[index]["example"]

# remaining_text = "من 1440 هـ إلى 2023 م. في عام 2020 م، حدث شيء مهم. حوالي 1445 هـ كان عامًا مميزًا. "

# matches = list(compiled.finditer(remaining_text))

# for test in patterns:
#     print(test['pattern'])
#     print(test['name'], test["example"])
#     match = re.search(test["pattern"], test["example"])
#     if match:
#         # Safely extract groups with bounds checking
#         groups = match.groups()
#         max_groups = len(groups)
#         # Debug output (consider removing in production)
#         print(f"Pattern: {test.get('name', 'Unknown')}")
#         print(f"Full match: {match.group(0)}")
#         for i in range(1, max_groups + 1):  # Show up to 5 groups safely
#             try:
#                 group_val = match.group(i)
#                 print(f"Group {i}: {group_val}")
#             except IndexError:
#                 print(f"Group {i}: N/A")
#         print("---")
    
    
    
    
#     assert match is not None, f"[{test['name']}] Pattern failed to match: {test['example']}"
#     print(f"[{test['name']}] Passed ✔")
#     if match:
#         print(" -------------- ", )
#         pprint(match.groupdict(), indent = 4)


class DatePatternMatcher:
    def __init__(self, patterns=patterns):
        """
        Initialize the matcher with predefined patterns.
        If no patterns are provided, use the default patterns.
        """
        # Use global patterns if none provided
        if patterns is None:
            self.patterns = globals()['patterns']
        else:
            self.patterns = patterns
            
        # self.patterns = sorted(patterns, key=lambda x: x['priority'])
        self.compiled_patterns = [re.compile(p['pattern'], flags=re.IGNORECASE | re.UNICODE) for p in self.patterns]
    
    def match(self, text):
        """
        Match the text against all patterns in priority order.
        
        Args:
            text: Input text to match
        
        Returns:
            tuple: (remaining_text, list_of_matched_patterns)
        """
        if not text or text.strip() == '':
            return text, []
        
        remaining_text = text
        date_matches = []
        
        # Iterate over patterns and compiled patterns together
        patterns_to_use = []
        
        if hasattr(self, 'patterns') and hasattr(self, 'compiled_patterns'):
            # Use both patterns (metadata) and compiled_patterns (compiled regexes)
            patterns_to_use = list(zip(self.patterns, self.compiled_patterns))
        elif hasattr(self, 'compiled_patterns'):
            # Only compiled patterns available, create minimal metadata
            for i, compiled in enumerate(self.compiled_patterns):
                pattern_info = {
                    'name': f'Pattern_{i}',
                    'match_type': 'unknown',
                    'hijri_start': None,
                    'gregorian_start': None,
                    'hijri_end': None,
                    'gregorian_end': None
                }
                patterns_to_use.append((pattern_info, compiled))
        
        for pattern, compiled in patterns_to_use:
            matches = list(compiled.finditer(remaining_text))
            
            if not matches:
                continue
                
            for match in matches:
                try:
                    # print(f"Using pattern: {compiled.pattern}")
                    
                    # Safely extract groups with bounds checking
                    groups = match.groups()
                    max_groups = len(groups)
                    
                    # Extract relevant groups based on pattern type with safe indexing
                    hijri_start = None
                    gregorian_start = None  
                    hijri_end = None
                    gregorian_end = None
                    
                    # Check if group indices exist and are within bounds
                    if (pattern.get('hijri_start') is not None and 
                        pattern['hijri_start'] > 0 and 
                        pattern['hijri_start'] <= max_groups):
                        hijri_start = match.group(pattern['hijri_start'])
                        
                    if (pattern.get('gregorian_start') is not None and 
                        pattern['gregorian_start'] > 0 and 
                        pattern['gregorian_start'] <= max_groups):
                        gregorian_start = match.group(pattern['gregorian_start'])
                        
                    if (pattern.get('hijri_end') is not None and 
                        pattern['hijri_end'] > 0 and 
                        pattern['hijri_end'] <= max_groups):
                        hijri_end = match.group(pattern['hijri_end'])
                        
                    if (pattern.get('gregorian_end') is not None and 
                        pattern['gregorian_end'] > 0 and 
                        pattern['gregorian_end'] <= max_groups):
                        gregorian_end = match.group(pattern['gregorian_end'])
                    
                    # # Debug output (consider removing in production)
                    # print(f"Pattern: {pattern.get('name', 'Unknown')}")
                    # print(f"Full match: {match.group(0)}")
                    # for i in range(1, max_groups + 1):  # Show up to 5 groups safely
                    #     try:
                    #         group_val = match.group(i)
                    #         print(f"Group {i}: {group_val}")
                    #     except IndexError:
                    #         print(f"Group {i}: N/A")
                    # print("---")
                    
                    date_matches.append({
                        "match_type": pattern.get('match_type'),
                        "hijri_start": hijri_start,
                        "gregorian_start": gregorian_start,
                        "hijri_end": hijri_end,
                        "gregorian_end": gregorian_end,
                        "match": match.group(0),
                        "pattern_name": pattern.get('name'),
                        "start_pos": match.start(),
                        "end_pos": match.end()
                    })
                    
                    # Remove the matched text to avoid overlapping matches
                    remaining_text = remaining_text.replace(match.group(0), ' ', 1)
                    
                except IndexError as e:
                    print(f"Group index error for pattern {pattern.get('name', 'Unknown')}: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error for pattern {pattern.get('name', 'Unknown')}: {e}")
                    continue
        
        return remaining_text, date_matches
    
    def standard_date(self, text):
        remaining_text, date_matches = self.match(text)
        matches_results =[]
        if date_matches:
            for date_match in date_matches:
                # date_match["match_type"]
                if date_match["hijri_start"] and not date_match["gregorian_start"]:
                    date_match["gregorian_start"] = hijri_year_to_gregorian_year(int(date_match["hijri_start"]))
                    
                if  date_match["gregorian_start"] and not date_match["hijri_start"]:
                    date_match["hijri_start"] = gregorian_year_to_hijri_year(int(date_match["gregorian_start"]))

                if date_match["hijri_end"] and not date_match["gregorian_end"]:
                    date_match["gregorian_end"] = hijri_year_to_gregorian_year(int(date_match["hijri_end"]))
                    
                if  date_match["gregorian_end"] and not date_match["hijri_end"]:
                    date_match["hijri_end"] = gregorian_year_to_hijri_year(int(date_match["gregorian_end"]))
                    
                # Optional: Create formatted range strings if needed
                if date_match["hijri_start"] and date_match["hijri_end"]:
                    date_match["hijri_range_formatted"] = f'{date_match["hijri_start"]} - {date_match["hijri_end"]}'
                else:
                    date_match["hijri_range_formatted"] = ""
                 
                if date_match["gregorian_start"] and date_match["gregorian_end"]:
                    date_match["gregorian_range_formatted"] = f'{date_match["gregorian_start"]} - {date_match["gregorian_end"]}'
                else:
                    date_match["gregorian_range_formatted"] = ""
                   
                if date_match["hijri_end"] and date_match["gregorian_end"]:
                    date_match["mix_end"] = f'{date_match["gregorian_end"]} CA - {date_match["hijri_end"]} AH'
                else:
                    date_match["mix_end"] = ""
                    
                if date_match["hijri_start"] and date_match["gregorian_start"]:
                    date_match["mix_start"] = f'{date_match["gregorian_start"]} CA - {date_match["hijri_start"]} AH'
                else:
                    date_match["mix_start"] = ""                 
                
                # Add the processed match to results
                matches_results.append(date_match)
        
        # Remove duplicates based on date ranges
        matches_results = remove_date_duplicates(matches_results)
        
       
        for match_result in matches_results:
            for key in ['end_pos', 'match', 'match_type', 'pattern_name', 'start_pos']:
                match_result.pop(key, None)

        
        return remaining_text, matches_results
        
        
if __name__ == "__main__":
    matcher = DatePatternMatcher(patterns)    
    # Test texts
    test_texts = [
        "من 1440 هـ إلى 2023 م. في عام 2020 م، حدث شيء مهم. حوالي 1445 هـ كان عامًا مميزًا.",
        "في سنة 1445 هجرية الموافق 2023 ميلادية",
        "من القرن الثالث الهجري حتى الخامس",
        "حوالي 1440 هـ إلى 1445 هـ",
        "بعد سنة 2020 م وقبل 1442 هجري",
        "القرن الحادي عشر الهجري (السابع عشر الميلادي)",
        "1445/2023 هـ/م",
        "من 1440 هـ إلى 2023 م",
       "سنة 1445 هـ (2023 م) كانت سنة مهمة",
       "١٤٢٣هـ/٢٠٠٢م",
       "١٤٣٠ هـ - ٢٠٠٩ م",
       
       
       
       "١٤١١هـ",
       "٢٠٠٠م",
       "١٤١٩هـ - ١٩٩٩م",
  "(١٤١٦ هـ=١٩٩٦ م) - (١٤٢٢ هـ=٢٠٠٢ م)"     ,
  "١٤١٠ - ١٩٩٠",
  "١٤١١هـ/١٩٩٠م",
  "١٤٤٠ هـ - ٢٠١٩ م (الأولى لدار ابن حزم)",
"العدد الرابع، ربيع ثاني ١٣٩٣ هـ، مايو ١٩٧٣ م"  ,
"العدد الخامس والخمسون والسادس والخمسون، رجب- ذو الحجة ١٤٠٢هـ/١٩٨١",
"العدد الثاني غرة ذي الحجة عام ١٣٩٨هـ/١٩٧٨م",
"العدد الثاني غرة ذي الحجة عام ١٣٩٨ هـ/١٩٧٨ م",
"العدد الثالث، ذو الحجة ١٣٩٥هـ/ ديسمبر ١٩٧٥م",
"العدد الأول، رجب ١٣٩٤هـ/١٩٧٤م",
"١٤١٧ هـ -١٩٩٦ م",
"١٤٢٣ هـ/٢٠٠٢ م",
"العدد الحادي عشر بعد المائة، ١٤٢١هـ/٢٠٠٠م",
"العدد الثاني والستون - ربيع الآخر - جمادى الآخرة ١٤٠٤هـ/١٩٨٤م",
"(١٣٨٩ - ١٤٠٤ هـ) (١٩٦٩ - ١٩٨٤ م)",
"العدد الأول، رجب ١٣٩٢هـ/ أغسطس ١٩٧٢م",
"صفر، ربيع الأول ١٤٠٢هـ/١٩٨١م",
"١٤١٧هـ، ١٩٩٦م",
"١٤١١هـ١٩٩١م",
"١٤١١ - ١٩٩١",
"١٤٢٤هـ-٢٠٠٣م",
"١٤٢٠هـ١٩٩٩م",
"(١٤١١ - ١٤١٢ هـ) = (١٩٩٠ - ١٩٩٢ م)",
"١٣٨١ - ١٣٨٢ هـ = ١٩٦١ - ١٩٦٢ م",
"١٤٠٤هـ/١٩٨٤م",
"١٣٠٤ - ١٣٠٥ هـ",

"١٤٢٤هـ/٢٠٠٣م",
"١٤٢٤هـ / ٢٠٠٣م",
"العددان - مائة وثلاثة - مائة وأربعة - ١٤١٦/١٤١٧هـ",
"بالمطبعة الكبرى الأميرية، ببولاق مصر ١٣١٦ - ١٣١٨ هـ",
"ذو الحجة ١٣٩٧هـ نوفمبر - تشرين ثاني ١٩٧٧ م",
  "٧٢) رجب-ذو الحجة ١٤٠٦هـ."     ,
"العدد الأول، جمادى الأخرة ١٣٩٧هـ مايو - يونية ١٩٧٧ م"    ,
"(١٣٨٨ هـ = ١٩٦٨ م) - (١٣٨٩ هـ = ١٩٦٩ م)",
"(١٤٢٩ هـ - ١٤٣٢ هـ)",
"١٤٢٠هـ =٢٠٠٠م",
"العدد الثاني غرة ذي الحجة عام ١٣٩٨هـ",
"من ١٤٢٣ - ١٤٢٩ هـ (ينظر التفصيل بأول كل جزء)"
]    

    
    
    for text in test_texts:
        print(f"\nText: {text}")
        remaining_text, date_matches = matcher.match(text)
        remaining_text, matches_results = matcher.standard_date(text)
        
        for match in date_matches:                
            print("\nDetailed match information:")
            print("remaining_text :", remaining_text)
            pprint(match)
 
            

test_texts = [
    "The event is on 23/03/2023.",
    "The is 23/03/2023.",
    "التاريخ المتوقع هو ١ رمضان ١٤٤٥ هـ.",
    "Meeting scheduled for March 4th, 2022.",
]



for text in test_texts:
    print(f"\nText: {text}")
    dates = search_dates(
        text=text,
        languages=['ar', 'en'],
        settings={
            'PREFER_DAY_OF_MONTH': 'first',
            'DATE_ORDER': 'DMY'
        },
        add_detected_language=False,
        detect_languages_function=None
    )
    if dates:
        for raw_date, parsed_date in dates:
            print(f"🗓 Raw date string: {raw_date} --> Parsed: {parsed_date}")
    else:
        print("⚠️ No dates found.")