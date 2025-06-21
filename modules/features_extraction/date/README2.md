# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 17:42:59 2025

@author: m
"""

Here are common regex patterns for matching dates in text:

## Basic Date Formats

**MM/DD/YYYY or MM-DD-YYYY:**
```regex
\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b
```

**YYYY-MM-DD (ISO format):**
```regex
\b\d{4}-\d{2}-\d{2}\b
```

**DD/MM/YYYY or DD-MM-YYYY:**
```regex
\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b
```

## More Specific Patterns

**Strict MM/DD/YYYY (with proper month/day ranges):**
```regex
\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])[/-]\d{4}\b
```

**Multiple separators (/, -, or .):**
```regex
\b\d{1,2}[/.-]\d{1,2}[/.-]\d{4}\b
```

**With optional 2-digit years:**
```regex
\b\d{1,2}[/-]\d{1,2}[/-](\d{4}|\d{2})\b
```

## Text-based Dates

**Month name formats (Jan 15, 2024 or January 15, 2024):**
```regex
\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b
```

**Full month names:**
```regex
\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b
```

## Universal Pattern

**Catches most common formats:**
```regex
\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4})\b
```

The `\b` word boundaries help ensure you're matching complete dates and not parts of longer numbers. Choose the pattern that best matches your expected date format!


Here are regex patterns that include day names with dates:

## Day Names + Date Formats

**Day name followed by date (Monday, Jan 15, 2024):**
```regex
\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b
```

**Abbreviated day names (Mon, Jan 15, 2024):**
```regex
\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b
```

**Day name with numeric dates (Monday, 01/15/2024):**
```regex
\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b
```

**Abbreviated day with numeric dates (Mon, 01/15/2024):**
```regex
\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b
```

## Full Month Names with Days

**Full day and month names (Monday, January 15, 2024):**
```regex
\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b
```

## Case-Insensitive Versions

**Case-insensitive day + abbreviated month:**
```regex
\b(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday),?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b
```

**Case-insensitive abbreviated day + month:**
```regex
\b(?i)(mon|tue|wed|thu|fri|sat|sun),?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b
```

## Universal Pattern with Days

**Comprehensive pattern (catches most day+date combinations):**
```regex
\b(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun),?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4})\b
```

## Alternative Format (Date followed by day)

**Date first, then day (Jan 15, 2024 (Monday)):**
```regex
\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\s*\(?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\)?\b
```

The `(?i)` flag makes the pattern case-insensitive. Choose the pattern that matches your specific text format!

Here are regex patterns for Arabic date variants:

## Arabic/Islamic Calendar Months

**Arabic month names (transliterated):**
```regex
\b(?i)(muharram|safar|rabi al-awwal|rabi al-thani|jumada al-awwal|jumada al-thani|rajab|shaban|ramadan|shawwal|dhu al-qadah|dhu al-hijjah)\s+\d{1,2},?\s+\d{3,4}\s*(ah|هـ)?\b
```

**Abbreviated Arabic months:**
```regex
\b(?i)(muh|saf|rab1|rab2|jum1|jum2|raj|sha|ram|shaw|dhiq|dhih)\s+\d{1,2},?\s+\d{3,4}\s*(ah|هـ)?\b
```

## Arabic Day Names

**Arabic day names (transliterated):**
```regex
\b(?i)(al-ahad|al-ithnayn|al-thulatha|al-arba|al-khamis|al-jumah|as-sabt|ahad|ithnayn|thulatha|arba|khamis|jumah|sabt)\b
```

**Day + Arabic date:**
```regex
\b(?i)(al-ahad|al-ithnayn|al-thulatha|al-arba|al-khamis|al-jumah|as-sabt),?\s+(muharram|safar|rabi al-awwal|rabi al-thani|jumada al-awwal|jumada al-thani|rajab|shaban|ramadan|shawwal|dhu al-qadah|dhu al-hijjah)\s+\d{1,2},?\s+\d{3,4}\s*(ah|هـ)?\b
```

## Arabic Script Patterns

**Arabic numerals and text (if your text contains Arabic script):**
```regex
[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+\s*[٠-٩]+\s*[\u0600-\u06FF]+\s*[٠-٩]+
```

**Arabic-Indic numerals (٠-٩):**
```regex
\b[٠-٩]{1,2}[/-][٠-٩]{1,2}[/-][٠-٩]{2,4}\b
```

## Mixed Arabic-English Patterns

**English day + Arabic month:**
```regex
\b(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun),?\s+(muharram|safar|rabi al-awwal|rabi al-thani|jumada al-awwal|jumada al-thani|rajab|shaban|ramadan|shawwal|dhu al-qadah|dhu al-hijjah)\s+\d{1,2},?\s+\d{3,4}\s*(ah|هـ)?\b
```

**Arabic day + Gregorian date:**
```regex
\b(?i)(al-ahad|al-ithnayn|al-thulatha|al-arba|al-khamis|al-jumah|as-sabt),?\s+\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b
```

## Regional Variations

**Persian/Farsi month names:**
```regex
\b(?i)(farvardin|ordibehesht|khordad|tir|mordad|shahrivar|mehr|aban|azar|dey|bahman|esfand)\s+\d{1,2},?\s+\d{3,4}\s*(ap|ه\.ش)?\b
```

**Turkish Islamic months:**
```regex
\b(?i)(muharrem|safer|rebiulevvel|rebiulahir|cemaziyelevvel|cemaziyelahir|recep|şaban|ramazan|şevval|zilkade|zilhicce)\s+\d{1,2},?\s+\d{3,4}\s*(h)?\b
```

## Universal Arabic Date Pattern

**Comprehensive pattern for various Arabic date formats:**
```regex
\b(?i)((al-ahad|al-ithnayn|al-thulatha|al-arba|al-khamis|al-jumah|as-sabt|ahad|ithnayn|thulatha|arba|khamis|jumah|sabt),?\s+)?(muharram|safar|rabi al-awwal|rabi al-thani|jumada al-awwal|jumada al-thani|rajab|shaban|ramadan|shawwal|dhu al-qadah|dhu al-hijjah|muh|saf|rab1|rab2|jum1|jum2|raj|sha|ram|shaw|dhiq|dhih)\s+\d{1,2},?\s+\d{3,4}\s*(ah|هـ|h)?\b
```

**Note:** The Hijri calendar years are typically 3-4 digits (current year is around 1446 AH), which is why the year pattern uses `\d{3,4}`.

Choose the pattern that best matches your specific Arabic date format and transliteration style!

Here are comprehensive regex patterns for Arabic Hijri dates with month and day names in Arabic script:

## Arabic Hijri Month Names (Arabic Script)

**Arabic Hijri months:**
```regex
\b(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\b
```

## Arabic Day Names (Arabic Script)

**Arabic day names:**
```regex
\b(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|أحد|اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت)\b
```

## Complete Arabic Hijri Date Patterns

**Day + Date + Month + Year + Era:**
```regex
\b(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|أحد|اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت)،?\s*[٠-٩\d]{1,2}\s+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*[٠-٩\d]{3,4}\s*(هـ|ه|AH|CE|AD|م)\b
```

**Month + Day + Year + Era (without day name):**
```regex
\b[٠-٩\d]{1,2}\s+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*[٠-٩\d]{3,4}\s*(هـ|ه|AH|CE|AD|م)\b
```

## Mixed Numeral Systems

**Arabic-Indic numerals (٠-٩) with Arabic text:**
```regex
\b(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت)،?\s*[٠-٩]{1,2}\s+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*[٠-٩]{3,4}\s*هـ\b
```

**Western numerals (0-9) with Arabic text:**
```regex
\b(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت)،?\s*\d{1,2}\s+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*\d{3,4}\s*(هـ|AH)\b
```

## Era Abbreviations

**Multiple era formats:**
```regex
\b[٠-٩\d]{1,2}\s+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)\s*[٠-٩\d]{3,4}\s*(هـ|ه|AH|H|هجرية|الهجرة|للهجرة)\b
```

**Gregorian dates in Arabic:**
```regex
\b[٠-٩\d]{1,2}\s+(يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\s*[٠-٩\d]{4}\s*(م|CE|AD|ميلادية|الميلاد|للميلاد)\b
```

## Alternative Month Name Variations

**Alternative spellings and shortened forms:**
```regex
\b[٠-٩\d]{1,2}\s+(محرم|صفر|ر\.أول|ر\.آخر|ج\.أولى|ج\.آخرة|رجب|شعبان|رمضان|شوال|ق\.دة|ح\.جة)\s*[٠-٩\d]{3,4}\s*هـ\b
```

## Universal Arabic Date Pattern

**Comprehensive pattern for all variations:**
```regex
\b((الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|أحد|اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت)،?\s*)?[٠-٩\d]{1,2}[/\-\s]+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة|يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)[/\-\s]*[٠-٩\d]{3,4}\s*(هـ|ه|م|AH|CE|AD|H|هجرية|ميلادية|الهجرة|الميلاد|للهجرة|للميلاد)?\b
```

## Common Date Separators in Arabic

**With various separators:**
```regex
\b[٠-٩\d]{1,2}[/\-\s\.](محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة)[/\-\s\.][٠-٩\d]{3,4}\s*هـ\b
```

**Notes:**
- `[٠-٩\d]` matches both Arabic-Indic numerals (٠-٩) and Western numerals (0-9)
- `هـ` is the common abbreviation for Hijri era
- `م` is used for Gregorian dates (ميلادية)
- The patterns account for optional commas and various spacing

Choose the pattern that best matches your specific Arabic text format!


Here are regex patterns that include Arabic month names like حزيران (Levantine/regional Arabic month names):

## Levantine/Regional Arabic Month Names

**Levantine months (used in Syria, Lebanon, Palestine, Jordan):**
```regex
\b(كانون الثاني|شباط|آذار|نيسان|أيار|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\b
```

**Iraqi/Gulf Arabic months:**
```regex
\b(كانون الثاني|شباط|آذار|نيسان|مايس|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\b
```

## Complete Date Patterns with Regional Months

**Day + Regional month + Year:**
```regex
\b(الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت)،?\s*[٠-٩\d]{1,2}\s+(كانون الثاني|شباط|آذار|نيسان|أيار|مايس|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\s*[٠-٩\d]{4}\s*(م|CE|AD|ميلادية)?\b
```

**Regional month + Day + Year (without day name):**
```regex
\b[٠-٩\d]{1,2}\s+(كانون الثاني|شباط|آذار|نيسان|أيار|مايس|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\s*[٠-٩\d]{4}\s*(م|CE|AD|ميلادية)?\b
```

## Egyptian/North African Month Names

**Egyptian Arabic months:**
```regex
\b(يناير|فبراير|مارس|إبريل|مايو|يونيه|يوليه|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\b
```

**Maghrebi (North African) variations:**
```regex
\b(جانفي|فيفري|مارس|أفريل|ماي|جوان|جويلية|أوت|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\b
```

## Comprehensive Universal Pattern

**All Arabic month variations (Hijri + Regional + Standard):**
```regex
\b((الأحد|الاثنين|الثلاثاء|الأربعاء|الخميس|الجمعة|السبت|أحد|اثنين|ثلاثاء|أربعاء|خميس|جمعة|سبت)،?\s*)?[٠-٩\d]{1,2}[/\-\s]+(محرم|صفر|ربيع الأول|ربيع الآخر|ربيع الثاني|جمادى الأولى|جمادى الآخرة|جمادى الثانية|رجب|شعبان|رمضان|شوال|ذو القعدة|ذو الحجة|كانون الثاني|شباط|آذار|نيسان|أيار|مايس|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول|يناير|فبراير|مارس|إبريل|أبريل|مايو|يونيه|يوليه|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر|جانفي|فيفري|أفريل|ماي|جوان|جويلية|أوت)[/\-\s]*[٠-٩\d]{3,4}\s*(هـ|ه|م|AH|CE|AD|H|هجرية|ميلادية)?\b
```

## Regional Specific Patterns

**Levantine specific (Syria, Lebanon, Palestine, Jordan):**
```regex
\b[٠-٩\d]{1,2}\s+(كانون الثاني|شباط|آذار|نيسان|أيار|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\s*[٠-٩\d]{4}\b
```

**Iraqi/Gulf specific:**
```regex
\b[٠-٩\d]{1,2}\s+(كانون الثاني|شباط|آذار|نيسان|مايس|حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول)\s*[٠-٩\d]{4}\b
```

**Maghrebi specific:**
```regex
\b[٠-٩\d]{1,2}\s+(جانفي|فيفري|مارس|أفريل|ماي|جوان|جويلية|أوت|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\s*[٠-٩\d]{4}\b
```

## Alternative Spellings

**Common alternative spellings:**
```regex
\b[٠-٩\d]{1,2}\s+(كانون ثاني|كانون أول|تشرين أول|تشرين ثاني|حزيران|تموز|آب|أيلول|نيسان|أيار|شباط|آذار)\s*[٠-٩\d]{4}\b
```

## Mixed Format (Arabic months with English/Western context)

**Arabic months with Western calendar indicators:**
```regex
\b[٠-٩\d]{1,2}\s+(حزيران|تموز|آب|أيلول|تشرين الأول|تشرين الثاني|كانون الأول|كانون الثاني|شباط|آذار|نيسان|أيار)\s*[٠-٩\d]{4}\s*(CE|AD|م)\b
```

**Month name mapping for reference:**
- كانون الثاني = January
- شباط = February  
- آذار = March
- نيسان = April
- أيار/مايس = May
- حزيران = June
- تموز = July
- آب = August
- أيلول = September
- تشرين الأول = October
- تشرين الثاني = November
- كانون الأول = December

These patterns will catch regional Arabic month names commonly used across different Arab countries!