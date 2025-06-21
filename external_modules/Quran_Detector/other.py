from dateparser.search import search_dates

from QuranDetectorAnnotater import qMatcherAnnotater,term
import codecs

import re

import spacy
from sentence_transformers import SentenceTransformer
import numpy as np

import torch
import sys
import os

import re

from dateparser.search import search_dates
from dateparser import DateDataParser
from dateparser.conf import settings

from transformers import AutoTokenizer
from transformers import pipeline

import clean_ar 

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


# Example usage:
input_text = "This is a test (example) string with (multiple) parentheses."
output_text = replace_parentheses_with_angle_quotes(input_text)
print(output_text)

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
        v_matches = qAn.matchAll(tweet, allowedErrPers=0.2 )
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




# Test the function
if __name__ == "__main__":
    # Test with some examples
    test_texts = [
        "سلام علیکم",  # Persian
        "آپ کیسے ہیں؟",  # Urdu
        "څنګه یاست؟",  # Pashto
        "چۆنی؟",  # Kurdish
    ]
    
    text = u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا ۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789"
    
    for text in test_texts:
        normalized = map_to_standard_arabic(text)
        print(f"Original: {text}")
        print(f"Normalized: {normalized}")
        print("---")
    
def format_quranic_matches(matches):
    """ ﴾<aya_text> ۞ <aya_text> ﴿ - «Quran:<sura>:<verse>»"""
    formatted = []

    for match in matches:
        verses = match.get('verses', [])
        if not verses:
            continue

        # Join multiple verse fragments if needed
        aya_text = ' ۞ '.join(verses)

        # Build verse reference
        aya_ref = f"{match['aya_start']}:{match['aya_end']}" if match['aya_start'] != match['aya_end'] else f"{match['aya_start']}"

        # Final format
        result = f"﴾{aya_text}﴿ - «Quran:{match['aya_name']}:{aya_ref}»"
        formatted.append(result)

    return formatted
    
vs = [
    {
        'aya_name': 'غافر',
        'verses': ['الذين يحملون العرش ومن حوله يسبحون بحمد ربهم'],
        'errors': [[('يسبحو', 'يسبحون', 18)]],
        'startInText': 13,
        'endInText': 21,
        'aya_start': 7,
        'aya_end': 7
    },
    {
        'aya_name': 'الكهف',
        'verses': ['واذكر ربك اذا نسيت'],
        'errors': [[]],
        'startInText': 21,
        'endInText': 25,
        'aya_start': 24,
        'aya_end': 24
    }
]

formatted = format_quranic_matches(vs)
for line in formatted:
    print(line)
    
def parse_quranic_formatted_text(lines):
    results = []

    for line in lines:
        match = re.search(r"۞ ﴿(.*?)﴾ ۝ ([\u0600-\u06FF]+):(\d+)", line)
        if match:
            aya_text = match.group(1).strip()
            surah = match.group(2).strip()
            verse = int(match.group(3).strip())

            results.append({
                "aya_name": surah,
                "verses": [aya_text],
                "aya_start": verse,
                "aya_end": verse
            })

    return results

formatted_lines = [
    "۞ ﴿ٱلَّذِينَ يَحۡمِلُونَ ٱلۡعَرۡشَ وَمَنۡ حَوۡلَهُۥ يُسَبِّحُونَ بِحَمۡدِ رَبِّهِمۡ﴾ ۝ غافر:7",
    "۞ ﴿وَٱذۡكُر رَّبَّكَ إِذَا نَسِيتَ﴾ ۝ الكهف:24"
]

parsed = parse_quranic_formatted_text(formatted_lines)
for p in parsed:
    print(p)

    

    qAn = qMatcherAnnotater()

        
    #Calling matchAll without changing any of the values of the default parmaters 
    txt = "RT @user: كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحو بِحمدِ ربهِم واذكر ربك إذا نسيت…"  
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )
    
    txt = clean_ar.clean_text(txt)
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )

    #Another example
    txt = 'RT @user: بسْمِ اللهِ الرَّحْمَنِ الرَّحِيمِ  قُلْ هُوَ اللَّهُ أَحَدٌ ۞ اللَّهُ الصَّمَدُ ۞ لَمْ يَلِدْ وَلَمْ يُولَدْ ۞ وَلَمْ يَ…'
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )

    #an example where a missing word is detected
    txt = 'الم ذلك الكتاب لا ريب هدي للمتقين'
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )


    txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )

    # here we remove الله from the first verse
    # the missing word appears in the error list of the first verse. 
    txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )


    #now we dis-able the detection of missing words. Again, the verse where a missing word exists, is now no longer detected. 
    txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ…'
    vs = qAn.matchAll(txt, findMissing=False)
    print(vs)


    #In this example we increase the error tolerance. This is not advised because you might end up with matches that are not accurate

    #With the default error tolerance of 25% or 0.25
    txt = 'RT @HolyQraan: من قرأها ثلاث مرات فكأنما قرأ القرآن كاملا ..   ﴿قُلْ هُوَا اللَّهُ أَحَ…'
    print('With the default error tolerance of 25% or 0.25 (no matches returned):')
    vs = qAn.matchAll(txt)
    print(vs)

    #With the increaced error tolerance
    vs = qAn.matchAll(txt, allowedErrPers=0.5)
    print('With the increaced error tolerance:')
    print(vs)

    ## Annotating Text
    txt = "RT @user:... كرامة المؤمن عند الله تعالى؛ حيث سخر له الملائكة يستغفرون له ﴿الذِين يحملونَ العرشَ ومَن حَولهُ يُسبحونَ بِحمدِ ربهِم…"
    t = qAn.annotateTxt(txt)
    print('')
    print(t)

    #note how the last word has been automatically corrected 
    txt = ' واستعينوا بالصبر والصلاه وانها لكبيره الا علي الخشعين'
    qAn.annotateTxt(txt)

    txt = 'RT @7Life4ever: ﷽  قل هو ﷲ أحد۝ ﷲ الصمد۝لم يلد ولم يولد۝ولم يكن له كفوا أحد  ﷽  قل أعوذ برب الفلق۝من شر ما خلق ۝ومن شر غاسق إذا وقب۝ومن شر ا…'
    qAn.annotateTxt(txt)


    txt = '''
    # اعلم يا أخي أن الله تعالى فضل مكة على سائر البلاد وأنزل ذكرها في كتابه
    ~~العزيز في مواضع عديدة فقال تعالى {إن أول بيت وضع للناس للذي ببكة مباركا
    ~~وهدى للعالمين فيه آيات بينات مقام إبراهيم ومن دخله كان آمنا}

    '''
    txt = txt.replace("~~", "")
    t = qAn.annotateTxt(txt)
    qAn.annotateTxt(txt)
    vs = qAn.matchAll(txt)
    print(vs)
    print(len(vs), 'entrie(s) returned.' )
    
    
    import re
    import pyarabic.number as number

    from pyarabic.araby import strip_tatweel
    text = u"العـــــربية"
    strip_tatweel(text)

    from pyarabic.araby import normalize_ligature
    text = u"لانها لالء الاسلام"
    normalize_ligature(text)

    import pyarabic.number
    an = pyarabic.number.ArNumbers()
    an.int2str('125')

    # === Main loop ===
    pyarabic.number.number2ordinal(125)

    from pyarabic.number import text2number
    text2number(u"خمسمئة وثلاث وعشرون")
    text2number(u'المئة والخامس والعشرون')
    text2number(u'مئة و خمس و عشرون')


    from pyarabic.number import extract_number_phrases
    extract_number_phrases(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")

    extract_number_phrases(u"خمسمئة وثلاث وعشرون")
    extract_number_phrases(u'المئة والخامس والعشرون')
    extract_number_phrases(u'مئة و خمس و عشرون')


    from pyarabic.number import extract_number_context
    extract_number_context(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")

    extract_number_context(u"خمسمئة وثلاث وعشرون")
    extract_number_context(u'المئة والخامس والعشرون'.replace('ال', ''))
    extract_number_context(u'مئة و خمس و عشرون')

    import pyarabic.trans
    text = u'۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789'

    from openiti.helper.ara import normalize_ara_heavy




    pyarabic.trans.normalize_digits(text, source='all', out='west')


    text =u"""السلام عليكم how are you, لم اسمع أخبارك منذ مدة, where are you going"""
    pyarabic.trans.segment_language(text)

    from pyarabic import araby
    from pyarabic.number import detect_numbers
    wordlist = araby.tokenize(u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا")
    detect_numbers(wordlist)

    wordlist = araby.tokenize(text)
    detect_numbers(wordlist)

    def preprocessing_numbers(text = u"وجدت خمسمئة وثلاثة وعشرين دينارا فاشتريت ثلاثة عشر دفترا ۰۱۲۳۴۵۶۷۸۹ ٠١٢٣٤٥٦٧٨٩ 123456789"):   
        text = normalize_ara_heavy(text)
        
        text = pyarabic.trans.normalize_digits(str(text), source='all', out='west')
        extract_number_context(text)
        extract_number_phrases(text)
        text2number(text)
        
        an.int2str("123456789")
        
        match = re.search(r'\d+',text)
        if match:
            match[0]
        
        
        text = strip_tatweel(text).replace('ال', '') 
        text = text2number(text)
        
        
        return number

    preprocessing_numbers(u"خمسمئة وثلاث وعشرون")
    preprocessing_numbers(u'المئة والخامس والعشرون')
    preprocessing_numbers(u'مئة و خمس و عشرون')


    from pyarabic.number import number2text

    number2text(text)
    
    
    

def load_models():
    """Load necessary NLP models."""
    nlp = spacy.load("xx_sent_ud_sm")  # Universal model supporting Arabic
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return nlp, model

def compute_similarity(embeddings):
    """Compute cosine similarity between consecutive sentence embeddings."""
    similarities = [
        np.dot(embeddings[i], embeddings[i + 1]) / (np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i + 1]))
        for i in range(len(embeddings) - 1)
    ]
    return similarities

def chunk_text(text, threshold=0.75):
    """Segment Arabic text into semantic chunks based on similarity."""
    nlp, model = load_models()
    
    # Sentence segmentation
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    
    # Compute sentence embeddings
    embeddings = model.encode(sentences)
    similarities = compute_similarity(embeddings)
    
    # Create chunks
    chunks, current_chunk = [], []
    for i, sentence in enumerate(sentences):
        current_chunk.append(sentence)
        if i < len(similarities) and similarities[i] < threshold:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks



print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"PyTorch CUDA version: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")

from dotenv import load_dotenv
import os

load_dotenv()  # defaults to looking for `.env` in current dir

# Now you can safely access the token
hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")

# Optional: set it explicitly in env vars (if some library expects it that way)
os.environ["HUGGING_FACE_HUB_TOKEN"] = hf_token
from transformers import AutoTokenizer, AutoModelForTokenClassification
# CAMeL-Lab/bert-base-arabic-camelbert-ca-ner
# CAMeL-Lab/bert-base-arabic-camelbert-mix-ner

# Load your desired tokenizer
tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")

# Tokenize a sample text and check how many tokens it generates
text = "هذا مثال على النص باللغة العربية."
tokens = tokenizer(text, return_tensors="pt")
print("Number of tokens in input:", tokens["input_ids"].shape[1])

ner = pipeline("ner", model="CAMeL-Lab/bert-base-arabic-camelbert-mix-ner", device=0)

text = "هدفي أن أكون عالِم بيانات ناجح في شركة جوجل."
entities = ner(text)

combined_entities = combine_entities(entities)

search_dates(
    text = 'The first artificial Earth satellite was launched on 4 اكتوبر .', 
    languages=['ar', 'en'], 
    settings=None, 
    add_detected_language=False, 
    detect_languages_function=None
    )

search_dates('The first artificial Earth satellite was launched on 4 October 1957.')

# [('on 4 October 1957', datetime.datetime(1957, 10, 4, 0, 0))]
search_dates('The first artificial Earth satellite was launched on 4 October 1957.',
             add_detected_language=True)


search_dates("The client arrived to the office for the first time in March 3rd, 2004 "
             "and got serviced, after a couple of months, on May 6th 2004, the customer "
             "returned indicating a defect on the part")


text = "The meeting happened 2 days ago and we need to follow up."
dt_list = []
dates = search_dates(text)

for dt in dates:
    date_str = dt[0]
    print(date_str)
    
    # Find the position of the date expression in the text
    match = re.search(r'\b' + re.escape(date_str) + r'\b', text)
    if match:
        x = match.start()
        y = match.end()
        
        dt_list.append({
            'entity': 'DATE', 
            'name': date_str, 
            'score': "", 
            'start': x, 
            'end': y        
        })
        
text[21:35]



if __name__ == "__main__":
    sample_text = "We had a meeting 2 days ago and we need another one next Friday."
    date_entities = extract_dates_with_positions(sample_text)
    
    for entity in date_entities:
        print(f"Found '{entity['name']}' at positions {entity['start']}-{entity['end']}")
        print(f"Parsed as: {entity['value']}")
        print()

    from camel_tools.morphology.database import MorphologyDB
    from camel_tools.morphology.analyzer import Analyzer

    db = MorphologyDB.builtin_db()

    # Create analyzer with no backoff
    analyzer = Analyzer(db)


    # Create analyzer with NOAN_PROP backoff
    analyzer = Analyzer(db, 'NOAN_PROP')

    # or
    analyzer = Analyzer(db, backoff='NOAN_PROP')


    # To analyze a word, we can use the analyze() method
    analyses = analyzer.analyze('شارع')

    from camel_tools.ner import NERecognizer

    ner = NERecognizer.pretrained()

    # Predict the labels of a single sentence.
    # The sentence must be pretokenized by whitespace and punctuation.
    sentence = 'إمارة أبوظبي هي إحدى إمارات دولة الإمارات العربية المتحدة السبع .'.split()
    labels = ner.predict_sentence(sentence)

    # Print the list of token-label pairs
    print(list(zip(sentence, labels)))




    # Use a pipeline as a high-level helper
    from transformers import pipeline

    pipe = pipeline("token-classification", model="CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")    
    from transformers import AutoTokenizer, AutoModelForTokenClassification

    tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")
    model = AutoModelForTokenClassification.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix-ner")


    from camel_tools.ner import NERecognizer
    from camel_tools.tokenizers.word import simple_word_tokenize


    # Load CAMeL NER
    ner = NERecognizer.pretrained()

    # Text
    sentence = simple_word_tokenize('إمارة أبوظبي هي إحدى إمارات دولة الإمارات العربية المتحدة السبع')

    # Predict
    entities = ner.predict_sentence(sentence)

    combined_entities = combine_entities(entities)


    # Print
    for token, label in zip(sentence, labels):
        print(f"{token} -> {label}")



    from transformers import AutoTokenizer, AutoModelForTokenClassification
    from transformers import pipeline

    # Initialize NER pipeline
    ner = pipeline(
        "ner",
        model="CAMeL-Lab/bert-base-arabic-camelbert-msa",
        tokenizer="CAMeL-Lab/bert-base-arabic-camelbert-msa"
    )

    # Example text
    text = "يعيش محمد في دبي ويعمل في شركة جوجل"
    results = ner(text)

    # Process and display results
    for result in results:
        print(f"Entity: {result['word']}, Type: {result['entity']}, Score: {result['score']:.2f}")


    # Text Preprocessing and Analysis:

        
    import torch
    from transformers import AutoTokenizer, AutoModel
    import numpy as np

    def get_text_embedding(text, model, tokenizer):
        # Tokenize and prepare input
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        # Get model outputs
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Get embeddings from last hidden state
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings

    # Initialize model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix")
    model = AutoModel.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix")

    # Example texts
    texts = [
        "مرحباً بكم في عالم الذكاء الاصطناعي",
        "تعلم الآلة هو مستقبل التكنولوجيا"
    ]

    # Get embeddings
    embeddings = [get_text_embedding(text, model, tokenizer) for text in texts]
