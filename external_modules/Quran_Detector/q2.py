# -*- coding: utf-8 -*-
"""
Created on Sun Jun 15 00:08:18 2025

@author: m
"""

import json

# 🔹 1. Load Uthmani Quran flat structure
def load_uthmani_quran(filepath='uthmani.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['quran']

# 🔹 2. Arabic Surah Name to Number Mapping
name_to_number = {
    'الفاتحة': 1, 'البقرة': 2, 'آل عمران': 3, 'النساء': 4, 'المائدة': 5, 'الأنعام': 6,
    'الأعراف': 7, 'الأنفال': 8, 'التوبة': 9, 'يونس': 10, 'هود': 11, 'يوسف': 12,
    'الرعد': 13, 'إبراهيم': 14, 'الحجر': 15, 'النحل': 16, 'الإسراء': 17, 'الكهف': 18,
    'مريم': 19, 'طه': 20, 'الأنبياء': 21, 'الحج': 22, 'المؤمنون': 23, 'النور': 24,
    'الفرقان': 25, 'الشعراء': 26, 'النمل': 27, 'القصص': 28, 'العنكبوت': 29, 'الروم': 30,
    'لقمان': 31, 'السجدة': 32, 'الأحزاب': 33, 'سبإ': 34, 'فاطر': 35, 'يس': 36,
    'الصافات': 37, 'ص': 38, 'الزمر': 39, 'غافر': 40, 'فصلت': 41, 'الشورى': 42,
    'الزخرف': 43, 'الدخان': 44, 'الجاثية': 45, 'الأحقاف': 46, 'محمد': 47, 'الفتح': 48,
    'الحجرات': 49, 'ق': 50, 'الذاريات': 51, 'الطور': 52, 'النجم': 53, 'القمر': 54,
    'الرحمن': 55, 'الواقعة': 56, 'الحديد': 57, 'المجادلة': 58, 'الحشر': 59,
    'الممتحنة': 60, 'الصف': 61, 'الجمعة': 62, 'المنافقون': 63, 'التغابن': 64,
    'الطلاق': 65, 'التحريم': 66, 'الملك': 67, 'القلم': 68, 'الحاقة': 69,
    'المعارج': 70, 'نوح': 71, 'الجن': 72, 'المزمل': 73, 'المدثر': 74, 'القيامة': 75,
    'الإنسان': 76, 'المرسلات': 77, 'النبأ': 78, 'النازعات': 79, 'عبس': 80,
    'التكوير': 81, 'الانفطار': 82, 'المطففين': 83, 'الانشقاق': 84, 'البروج': 85,
    'الطارق': 86, 'الأعلى': 87, 'الغاشية': 88, 'الفجر': 89, 'البلد': 90, 'الشمس': 91,
    'الليل': 92, 'الضحى': 93, 'الشرح': 94, 'التين': 95, 'العلق': 96, 'القدر': 97,
    'البينة': 98, 'الزلزلة': 99, 'العاديات': 100, 'القارعة': 101, 'التكاثر': 102,
    'العصر': 103, 'الهمزة': 104, 'الفيل': 105, 'قريش': 106, 'الماعون': 107,
    'الكوثر': 108, 'الكافرون': 109, 'النصر': 110, 'المسد': 111, 'الإخلاص': 112,
    'الفلق': 113, 'الناس': 114
}

# 🔹 3. Lookup function
def uthmani_lookup(quran_data, sura_name, verse_num):
    sura_number = name_to_number.get(sura_name.strip())
    if not sura_number:
        print(f"❌ Surah not found: {sura_name}")
        return None
    for verse in quran_data:
        if verse['chapter'] == sura_number and verse['verse'] == verse_num:
            return verse['text']
    print(f"❌ Verse not found: {sura_name}:{verse_num}")
    return None

# 🔹 4. Apply and replace with formatting
def apply_uthmani_to_text(original_text, matches, quran_data, wrap_html=True):
    # Reverse sort so earlier replacements don’t shift later offsets
    matches_sorted = sorted(matches, key=lambda m: m['startInText'], reverse=True)

    for m in matches_sorted:
        start = m['startInText']
        end = m['endInText']
        sura = m['aya_name']
        verse_num = m['aya_start']

        uthmani_text = uthmani_lookup(quran_data, sura, verse_num)
        if not uthmani_text:
            continue

        formatted = f"۞ ﴿{uthmani_text}﴾ ۝ {sura}:{verse_num}"
        if wrap_html:
            formatted = f'<span class="quran-verse">{formatted}</span>'

        original_text = original_text[:start] + formatted + original_text[end:]

    return original_text


if __name__ == "__main__":
    # Example text & matches
    text = "قال الله الذين يحملون العرش ومن حوله يسبحون بحمد ربهم واذكر ربك اذا نسيت"

    matches = [
        {
            'aya_name': 'غافر',
            'verses': ['الذين يحملون العرش ومن حوله يسبحون بحمد ربهم'],
            'errors': [[('يسبحو', 'يسبحون', 18)]],
            'startInText': 9,
            'endInText': 55,
            'aya_start': 7,
            'aya_end': 7
        },
        {
            'aya_name': 'الكهف',
            'verses': ['واذكر ربك اذا نسيت'],
            'errors': [[]],
            'startInText': 56,
            'endInText': 75,
            'aya_start': 24,
            'aya_end': 24
        }
    ]

    quran_data = load_uthmani_quran("uthmani.json")
    updated_text = apply_uthmani_to_text(text, matches, quran_data, wrap_html=True)
    print(updated_text)
