# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 16:34:43 2025

@author: m
"""

# Persian characters that may appear in Arabic text (typos) → Standard Arabic
PERSIAN_TO_ARABIC = {
    # PERSIAN (FARSI) - Iran, Afghanistan - Non-Arabic specific letters only
    'ک': 'ك',  # Persian keheh (U+06A9) → Arabic kaf (U+0643)
    'گ': 'ك',  # Persian gaf (U+06AF) → Arabic kaf (U+0643) 
    'پ': 'ب',  # Persian peh (U+067E) → Arabic beh (U+0628)
    'چ': 'ج',  # Persian cheh (U+0686) → Arabic jeem (U+062C)
    'ژ': 'ز',  # Persian jeh (U+0698) → Arabic zain (U+0632)
    'ی': 'ي',  # Persian yeh (U+06CC) → Arabic yeh (U+064A)
    'ى': 'ي',  # Alef maksura (U+0649) → Arabic yeh (U+064A) 
}

# Urdu characters that may appear in Arabic text (typos) → Standard Arabic  
URDU_TO_ARABIC = {
    # URDU - Pakistan, India - Non-Arabic specific letters only
    'ے': 'ي',  # Yeh barree (U+06D2) → Arabic yeh (U+064A)
    'ۓ': 'ي',  # Yeh barree with hamza (U+06D3) → Arabic yeh (U+064A)
    'ں': 'ن',  # Noon ghunna (U+06BA) → Arabic noon (U+0646)
    'ٹ': 'ت',  # Teh with ring (U+0679) → Arabic teh (U+062A)
    'ڈ': 'د',  # Dal with dot below (U+0688) → Arabic dal (U+062F)
    'ڑ': 'ر',  # Reh with small v below (U+0691) → Arabic reh (U+0631)
    'ہ': 'ه',  # Heh goal (U+06C1) → Arabic heh (U+0647)
    'ھ': 'ه',  # Heh doachashmee (U+06BE) → Arabic heh (U+0647)
    'ۃ': 'ه',  # Teh marbuta goal (U+06C3) → Arabic heh (U+0647)
    'ۂ': 'ه',  # Heh goal with hamza (U+06C2) → Arabic heh (U+0647)
}

# Pashto characters that may appear in Arabic text (typos) → Standard Arabic
PASHTO_TO_ARABIC = {
    # PASHTO - Afghanistan, Pakistan - Non-Arabic specific letters only
    'ږ': 'ز',  # Reh with dot below and dot above (U+0696) → Arabic zain (U+0632)
    'ښ': 'ش',  # Shin with dot below (U+069A) → Arabic sheen (U+0634)
    'ګ': 'ك',  # Gaf with ring (U+06AB) → Arabic kaf (U+0643)
    'ڼ': 'ن',  # Noon with ring (U+06BC) → Arabic noon (U+0646)
    'ړ': 'ر',  # Reh with ring (U+0693) → Arabic reh (U+0631)
    'ۍ': 'ي',  # Yeh with tail (U+06CD) → Arabic yeh (U+064A)
    'ې': 'ي',  # Yeh with small v above (U+06D0) → Arabic yeh (U+064A)
    'ځ': 'ج',  # Hah with hamza above (U+0681) → Arabic jeem (U+062C)
    'څ': 'ج',  # Hah with three dots above (U+0685) → Arabic jeem (U+062C)
    'ډ': 'د',  # Dal with ring (U+0689) → Arabic dal (U+062F)
    'ټ': 'ت',  # Teh with ring (U+067C) → Arabic teh (U+062A)
}
# Kurdish characters that may appear in Arabic text (typos) → Standard Arabic
KURDISH_TO_ARABIC = {
    # KURDISH (Sorani) - Iraq, Iran - Non-Arabic specific letters only
    'ڕ': 'ر',  # Reh with small v above (U+0695) → Arabic reh (U+0631)
    'ڵ': 'ل',  # Lam with small v above (U+06B5) → Arabic lam (U+0644)
    'ۆ': 'و',  # Waw with small v above (U+06C6) → Arabic waw (U+0648)
    'ێ': 'ي',  # Yeh with small v above (U+06CE) → Arabic yeh (U+064A)
    'ڤ': 'ف',  # Feh with three dots above (U+06A4) → Arabic feh (U+0641)
}

# 
# UYGHUR characters that may appear in Arabic text (typos) → Standard Arabic
UYGHUR_TO_ARABIC = {
# UYGHUR - China (Xinjiang) - Non-Arabic specific letters only
    'ۇ': 'و',  # Waw with damma above (U+06C7) → Arabic waw (U+0648)
    'ۈ': 'و',  # Waw with alef above (U+06C8) → Arabic waw (U+0648)
    'ۉ': 'و',  # Waw with inverted small v (U+06C9) → Arabic waw (U+0648)
    'ۊ': 'و',  # Waw with two dots above (U+06CA) → Arabic waw (U+0648)
}  

# Sindhi and Malay characters that may appear in Arabic text (typos) → Standard Arabic
SINDHI_TO_ARABIC = {
    # SINDHI - Pakistan - Non-Arabic specific letters only
    'ٻ': 'ب',  # Beh with dot below (U+067B) → Arabic beh (U+0628)
    'ڀ': 'ب',  # Beh with small v below (U+0680) → Arabic beh (U+0628)
    'ٺ': 'ت',  # Teh with dot above (U+067A) → Arabic teh (U+062A)
    'ٿ': 'ت',  # Theh with dot above (U+067F) → Arabic teh (U+062A) - Changed to avoid ث conflict
    'ڄ': 'ج',  # Jeem with dot below (U+0684) → Arabic jeem (U+062C)
    'چھ': 'ج',  # Cheh with dot above (U+0687) → Arabic jeem (U+062C)
    'ڃ': 'ج',  # Nyeh (U+0683) → Arabic jeem (U+062C)
    'ڊ': 'د',  # Dal with dot below and small tah (U+068A) → Arabic dal (U+062F)
    'ڏ': 'د',  # Dal with dot below and dot above (U+068F) → Arabic dal (U+062F)
    'ڙ': 'ر',  # Reh with small v below (U+0699) → Arabic reh (U+0631)
    'ڪ': 'ك',  # Swash kaf (U+06AA) → Arabic kaf (U+0643)
    'ڬ': 'ك',  # Gaf with two dots below (U+06AC) → Arabic kaf (U+0643)
    'ڮ': 'ك',  # Ngoeh (U+06AE) → Arabic kaf (U+0643)
    'ڶ': 'ل',  # Lam with dot above (U+06B6) → Arabic lam (U+0644)
    'ڷ': 'ل',  # Lam with three dots above (U+06B7) → Arabic lam (U+0644)
    'ڸ': 'ل',  # Lam with three dots below (U+06B8) → Arabic lam (U+0644)
    'ڻ': 'ن',  # Noon with three dots above (U+06BB) → Arabic noon (U+0646)
    'ڦ': 'ف',  # Feh with dot below (U+06A6) → Arabic feh (U+0641)
    'ڳ': 'ك',  # Gaf with two dots below (U+06B3) → Arabic kaf (U+0643)
}

# Malay characters that may appear in Arabic text (typos) → Standard Arabic
MALAY_TO_ARABIC = {
    # MALAY (Jawi) - Malaysia, Brunei - Non-Arabic specific letters only
    'ڠ': 'ن',  # Ng (U+06A0) → Arabic noon (U+0646)
    'ݢ': 'ك',  # Gaf with dot above (U+0762) → Arabic kaf (U+0643)
    'ۑ': 'ي',  # Yeh with three dots below (U+06D1) → Arabic yeh (U+064A)
    'ڽ': 'ن',  # Knotted heh (U+06BD) → Arabic noon (U+0646)
    'ۏ': 'و',  # Waw with dot above (U+06CF) → Arabic waw (U+0648)
}

# Kurdish and Uyghur characters that may appear in Arabic text (typos) → Standard Arabic
OTHER_SAFE_TO_ARABIC = {
    # OTHER SAFE LANGUAGE-SPECIFIC LETTERS
    'ڡ': 'ف',  # Feh with dot moved below (U+06A1) → Arabic feh (U+0641)
    'ۺ': 'س',  # Seen with small tah and two dots (U+06FA) → Arabic seen (U+0633)
    'ۼ': 'ق',  # Qaf with dot above (U+06FC) → Arabic qaf (U+0642)
    'ڭ': 'ك',  # Ng (U+06AD) → Arabic kaf (U+0643)
}



ZERO_WIDTH_CHARS = {
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

# Basic punctuation mappings (what you already have)
PUNCTUATION_NORMALIZATION = {
    # Punctuation normalization (safe - these are not Arabic letters)
    ',': '،',     # Comma → Arabic comma
    ';': '؛',     # Semicolon → Arabic semicolon
    '?': '؟',     # Question mark → Arabic question mark
}

# Qur'anic and Extended Arabic diacritical marks (not in DIACRITICS)
QURANIC_MARKS = {
    'ࣰ': '',  # Quranic Open Fathatan (U+08F0)
    'ࣱ': '',  # Quranic Open Dammatan (U+08F1)
    'ࣲ': '',  # Quranic Open Kasratan (U+08F2)
    'ۡ': '',  # Quranic Sukūn / Small High Dotless Head of Khah (U+06E1)
    'ٖ': '',  # Arabic Subscript Alef (already in DIACRITICS, optional if you want to separate)
    'ٗ': '',  # Arabic Inverted Damma (already in DIACRITICS)
    '٘': '',  # Arabic Mark Noon Ghunna (U+0658) — not in DIACRITICS
    'ۤ': '',  # Arabic Small High Madda (U+06E4)
    'ۨ': '',  # Arabic Small High Yeh (U+06E8)
    '۪': '',  # Arabic Small High Noon (U+06EA)
    '۫': '',  # Arabic Small Low Meem (U+06EB)
    '۬': '',  # Arabic Small Low Seen (U+06EC)
    'ۭ': '',  # Arabic Small High Seen (U+06ED)
}

# Arabic diacritics (harakat) to remove
DIACRITICS = {
    'َ': '',   # Fatha (U+064E)
    'ِ': '',   # Kasra (U+0650)
    'ُ': '',   # Damma (U+064F)
    'ً': '',   # Tanween fath (U+064B)
    'ٍ': '',   # Tanween kasr (U+064D)
    'ٌ': '',   # Tanween damm (U+064C)
    'ْ': '',   # Sukun (U+0652)
    'ّ': '',   # Shadda (U+0651)
    'ٰ': '',   # Superscript alef (U+0670)
    'ٖ': '',   # Small high seen (U+0656)
    'ٗ': '',   # Small high qaf (U+0657)
    '٘': '',   # Mark noon ghunna (U+0658)
}

TATWEEL = {
    'ـ': ''  # TATWEEL (Kashīda, U+0640)  
}

NUMBERS_NORMALIZATION = {
    # Arabic-Indic digits to Western digits
    '٠': '0',  # Arabic-Indic 0
    '١': '1',  # Arabic-Indic 1
    '٢': '2',  # Arabic-Indic 2
    '٣': '3',  # Arabic-Indic 3
    '٤': '4',  # Arabic-Indic 4
    '٥': '5',  # Arabic-Indic 5
    '٦': '6',  # Arabic-Indic 6
    '٧': '7',  # Arabic-Indic 7
    '٨': '8',  # Arabic-Indic 8
    '٩': '9',  # Arabic-Indic 9

    # Persian (Extended Arabic-Indic) digits to Western digits
    '۰': '0',  # Persian 0
    '۱': '1',  # Persian 1
    '۲': '2',  # Persian 2
    '۳': '3',  # Persian 3
    '۴': '4',  # Persian 4
    '۵': '5',  # Persian 5
    '۶': '6',  # Persian 6
    '۷': '7',  # Persian 7
    '۸': '8',  # Persian 8
    '۹': '9',  # Persian 9
    
    # Arabic-Indic digits to Western digits (safe - these are digits, not letters)
    #     '0': '٠',      # English 0 → Arabic-Indic 0
    #     '1': '١',      # English 1 → Arabic-Indic 1
    #     '2': '٢',      # English 2 → Arabic-Indic 2
    #     '3': '٣',      # English 3 → Arabic-Indic 3
    #     '4': '٤',      # English 4 → Arabic-Indic 4
    #     '5': '٥',      # English 5 → Arabic-Indic 5
    #     '6': '٦',      # English 6 → Arabic-Indic 6
    #     '7': '٧',      # English 7 → Arabic-Indic 7
    #     '8': '٨',      # English 8 → Arabic-Indic 8
    #     '9': '٩',      # English 9 → Arabic-Indic 9
        
    #     # Persian (Extended Arabic-Indic) digits to Arabic-Indic digits
    #     '۰': '٠',  # Persian 0
    #     '۱': '١',  # Persian 1
    #     '۲': '٢',  # Persian 2
    #     '۳': '٣',  # Persian 3
    #     '۴': '٤',  # Persian 4
    #     '۵': '٥',  # Persian 5
    #     '۶': '٦',  # Persian 6
    #     '۷': '٧',  # Persian 7
    #     '۸': '٨',  # Persian 8
    #     '۹': '٩',  # Persian 9
}

# Other Arabic-script variants → Standard Arabic
ARABIC_VARIANTS = {
    # ALEF VARIANTS (safe - these are not standard Arabic letters)
    'أ': 'ا',  # Alef with hamza above (U+0623) → Arabic alef (U+0627)
    'إ': 'ا',  # Alef with hamza below (U+0625) → Arabic alef (U+0627)
    'آ': 'ا',  # Alef with madda above (U+0622) → Arabic alef (U+0627)
    'ٱ': 'ا',  # Alef wasla (U+0671) → Arabic alef (U+0627)
    'ٲ': 'ا',  # Alef with wavy hamza above (U+0672) → Arabic alef (U+0627)
    'ٳ': 'ا',  # Alef with wavy hamza below (U+0673) → Arabic alef (U+0627)
        
    # HEH VARIANTS (safe - these are not standard Arabic letters)
#     'ة': 'ه',  # Teh marbuta (U+0629) → Arabic heh (U+0647)ة
    'ۀ': 'ه',  # Heh with yeh above (U+06C0) → Arabic heh (U+0647)
        
    # WAW VARIANTS (safe - these are not standard Arabic letters)
    'ؤ': 'و',  # Waw with hamza above (U+0624) → Arabic waw (U+0648)ؤ
    'ۄ': 'و',  # Waw with ring (U+06C4) → Arabic waw (U+0648)
        
    # YEH VARIANTS (safe - these are not standard Arabic letters)
    'ئ': 'ي',  # Yeh with hamza above (U+0626) → Arabic yeh (U+064A)
    'ؠ': 'ي',  # Yeh with small v above (U+0620) → Arabic yeh (U+064A)
    'ى': 'ي',  # Alef maksura (U+0649) → Arabic yeh (U+064A)
}