# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 17:24:51 2025

@author: m.lotfi

"""

import datetime
import gzip
import json
import logging
import os
import re
import time
from copy import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
import selenium
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from bson import ObjectId
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# [custom import]
# 📌 **data_extraction_tags**
from scraping.data_extraction_tags import (
    get_author,
    get_chapters_tree,
    get_hadith_base_info,
    get_hadith_info,
    get_hadith_info_thaskeel,
    get_hadith_narrators,
    get_page_navigation,
    get_page_volume,
    get_tkhreg_hadith_api,
    get_toc_path,
    get_narrator_data_from_tags,
)

# 📌 **data_proccessing**
from scraping.data_proccessing import (
    bytes_to_human_readable,
    clean_html,
    clean_text,
    extract_number_before_haddathana,
    extract_text_from_html,
    find_common_columns,
    get_h_wa_haddathana_count_occurrences,
    get_url_components,
    remove_diacritics_and_spaces,
    remove_diacritics_spaces_and_normalize_numbers,
    divide_pages_into_parts,
)

# 📌 **handles_files**
from scraping.handles_files import (
    convert_to_serializable,
    is_files_saved,
    save_html_files,
    to_csv_pd,
    to_html_append,
    to_json_csv,
    to_json_with_arabic,

)

# 📌 **html_proccessing**
from scraping.html_proccessing import (
    parse_hadith_isnad,
    parse_hadith_page,
)

# 📌 **time_date**
from scraping.time_date import (
    generate_random_delay_gauss,
)

# 📌 **web_automation**
from scraping.web_automation import (
    create_human_like_browser,
    get_api_response,
    get_driver,
    handle_modal_interaction,
    is_modal_open,
    move_mouse_randomly,
    simulate_human_scroll,
    simulate_human_typing,
    try_close_modal_js,
    try_open_modal_js,
    try_open_modal,
    scrape_pages
)

# Configure custom logging if needed
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='modal_interactions.log'
)

## **✅ Setting initial variables**
wait_time = 10
timeout   = 10


from pprint import pprint

from urllib.parse import urlparse, parse_qs

def to_csv(df, csv_path):
    """Save DF to file with proper encoding for Arabic text"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path


def simple_extraction(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')
    
    # Find book_id
    book_id = next((seg for seg in path_segments if seg.isdigit()), None)
    
    # Parse query parameters
    query_params = parse_qs(parsed_url.query)
    
    return book_id, query_params.get('idfrom', [None])[0], query_params.get('idto', [None])[0]

# More comprehensive version with additional patterns
def advanced_date_standardization(date_str):
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
# subject_info = subjects[0]
def extract_book_details(raw_html, subject_info, url):
    soup = BeautifulSoup(raw_html, 'html.parser')
    book_list = []

    # Find the UL with book items
    div = soup.find('div', id="cat_books")
    if div:
        # Find all list items
        li_elements = div.find_all('div', class_="book_item margin-top-10")
        len(li_elements)
        
        # li_element = li_elements[0]
    
        for li_element in li_elements:
            result = {}
            book_meta = li_element.find("a", class_="book_title text-primary")
            if book_meta :
                result['book_title'] = book_meta.text.strip()
                result['book_url']   = book_meta.get("href", "")
                result['book_id']    = result['book_url'].split("/")[-1] if result['book_url'] else ""
                
            author_meta = li_element.find("a", class_="text-gray")
            if author_meta :
                result['author']      = author_meta.text.strip()
                result['author_url']   = author_meta.get("href", "")
                result['author_id']    = result['author_url'].split("/")[-1] if result['author_url'] else ""
            
            p = li_element.find("p").text
            
            lines = p.strip().split('\n')
            
            for line in lines:
                if line.startswith("الكتاب:"):
                    match = re.match(r'الكتاب:\s*([^\(]+)\s*\((.+)\)', line)
                    if match:
                        result['p_title'] = match.group(1).strip()
                        result['p_title_note'] = match.group(2).strip()
                    else:
                        result['p_title'] = line[len("الكتاب:"):].strip()
                elif line.startswith("المؤلف:"):
                    match = re.match(r'المؤلف:\s*([^\(]+)\s*\((.+)\)', line)
                    if match:
                        result['p_author'] = match.group(1).strip()
                        result['p_author_died'] = match.group(2).strip()
                    else:
                        result['p_author'] = line[len("المؤلف:"):].strip()
                elif line.startswith("المحقق:") or line.startswith("تحقيق:"):
                    result['p_verified_by'] = line.split(":", 1)[1].strip()
                elif line.startswith("أصل الكتاب:"):
                    result['book_origin'] = line.split(":", 1)[1].strip()
                elif line.startswith("طبع على نفقة:"):
                    result['sponsored_by'] = line.split(":", 1)[1].strip()
                elif line.startswith("الناشر:"):
                    result['p_publisher'] = line[len("الناشر:"):].strip()
                elif line.startswith("الطبعة:"):
                    match = re.match(r'الطبعة:\s*([^\،,]+)[،,]\s*(.+)', line)
                    if match:
                        result['p_edition'] = match.group(1).strip()
                        result['p_published'] = match.group(2).strip()
                    else:
                        result['p_edition'] = line[len("الطبعة:"):].strip()
                
                elif line.startswith("عدد الأجزاء:"):
                    result['p_volumes'] = line[len("عدد الأجزاء:"):].strip()
                elif line.startswith("بإشراف:"):
                    result['supervisor'] = line.split(":", 1)[1].strip()
                elif line.startswith("رسالة:") or line.startswith("أطروحة:"):
                    result['thesis_type'] = line.split(":", 1)[1].strip()
                elif line.startswith("قدم له:"):
                    result['preface_by'] = line.split(":", 1)[1].strip()
                elif line.startswith("أطروحة:"):
                    rest = line.split(":", 1)[1].strip()
                    # Try to extract supervisor and date
                    parts = rest.split("،")
                    for part in parts:
                        part = part.strip()
                        if part.startswith("بإشراف"):
                            result['supervisor'] = part.replace("بإشراف", "").strip(" :،")
                        elif re.search(r'\d{3,4}\s*هـ', part):  # e.g., ١٤٤٣ هـ
                            result['published_years'] = part.strip()
                        else:
                            result['thesis_type'] = part.strip()
                elif re.match(r'راجعه(?:\s+ودققه)?\s*[:/،]?', line):
                    reviewer = re.sub(r'^راجعه(?:\s+ودققه)?\s*[:/،]?', '', line).strip()
                    result['reviewer'] = reviewer
                elif line.startswith("عدد الصفحات:"):
                    result['p_pages'] = line[len("عدد الصفحات:"):].strip()
                elif line.startswith("[") and line.endswith("]"):
                    result['p_note'] = line[1:-1].strip()
            result['book_dtails'] = p
            
            result['category'] = subject_info['category']
            result['category_id'] = subject_info['category_id']
            result['category_book_count'] = subject_info['book_count']
            result['category_url'] = url
            
            print(result['book_dtails'])
            
            print('\n -------------------------------')
            
            # pprint(result)
            book_list.append(result)
        
    return book_list


# Create dictionary of subjects
subjects = [
    {
        "category": "العقيدة",
        "book_count": 803,
        "category_id": 1
    },
    {
        "category": "الفرق والردود",
        "book_count": 151,
        "category_id": 2
    },
    {
        "category": "التفسير",
        "book_count": 271,
        "category_id": 3
    },
    {
        "category": "علوم القرآن وأصول التفسير",
        "book_count": 309,
        "category_id": 4
    },
    {
        "category": "التجويد والقراءات",
        "book_count": 151,
        "category_id": 5
    },
    {
        "category": "كتب السنة",
        "book_count": 1240,
        "category_id": 6
    },
    {
        "category": "شروح الحديث",
        "book_count": 264,
        "category_id": 7
    },
    {
        "category": "التخريج والأطراف",
        "book_count": 128,
        "category_id": 8
    },
    {
        "category": "العلل والسؤلات الحديثية",
        "book_count": 76,
        "category_id": 9
    },
    {
        "category": "علوم الحديث",
        "book_count": 320,
        "category_id": 10
    },
    {
        "category": "أصول الفقه",
        "book_count": 247,
        "category_id": 11
    },
    {
        "category": "علوم الفقه والقواعد الفقهية",
        "book_count": 57,
        "category_id": 12
    },
    {
        "category": "المنطق",
        "book_count": 11,
        "category_id": 13
    },
    {
        "category": "الفقه الحنفي",
        "book_count": 85,
        "category_id": 14
    },
    {
        "category": "الفقه المالكي",
        "book_count": 86,
        "category_id": 15
    },
    {
        "category": "الفقه الشافعي",
        "book_count": 87,
        "category_id": 16
    },
    {
        "category": "الفقه الحنبلي",
        "book_count": 151,
        "category_id": 17
    },
    {
        "category": "الفقه العام",
        "book_count": 206,
        "category_id": 18,
    },
    {
        "category": "مسائل فقهية",
        "book_count": 424,
        "category_id": 19
    },
    {
        "category": "السياسة الشرعية والقضاء",
        "book_count": 100,
        "category_id": 20
    },
    {
        "category": "الفرائض والوصايا",
        "book_count": 28,
        "category_id": 21
    },
    {
        "category": "الفتاوى",
        "book_count": 64,
        "category_id": 22
    },
    {
        "category": "الرقائق والآداب والأذكار",
        "book_count": 623,
        "category_id": 23
    },
    {
        "category": "السيرة النبوية",
        "book_count": 187,
        "category_id": 24
    },
    {
        "category": "التاريخ",
        "book_count": 202,
        "category_id": 25
    },
    {
        "category": "التراجم والطبقات",
        "book_count": 574,
        "category_id": 26
    },
    {
        "category": "الأنساب",
        "book_count": 52,
        "category_id": 27
    },
    {
        "category": "البلدان والرحلات",
        "book_count": 93,
        "category_id": 28
    },
    {
        "category": "كتب اللغة",
        "book_count": 79,
        "category_id": 29
    },
    {
        "category": "الغريب والمعاجم",
        "book_count": 134,
        "category_id": 30
    },
    {
        "category": "النحو والصرف",
        "book_count": 213,
        "category_id": 31
    },
    {
        "category": "الأدب",
        "book_count": 406,
        "category_id": 32
    },
    {
        "category": "العروض والقوافي",
        "book_count": 9,
        "category_id": 33
    },
    {
        "category": "الشعر ودواوينه",
        "book_count": 25,
        "category_id": 34
    },
    {
        "category": "البلاغة",
        "book_count": 44, 
        "category_id": 35
    },
    {
        "category": "الجوامع",
        "book_count": 136,
        "category_id": 36
    },
    {
        "category": "فهارس الكتب والأدلة",
        "book_count": 101,
        "category_id": 37
    },
    {
        "category": "الطب",
        "book_count": 14,
        "category_id": 38
    },
    {
        "category": "كتب عامة",
        "book_count": 356,
        "category_id": 39
    },
    {
        "category": "علوم أخرى",
        "book_count": 26,
        "category_id": 40
    }
]


# Function to fetch and process URLs
def process_subjects(subjects):   
    
    all_books = []
    
    # ✅ Initialize browser
    driver = create_human_like_browser()
    
    for subject_info in subjects:
        # Get URL
        url = f"https://shamela.ws/category/{subject_info['category_id']}"
        category_id = subject_info['category_id']
        
        print(f"Processing {subject_info['category']} (ID: {category_id})")
        
        # ✅ Open target website
        driver.get(url)
        
        # Get the raw HTML
        raw_html = driver.page_source
        
        # ✅ Save Save clean html
        with open(f'./shamela/raw_html/cat{category_id}.html', "w", encoding="utf-8") as file:
            file.write(raw_html)
        
        # Polite delay between requests
        time.sleep(2)         

    # ✅ Close browser
    driver.quit()    
    
    # return all_books        

if __name__ == "__main__":
    
    # process_subjects(subjects)
    # # ✅ Close browser
    # driver.quit()
     
    
    all_books = []
    # set(book_df["publication_date"])
    # category_id = 1
    for subject_info in subjects:
        # Get URL
        url = f"https://shamela.ws/category/{subject_info['category_id']}"
        category_id = subject_info['category_id']
        
        
        print(f"Processing {subject_info['category']} (ID: {category_id})")
        
        
        with open(f'./shamela/raw_html/cat{category_id}.html', "r", encoding="utf-8") as file:
            raw_html = file.read()
            
        # Process books (using your existing book processing logic)
        books = extract_book_details(raw_html, subject_info, url)
        
        all_books = all_books + books
        
    # book_list = process_subjects(subjects)
    # book_list = process_subjects()
    book_df = pd.DataFrame(all_books) 
    to_csv(book_df, "./shamela/shamela_book_subject.csv")
    


