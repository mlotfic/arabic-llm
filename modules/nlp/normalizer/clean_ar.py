import re
import logging

# Configure logging at the top of the file, after the imports
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(message)s',
    handlers=[
        logging.FileHandler('arabic_cleaning.log', 'w', 'utf-8'),
        logging.StreamHandler()  # Added to show output in console too
    ]
)

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

cleaning_pipline = [
    PERSIAN_TO_ARABIC,
    URDU_TO_ARABIC,
    PASHTO_TO_ARABIC,
    KURDISH_TO_ARABIC,
    UYGHUR_TO_ARABIC,
    SINDHI_TO_ARABIC,
    MALAY_TO_ARABIC,
    ARABIC_VARIANTS,
    OTHER_SAFE_TO_ARABIC,
    PUNCTUATION_NORMALIZATION,
    NUMBERS_NORMALIZATION,  
    DIACRITICS,
    TATWEEL,        
    ZERO_WIDTH_CHARS,
    ]

def map_to_standard_arabic(text: str, mapping: dict):
    # Apply character mapping
    for src, tgt in mapping.items():
        logging.debug(f"Replacing '{src}' with '{tgt}'")
        # Replace each character in the mapping
        text = text.replace(src, tgt)

    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()

    return text

def map_to_standard_arabic(text: str, mapping: dict):
        
    # Apply character mapping
    for src, tgt in mapping.items():
        text = text.replace(src, tgt)

    # Normalize multiple spaces to single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()

    return text

# Function to clean text using the defined mappings
def clean_text(text: str) -> str:
    for mapping in cleaning_pipline:
        text = map_to_standard_arabic(text, mapping)
    return text

def replace_parentheses_with_angle_quotes(text):
    """
    Replace any text inside parentheses () with the same text inside
    « and » (LEFT-POINTING and RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK).

    Args:
        text (str): Input string possibly containing parentheses.

    Returns:
        str: Modified string with parentheses replaced by angle quotes.
    """
    # Pattern to match text inside parentheses (non-greedy)
    pattern = r'\((.*?)\)'

    # Replacement function to wrap the captured group with « and »
    def replacer(match):
        inner_text = match.group(1)
        return f'«{inner_text}»'

    # Substitute all occurrences
    return re.sub(pattern, replacer, text)

def padSymbols(inTxt, symbolList=['۞', '۝']):
    for sym in symbolList:
        inTxt = inTxt.replace(sym, ' ' + sym + ' ')
    return inTxt

# Code to read in the test tweets and to generate the tool output 
def outPutResults(fname, outF):
    f = codecs.open(fname, "r", "utf-8")
    f2 = codecs.open(outF, "w", "utf-8")
    i =1 
    for line in f:
        sp = line.split('\t')
        if len(sp)!= 2:
            print('err in line', i)
            continue
        idd = sp[0]
        tweet = sp[1].strip()
        #print(tweet)
        v_matches = qAn.matchAll(tweet,allowedErrPers=0.2 )
        matches = []
        unique = set([])
        for i in range(len(v_matches)): 
            r1 = v_matches[i]
            aya = r1['aya_name'] + ':' 
            if (r1['aya_start']) != (r1['aya_end']):
                aya = aya + str(r1['aya_start']) + '-' + str((r1['aya_end']))
            else:
                aya = aya + str(r1['aya_start'])

            start = int(r1['startInText'])
            end = int(r1['endInText'])
            loc = (start,end)
            unique.add(loc)
            m = tweet.split()[start:end]
            matches.append((' '.join(m),aya))
        f2.write(idd + "\t" + str(matches)+  "\t" +str(len(unique))+ "\n")
        i= i+1
        
    f.close()
    f2.close()

def combine_entities(entities):
    combined = []
    current_name = []
    current_indices = []
    
    for i, entity in enumerate(entities):
        # Start a new name if it's a B-PERS or if there's no current name
        if entity['entity'] == 'B-PERS':
            # If there was a previous name, add it to combined list
            if current_name:
                combined.append({
                    'entity': 'PERS',
                    'name': ' '.join(current_name),
                    'score': sum(current_indices) / len(current_indices),
                    'start': entities[current_indices[0]]['start'],
                    'end': entities[current_indices[-1]]['end']
                })
            current_name = [entity['word']]
            current_indices = [i]
            
        # Continue building the current name if it's an I-PERS
        elif entity['entity'] == 'I-PERS' and current_name:
            current_name.append(entity['word'])
            current_indices.append(i)
            
        # Handle non-person entities or gaps
        else:
            # Save any accumulated name
            if current_name:
                combined.append({
                    'entity': 'PERS',
                    'name': ' '.join(current_name),
                    'score': sum(current_indices) / len(current_indices),
                    'start': entities[current_indices[0]]['start'],
                    'end': entities[current_indices[-1]]['end']
                })
                current_name = []
                current_indices = []
            
            # Add the current entity if it's not an I-PERS
            if entity['entity'] != 'I-PERS':
                combined.append({
                    'entity': entity['entity'].replace('B-', ''),
                    'name': entity['word'],
                    'score': entity['score'],
                    'start': entity['start'],
                    'end': entity['end']
                })
    
    # Add the last name if there is one
    if current_name:
        combined.append({
            'entity': 'PERS',
            'name': ' '.join(current_name),
            'score': sum(current_indices) / len(current_indices),
            'start': entities[current_indices[0]]['start'],
            'end': entities[current_indices[-1]]['end']
        })
    return combined
        

def extract_dates_with_positions(text):
    """
    Extract dates from text and return them with their positions.
    
    Args:
        text (str): The text to search for dates
        
    Returns:
        list: A list of dictionaries containing date information and positions
    """
    import re
    from dateparser.search import search_dates
    
    results = []
    dates = search_dates(text)
    
    if dates:
        for dt in dates:
            date_str = dt[0]
            date_obj = dt[1]
            
            # Find the position of the date expression in the text
            match = re.search(r'\b' + re.escape(date_str) + r'\b', text)
            if match:
                start_pos = match.start()
                end_pos = match.end()
                
                results.append({
                    'entity': 'DATE',
                    'name': date_str,
                    'value': date_obj,
                    'score': "",
                    'start': start_pos,
                    'end': end_pos
                })
    
    return results




# def load_models():
#     """Load necessary NLP models."""
#     nlp = spacy.load("xx_sent_ud_sm")  # Universal model supporting Arabic
#     model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
#     return nlp, model

# def compute_similarity(embeddings):
#     """Compute cosine similarity between consecutive sentence embeddings."""
#     similarities = [
#         np.dot(embeddings[i], embeddings[i + 1]) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1]))
#         for i in range(len(embeddings) - 1)
#     ]
#     return similarities

# def chunk_text(text, threshold=0.75):
#     """Segment Arabic text into semantic chunks based on similarity."""
#     nlp, model = load_models()
    
#     # Sentence segmentation
#     doc = nlp(text)
#     sentences = [sent.text for sent in doc.sents]
    
#     # Compute sentence embeddings
#     embeddings = model.encode(sentences)
#     similarities = compute_similarity(embeddings)
    
#     # Create chunks
#     chunks, current_chunk = [], []
#     for i, sentence in enumerate(sentences):
#         current_chunk.append(sentence)
#         if i < len(similarities) and similarities[i] < threshold:
#             chunks.append(" ".join(current_chunk))
#             current_chunk = []
    
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))
    
#     return chunks


if __name__ == "__main__":
    # Force UTF-8 encoding for stdout
    import sys
    import codecs
    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    
    text = "هذا نص عربي مع بعض الأخطاء مثل ك، گ، پ، چ، ژ، ي، ى، ے، ڑ، ٹ، ڈ، ں، ہ، ھ، ۓ."
    cleaned_text = clean_text(text)
    print("Original text:", text)
    print("Cleaned text:", cleaned_text)


    # Example usage:
    input_text = "This is a test (example) string with (multiple) parentheses."
    output_text = replace_parentheses_with_angle_quotes(input_text)
    print(output_text)


    # Test with some examples
    test_texts = [
        "سلام علیکم",  # Persian
        "آپ کیسے ہیں؟",  # Urdu
        "څنګه یاست؟",  # Pashto
        "چۆنی؟",  # Kurdish,
        u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا ۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789"
    ]
    
    
    for text in test_texts:
        normalized = clean_text(text)
        print(f"Original: {text}")
        print(f"Normalized: {normalized}")
        print("---")
    
    
    # from QuranDetectorAnnotater import qMatcherAnnotater,term
    # import codecs

    # qAn = qMatcherAnnotater()

        
    # #Calling matchAll without changing any of the values of the default parmaters 
    # txt = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"  
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )

    # #Another example
    # txt = 'RT @user: بسْمِ اللهِ الرَّحْمَنِ الرَّحِيمِ  قُلْ هُوَ اللَّهُ أَحَدٌ ۞ اللَّهُ الصَّمَدُ ۞ لَمْ يَلِدْ وَلَمْ يُولَدْ ۞ وَلَمْ يَ…'
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )

    # #an example where a missing word is detected
    # txt = 'الم ذلك الكتاب لا ريب هدي للمتقين'
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )


    # txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )

    # # here we remove الله from the first verse
    # # the missing word appears in the error list of the first verse. 
    # txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )


    # #now we dis-able the detection of missing words. Again, the verse where a missing word exists, is now no longer detected. 
    # txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    # vs = qAn.matchAll(txt, findMissing=False)
    # print(vs)


    # #In this example we increase the error tolerance. This is not advised because you might end up with matches that are not accurate

    # #With the default error tolerance of 25% or 0.25
    # txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَا اللَّهُ أَحَ…'
    # print('With the default error tolerance of 25% or 0.25 (no matches returned):')
    # vs = qAn.matchAll(txt)
    # print(vs)

    # #With the increaced error tolerance
    # vs = qAn.matchAll(txt, allowedErrPers=0.5)
    # print('With the increaced error tolerance:')
    # print(vs)

    # ## Annotating Text
    # txt = "RT @user:... كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحونَ بِحمدِ ربهِم…"
    # t = qAn.annotateTxt(txt)
    # print('')
    # print(t)

    # #note how the last word has been automatically corrected 
    # txt = ' واستعينوا بالصبر والصلاه وانها لكبيره الا علي الخشعين'
    # qAn.annotateTxt(txt)

    # txt = 'RT @7Life4ever: ﷽  قل هو ﷲ أحد۝ ﷲ الصمد۝لم يلد ولم يولد۝ولم يكن له كفوا أحد  ﷽  قل أعوذ برب الفلق۝من شر ما خلق ۝ومن شر غاسق إذا وقب۝ومن شر ا…'
    # qAn.annotateTxt(txt)


    # txt = ''' اعلم يا أخي أن الله تعالى فضل مكة على سائر البلاد وأنزل ذكرها في كتابه  ~~العزيز في مواضع عديدة فقال تعالى {إن أول بيت وضع للناس للذي ببكة مباركا    ~~وهدى للعالمين فيه آيات بينات مقام إبراهيم ومن دخله كان آمنا}

    # '''
    # txt = txt.replace("~~", "")
    # t = qAn.annotateTxt(txt)
    # qAn.annotateTxt(txt)
    # vs = qAn.matchAll(txt)
    # print(vs)
    # print(len(vs), 'entrie(s) returned.' )
    
    
    # import re
    # import pyarabic.number as number

    # from pyarabic.araby import strip_tatweel
    # text = u"العـــــربية"
    # strip_tatweel(text)

    # from pyarabic.araby import normalize_ligature
    # text = u"لانها لالء الاسلام"
    # normalize_ligature(text)

    # import pyarabic.number
    # an = pyarabic.number.ArNumbers()
    # an.int2str('125')

    # # === Main loop ===
    # pyarabic.number.number2ordinal(125)

    # from pyarabic.number import text2number
    # text2number(u"خمسمئة وثلاث وعشرون")
    # text2number(u'المئة والخامس والعشرون')
    # text2number(u'مئة و خمس و عشرون')


    # from pyarabic.number import extract_number_phrases
    # extract_number_phrases(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")

    # extract_number_phrases(u"خمسمئة وثلاث وعشرون")
    # extract_number_phrases(u'المئة والخامس والعشرون')
    # extract_number_phrases(u'مئة و خمس و عشرون')


    # from pyarabic.number import extract_number_context
    # extract_number_context(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")

    # extract_number_context(u"خمسمئة وثلاث وعشرون")
    # extract_number_context(u'المئة والخامس والعشرون'.replace('ال', ''))
    # extract_number_context(u'مئة و خمس و عشرون')

    # import pyarabic.trans
    # text = u'۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789'

    # from openiti.helper.ara import normalize_ara_heavy




    # pyarabic.trans.normalize_digits(text, source='all', out='west')


    # text =u"""السلام عليكم how are you, لم اسمع أخبارك منذ مدة, where are you going"""
    # pyarabic.trans.segment_language(text)

    # from pyarabic import araby
    # from pyarabic.number import detect_numbers
    # wordlist = araby.tokenize(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")
    # detect_numbers(wordlist)

    # wordlist = araby.tokenize(text)
    # detect_numbers(wordlist)

    # def preprocessing_numbers(text = u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا ۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789"):   
    #     text = normalize_ara_heavy(text)
        
    #     text = pyarabic.trans.normalize_digits(str(text), source='all', out='west')
    #     extract_number_context(text)
    #     extract_number_phrases(text)
    #     text2number(text)
        
    #     an.int2str("123456789")
        
    #     match = re.search(r'\d+',text)
    #     if match:
    #         match[0]
        
        
    #     text = strip_tatweel(text).replace('ال', '') 
    #     text = text2number(text)
        
        
    #     return number

    # preprocessing_numbers(u"خمسمئة وثلاث وعشرون")
    # preprocessing_numbers(u'المئة والخامس والعشرون')
    # preprocessing_numbers(u'مئة و خمس و عشرون')


    # from pyarabic.number import number2text

    # number2text(text)
    
    
    



# import spacy
# from sentence_transformers import SentenceTransformer
# import numpy as np

# import torch
# import sys
# import os

# import re

# from dateparser.search import search_dates
# from dateparser import DateDataParser
# from dateparser.conf import settings

# from transformers import AutoTokenizer
# from transformers import pipeline

# print(f"Python version: {sys.version}")
# print(f"PyTorch version: {torch.__version__}")
# print(f"PyTorch CUDA version: {torch.version.cuda}")
# print(f"CUDA available: {torch.cuda.is_available()}")
# if torch.cuda.is_available():
#     print(f"CUDA device: {torch.cuda.get_device_name(0)}")

from dotenv import load_dotenv
import os

load_dotenv()  # defaults to looking for `.env` in current dir

# Now you can safely access the token
hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Optional: set it explicitly in env vars (if some library expects it that way)
os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token

# # CAMeL-Lab/bert-base-arabic-camelbert-ca-ner
# # CAMeL-Lab/bert-base-arabic-camelbert-mix-ner

# # Load your desired tokenizer
# tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")

# # Tokenize a sample text and check how many tokens it generates
# text = "هذا مثال على النص باللغة العربية."
# tokens = tokenizer(text, return_tensors="pt")
# print("Number of tokens in input:", tokens["input_ids"].shape[1])

# ner = pipeline("ner", model="CAMeL-Lab/bert-base-arabic-camelbert-mix-ner", device=0)

# text = "هدفي أن أكون عالِم بيانات ناجح في شركة جوجل."
# entities = ner(text)

# combined_entities = combine_entities(entities)

# search_dates(
#     text = 'The first artificial Earth satellite was launched on 4 اكتوبر .', 
#     languages=['ar', 'en'], 
#     settings=None, 
#     add_detected_language=False, 
#     detect_languages_function=None
#     )

# search_dates('The first artificial Earth satellite was launched on 4 October 1957.')

# # [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]
# search_dates('The first artificial Earth satellite was launched on 4 October 1957.',
#              add_detected_language=True)


# search_dates("The client arrived to the office for the first time in March 3rd, 2004 "
#              "and got serviced, after a couple of months, on May 6th 2004, the customer "
#              "returned indicating a defect on the part")


# text = "The meeting happened 2 days ago and we need to follow up."
# dt_list = []
# dates = search_dates(text)

# for dt in dates:
#     date_str = dt[0]
#     print(date_str)
    
#     # Find the position of the date expression in the text
#     match = re.search(r'\b' + re.escape(date_str) + r'\b', text)
#     if match:
#         x = match.start()
#         y = match.end()
        
#         dt_list.append({
#             'entity': 'DATE', 
#             'name': date_str, 
#             'score': "", 
#             'start': x, 
#             'end': y        
#         })
        
# text[21:35]



# if __name__ == "__main__":
#     sample_text = "We had a meeting 2 days ago and we need another one next Friday."
#     date_entities = extract_dates_with_positions(sample_text)
    
#     for entity in date_entities:
#         print(f"Found '{entity['name']}' at positions {entity['start']}-{entity['end']}")
#         print(f"Parsed as: {entity['value']}")
#         print()

#     from camel_tools.morphology.database import MorphologyDB
#     from camel_tools.morphology.analyzer import Analyzer

#     db = MorphologyDB.builtin_db()

#     # Create analyzer with no backoff
#     analyzer = Analyzer(db)


#     # Create analyzer with NOAN_PROP backoff
#     analyzer = Analyzer(db, 'NOAN_PROP')

#     # or
#     analyzer = Analyzer(db, backoff='NOAN_PROP')


#     # To analyze a word, we can use the analyze() method
#     analyses = analyzer.analyze('شارع')

#     from camel_tools.ner import NERecognizer

#     ner = NERecognizer.pretrained()

#     # Predict the labels of a single sentence.
#     # The sentence must be pretokenized by whitespace and punctuation.
#     sentence = 'إمارة أبوظبي هي إحدى إمارات دولة الإمارات العربية المتحدة السبع .'.split()
#     labels = ner.predict_sentence(sentence)

#     # Print the list of token-label pairs
#     print(list(zip(sentence, labels)))




#     # Use a pipeline as a high-level helper
#     from transformers import pipeline

#     pipe = pipeline("token-classification", model="CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")    
#     from transformers import AutoTokenizer, AutoModelForTokenClassification

#     tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")
#     model = AutoModelForTokenClassification.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")


#     from camel_tools.ner import NERecognizer
#     from camel_tools.tokenizers.word import simple_word_tokenize


#     # Load CAMeL NER
#     ner = NERecognizer.pretrained()

#     # Text
#     sentence = simple_word_tokenize('إمارة أبوظبي هي إحدى إمارات دولة الإمارات العربية المتحدة السبع')

#     # Predict
#     entities = ner.predict_sentence(sentence)

#     combined_entities = combine_entities(entities)


#     # Print
#     for token, label in zip(sentence, labels):
#         print(f"{token} -> {label}")



#     from transformers import AutoTokenizer, AutoModelForTokenClassification
#     from transformers import pipeline

#     # Initialize NER pipeline
#     ner = pipeline(
#         "ner",
#         model="CAMeL-Lab/bert-base-arabic-camelbert-msa",
#         tokenizer="CAMeL-Lab/bert-base-arabic-camelbert-msa"
#     )

#     # Example text
#     text = "يعيش محمد في دبي ويعمل في شركة جوجل"
#     results = ner(text)

#     # Process and display results
#     for result in results:
#         print(f"Entity: {result['word']}, Type: {result['entity']}, Score: {result['score']:.2f}")


#     # Text Preprocessing and Analysis:

        
#     import torch
#     from transformers import AutoTokenizer, AutoModel
#     import numpy as np

#     def get_text_embedding(text, model, tokenizer):
#         # Tokenize and prepare input
#         inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
#         # Get model outputs
#         with torch.no_grad():
#             outputs = model(**inputs)
        
#         # Get embeddings from last hidden state
#         embeddings = outputs.last_hidden_state.mean(dim=1)
#         return embeddings

#     # Initialize model and tokenizer
#     tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix")
#     model = AutoModel.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix")

#     # Example texts
#     texts = [
        "مرحباً بكم في عالم الذكاء الاصطناعي",
        "تعلم الآلة هو مستقبل التكنولوجيا"
#     ]

#     # Get embeddings
#     embeddings = [get_text_embedding(text, model, tokenizer) for text in texts]
