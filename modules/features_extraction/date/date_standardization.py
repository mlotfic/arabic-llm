# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 00:04:35 2025

@author: m
"""

# # Arabic-Indic digits to Western digits (safe - these are digits, not letters)
#     ord('0'): '٠',      # English 0 → Arabic-Indic 0
#     ord('1'): '١',      # English 1 → Arabic-Indic 1
#     ord('2'): '٢',      # English 2 → Arabic-Indic 2
#     ord('3'): '٣',      # English 3 → Arabic-Indic 3
#     ord('4'): '٤',      # English 4 → Arabic-Indic 4
#     ord('5'): '٥',      # English 5 → Arabic-Indic 5
#     ord('6'): '٦',      # English 6 → Arabic-Indic 6
#     ord('7'): '٧',      # English 7 → Arabic-Indic 7
#     ord('8'): '٨',      # English 8 → Arabic-Indic 8
#     ord('9'): '٩',      # English 9 → Arabic-Indic 9
    
#     # Persian (Extended Arabic-Indic) digits to Arabic-Indic digits
#     ord('۰'): '٠',  # Persian 0
#     ord('۱'): '١',  # Persian 1
#     ord('۲'): '٢',  # Persian 2
#     ord('۳'): '٣',  # Persian 3
#     ord('۴'): '٤',  # Persian 4
#     ord('۵'): '٥',  # Persian 5
#     ord('۶'): '٦',  # Persian 6
#     ord('۷'): '٧',  # Persian 7
#     ord('۸'): '٨',  # Persian 8
#     ord('۹'): '٩',  # Persian 9




# Arabic and Persian numeral conversion
arabic_digit_map = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}

# Persian/Farsi digits (Extended Arabic-Indic)
persian_digit_map = {'۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
                     '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'}

# Combined mapping for both Arabic and Persian digits
combined_digit_map = {**arabic_digit_map, **persian_digit_map}


def normalizeText(text):
    """
        normalizes all forms to alf to ا, converts ة to ه, and ى to ي.  It also converts new lines and tabs to a single space
        and seperates common punctuation marks from text
    """

    search = ["أ", "إ", "آ", "ٱ", "ة", "_", "-", "/", ".", "،", " و ", '"', "ـ", "'", "ى", "ی", "\\", '\n', '\t', '&quot;', '?', '؟', '!', 'ﷲ']
    replace = ["ا", "ا", "ا", "ا", "ه", " ", " ", "", "", "", " و", "", "", "", "ي", "ي", "", ' ', ' ', ' ', ' ? ', ' ؟ ',' ! ', 'الله']

    # search = ["آ", "إ", "أ", "ة"]
    # replace = ["ا", "ا", "ا", "ه"]

    for i in range(0, len(search)):
        text = text.replace(search[i], replace[i])
    return text

def padSymbols(inTxt, symbolList = ['۞', '۝']):
    for sym in symbolList:
        inTxt = inTxt.replace(sym, ' '+sym+' ')
    return inTxt


def removeTashkeel(text):
    # Removes Tashkeel from input text
    p_tashkeel = re.compile(r'[\u0616-\u061A\u064B-\u0652\u06D6-\u06ED\u08F0-\u08F3\uFC5E-\uFC63\u0670]')
    text = re.sub(p_tashkeel, "", text)
    return text



# using simple string replacement (no regex needed)
def normalize_arabic_digits(text):
    """Convert Arabic-Indic and Persian digits using simple string replacement"""
    for digit, western_digit in combined_digit_map.items():
        text = text.replace(digit, western_digit)
    return text


def clean_text(text: str) -> str:
    """
    Clean text by removing quotes, backslashes, tildes, and normalizing spaces and case.
    Args:
        text (str): Input text.
    Returns:
        str: Cleaned, lowercased text.
    """
    text = re.sub(r"[\'\"\\`~]", "", text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = normalize_arabic_digits(text)
    text = strip_tatweel(text)
    
    # Remove Tashkeel (diacritics)
   text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)

   # Replace different forms of Alef with bare Alef
   text = re.sub(r'[إأآا]', 'ا', text)

   # Replace Teh Marbuta with Heh
   text = re.sub(r'ة', 'ه', text)

   # Replace Yeh variants with dotless Yeh (e.g., Persian/Farsi Yeh to Arabic)
   text = re.sub(r'[يى]', 'ي', text)

   # Replace Kaf variants
   text = re.sub(r'ک', 'ك', text)
# Normalize Alef variants to ا
    text = re.sub(r'[إأآٱا]', 'ا', text)

    # Normalize Yeh variants (Persian/Urdu) to Arabic ي
    text = re.sub(r'[یئى]', 'ي', text)

    # Normalize Kaf variants to ك
    text = re.sub(r'[ک]', 'ك', text)

    # Normalize Heh variants (e.g. ة to ه)
    text = re.sub(r'[ةۀ]', 'ه', text)
    
    return text.lower()
    
def map_to_standard_arabic(text):
    mapping = {
        # Existing mappings
        'ک': 'ك',
        'ی': 'ي',
        'ى': 'ي',
        'ے': 'ي',
        'ې': 'ي',
        'ۀ': 'ه',
        'ة': 'ه',
        'ہ': 'ه',
        'ھ': 'ه',
        'أ': 'ا',
        'إ': 'ا',
        'آ': 'ا',
        'ٱ': 'ا',
        'پ': 'ب',
        'چ': 'ج',
        'ژ': 'ز',
        'ڤ': 'ف',
        'گ': 'ك',
        'غ': 'غ',  # leave as-is
        'ں': 'ن',
        'ڑ': 'ر',
        
        # Additional Alef variants
        'ٲ': 'ا',  # Alef with wavy hamza above (Kashmiri)
        'ٳ': 'ا',  # Alef with wavy hamza below (Kashmiri)
        
        # Additional Yeh variants
        'ئ': 'ي',  # Yeh with hamza above
        'ؠ': 'ي',  # Yeh with small v above
        'ۍ': 'ي',  # Yeh with tail (Pashto)
        'ۑ': 'ي',  # Yeh with three dots below
        'ۓ': 'ي',  # Yeh barree with hamza above (Urdu)
        
        # Additional Heh variants
        'ۃ': 'ه',  # Teh marbuta goal (Urdu)
        'ۂ': 'ه',  # Heh goal with hamza above (Urdu)
        
        # Additional Persian/Urdu letters
        'ڈ': 'د',  # Dal with dot below (Urdu)
        'ڊ': 'د',  # Dal with dot below and small tah (Sindhi)
        'ڏ': 'د',  # Dal with dot below and dot above (Sindhi)
        'ٹ': 'ت',  # Teh with ring (Urdu)
        'ٹھ': 'ت', # Teh with ring and small teh (compound)
        'ڙ': 'ر',  # Reh with small v below (Sindhi)
        'ړ': 'ر',  # Reh with ring (Pashto)
        'ڕ': 'ر',  # Reh with small v above (Kurdish)
        'ڇ': 'ج',  # Cheh with dot above (Sindhi)
        'ڃ': 'ج',  # Nyeh (Sindhi)
        'ٿ': 'ث',  # Theh with dot above (Sindhi)
        'ٺ': 'ت',  # Teh with dot above (Sindhi)
        'ٻ': 'ب',  # Beh with dot below (Sindhi)
        'ڀ': 'ب',  # Beh with small v below (Sindhi)
        'ڦ': 'ف',  # Feh with dot below (Sindhi)
        'ڡ': 'ف',  # Feh with dot moved below (Arabic)
        'ؤ': 'و',  # Waw with hamza above
        'ۄ': 'و',  # Waw with ring (Kashmiri)
        'ۆ': 'و',  # Waw with small v above (Kurdish)
        'ۇ': 'و',  # Waw with damma above (Uyghur)
        'ۈ': 'و',  # Waw with alef above (Uyghur)
        'ۉ': 'و',  # Waw with inverted small v above (Uyghur)
        'ۊ': 'و',  # Waw with two dots above (Uyghur)
        
        # Additional Noon variants
        'ڼ': 'ن',  # Noon with ring (Pashto)
        'ڻ': 'ن',  # Noon with three dots above (Sindhi)
        'ں': 'ن',  # Noon ghunna (Urdu) - already included
        
        # Additional Seen/Sheen variants
        'ښ': 'ش',  # Seen with dot below and dot above (Pashto)
        'ۺ': 'س',  # Seen with small tah and two dots (Balochi)
        
        # Additional Lam variants
        'ڵ': 'ل',  # Lam with small v above (Kurdish)
        'ڶ': 'ل',  # Lam with dot above (Sindhi)
        'ڷ': 'ل',  # Lam with three dots above (Sindhi)
        'ڸ': 'ل',  # Lam with three dots below (Sindhi)
        
        # Additional Kaf variants
        'ڪ': 'ك',  # Swash kaf (Sindhi)
        'ګ': 'ك',  # Gaf with ring (Pashto)
        'ڬ': 'ك',  # Gaf with two dots below (Sindhi)
        'ڭ': 'ك',  # Ng (Kazakh, Kyrgyz)
        'ڮ': 'ك',  # Ngoeh (Sindhi)
        
        # Additional Qaf variants
        'ۼ': 'ق',  # Qaf with dot above (Balochi)
        
        # Additional Jeem variants
        'ڄ': 'ج',  # Jeem with dot below (Sindhi)
        'ځ': 'ج',  # Hah with hamza above (Pashto)
        'څ': 'ج',  # Hah with three dots above (Pashto)
        
        # Zero-width characters (normalize to empty)
        '\u200C': '',  # Zero Width Non-Joiner
        '\u200D': '',  # Zero Width Joiner
        '\u200E': '',  # Left-to-Right Mark
        '\u200F': '',  # Right-to-Left Mark
        '\u202A': '',  # Left-to-Right Embedding
        '\u202B': '',  # Right-to-Left Embedding
        '\u202C': '',  # Pop Directional Formatting
        '\u202D': '',  # Left-to-Right Override
        '\u202E': '',  # Right-to-Left Override

    }
    
    for src, tgt in mapping.items():
        text = text.replace(src, tgt)
    
    # Remove diacritics - expanded range
    import re
    # Arabic diacritics, Quranic annotation signs, and other marks
    text = re.sub(r'[\u0610-\u061A\u0640\u064B-\u065F\u0670\u06D6-\u06ED\u08E3-\u08FE]', '', text)
    
    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

text = "کیا آپ کو اُردو یا فارسی سمجھ آتی ہے؟"
print(map_to_standard_arabic(text))




import re
from pyarabic.araby import strip_tatweel

patterns = {
    'hijri': [
        r'(\d{1,4})\s*هـ',   # Handles different digit lengths
        r'(\d{1,4})\s*هــ',
        r'(\d{1,4})\s*هـــ',
        r'(\d{1,4})\s*ه',
        r'(\d{1,4})\s*هجري',  # Explicit mention of "Hijri"
        r'(\d{1,4})\s*سنة هجرية'
    ],
    'gregorian': [
        r'(\d{4})\s*م',
        r'(\d{4})\s*ميلادي',
        r'(\d{4})',
        r'(\d{1,4})\s*AD',  # English format
        r'(\d{1,4})\s*Anno Domini',
        r'(\d{4})\s*CE',  # Common Era notation
        r'(\d{4})\s*السنة الميلادية'  # Explicit Arabic wording
    ],
    'mixed': [
        r'(\d{1,4})\s*هـ\s*\((\d{4})\s*م\)',  # Hijri with Gregorian in parentheses
        r'(\d{4})\s*م\s*\((\d{1,4})\s*هـ\)'   # Gregorian with Hijri in parentheses
    ]
}

patterns = {
    'hijri': [
        r'(\d{1,4})\s*هـ',   
        r'(\d{1,4})\s*هــ',
        r'(\d{1,4})\s*هـــ',
        r'(\d{1,4})\s*ه',
        r'(\d{1,4})\s*هجري',  
        r'(\d{1,4})\s*سنة هجرية',
        r'(\d{1,4})-(\d{1,4})\s*هـ'  # Hijri year range (e.g., 1440-1445 هـ)
    ],
    'gregorian': [
        r'(\d{4})\s*م',
        r'(\d{4})\s*ميلادي',
        r'(\d{4})',
        r'(\d{1,4})\s*AD',
        r'(\d{1,4})\s*Anno Domini',
        r'(\d{4})\s*CE',  
        r'(\d{4})\s*السنة الميلادية',
        r'(\d{4})-(\d{4})\s*م'  # Gregorian year range (e.g., 1990-2025 م)
    ],
    'mixed': [
        r'(\d{1,4})\s*هـ\s*\((\d{4})\s*م\)',  
        r'(\d{4})\s*م\s*\((\d{1,4})\s*هـ\)',
        r'(\d{1,4})-(\d{1,4})\s*هـ\s*\((\d{4})-(\d{4})\s*م\)',  # Hijri range with Gregorian equivalent
        r'(\d{4})-(\d{4})\s*م\s*\((\d{1,4})-(\d{1,4})\s*هـ\)'   # Gregorian range with Hijri equivalent
    ]
}




# Various date patterns
patterns = {
    'hijri': [
        r'(\d{4})\s*هـ',
        r'(\d{4})\s*هــ',
        r'(\d{4})\s*هـــ',
        r'(\d{4})\s*ه'
    ],
    'gregorian': [
        r'(\d{4})\s*م',
        r'(\d{4})\s*ميلادي',
        r'(\d{4})'
    ]
}

# More comprehensive version with additional patterns
def date_standardization(date_str):
    """
    Advanced date standardization with multiple patterns
    """
    if not date_str or date_str.strip() == '':
        return "", {
            'hijri_year': "",
            'gregorian_year': "",
            'hijri': "",
            'gregorian': ""
        }
    
    # Clean input
    date_str = date_str.strip(' -')
    
    try:
        # Find Hijri year
        hijri_year = None
        for pattern in patterns['hijri']:
            match = re.search(pattern, date_str)
            if match:
                hijri_year = match.group(1)
                break
        
        # Find Gregorian year
        gregorian_year = None
        for pattern in patterns['gregorian']:
            match = re.search(pattern, date_str)
            if match:
                gregorian_year = match.group(1)
                break
        
        # Format dates
        hijri = f"{hijri_year} هـ" if hijri_year else ""
        gregorian = f"{gregorian_year} م" if gregorian_year else ""
        
        # Create standardized format
        if hijri and gregorian:
            standardized_date = f"{gregorian} - {hijri}"
        else:
            standardized_date = hijri or gregorian
        
        return  standardized_date, {
            'hijri_year'        : int(hijri_year) if hijri_year else None,
            'gregorian_year'    : int(gregorian_year) if gregorian_year else None,
            'hijri'             : hijri,
            'gregorian'         : gregorian
        }
        
    except Exception as e:
        print(f"Error in advanced date processing: {date_str}, Error: {e}")
        return "", {
            'hijri_year': "",
            'gregorian_year': "",
            'hijri': "",
            'gregorian': ""
        }