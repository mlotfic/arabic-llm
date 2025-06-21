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

def extract_book_details(raw_html, subject_name, subject_id, url):
    soup = BeautifulSoup(raw_html, 'html.parser')
    book_list = []

    # Find the UL with book items
    ul = soup.find('ul', class_="oneitems w-border")
    if ul:
        # Find all list items
        li_elements = ul.find_all('li', class_="answer")
    
    
        for li_element in li_elements:
            # Extract book URL and full URL
            h2_link = li_element.find("h2").find("a")
            book_relative_url = h2_link.get("href", "")
            book_full_url = 'https://www.islamweb.net' + book_relative_url if book_relative_url else ""
            
            li_element_text = li_element.text.strip()
            
            # Extract book ID, idfrom, idto
            book_id, idfrom, idto = simple_extraction(book_full_url)
            
            # Extract book title
            label = h2_link.find("label")        
            
            # Extract publication date
            date_span = label.find("span", class_="date")
            if date_span:
                publication_date_text = date_span.text.strip()
                publication_date, date_parts = advanced_date_standardization(publication_date_text)
                date_span.decompose()
                
            else:
                publication_date = ""
                date_parts = {
                    'hijri_year': "",
                    'gregorian_year': "",
                    'hijri': "",
                    'gregorian': ""
                }
                
            book_title = label.text.strip()
            
            # Extract author information
            author_div = li_element.select_one('div:has(a.a-inverse)')
            
            author_label = author_div.find('a').find("label")
            if author_label:
                author_label_text = author_label.text.strip()
                author_parts = author_label.text.strip().split("-")
                author_short_name = author_parts[0].strip() if len(author_parts) > 0 else ""
                author_full_name = author_parts[1].strip() if len(author_parts) > 1 else ""
            else:
                author_short_name = author_full_name = ""
                author_label_text =""
            
            # Extract additional book details
            info_divs = li_element.find_all('div', class_='info-book')
            if info_divs and len(info_divs) > 0:
                samp_tags = info_divs[0].find_all('samp')
                
                # Extract topic
                topic_samp = samp_tags[0]
                topic_link = topic_samp.find('a')
                
                if topic_link:
                    topic = topic_link.text.strip()
                else:                
                    topic = ""
                
                
                # Extract publisher
                publisher_samp = samp_tags[1]
                publisher_label = publisher_samp.find('label').find('label')
                if publisher_label:
                    publisher = publisher_label.text.strip()
                else:                
                    publisher = ""       
            
            # Compile book details
            book_details = {
                "book_id"               : book_id,
                "idfrom"                : idfrom,
                "idto"                  : idto,
                "book_title"            : book_title,
                "li_element_text"       : li_element_text,
                "publication_date"      : publication_date,
                "publication_gregorian" : date_parts['gregorian_year'],
                "publication_hijri"     : date_parts['hijri_year'],
                "author_label_text"     : author_label_text,
                "publication_date_text" : publication_date_text,
                "author_short_name"     : author_short_name,
                "author_full_name"      : author_full_name,
                "book_url"              : book_full_url,
                "topic"                 : topic,
                "publisher"             : publisher,
                "subject_name"          : subject_name,
                "subject_id"            : subject_id,
                "subject_url"           : url
            }
            
            book_list.append(book_details)           
        
    return book_list


# Create dictionary of subjects
subjects = {
    "متون الحديث": {"subject_id": "1", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=1"},
    "أحاديث الأحكام": {"subject_id": "4", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=4"},
    "فروع الفقه الحنفي": {"subject_id": "7", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=7"},
    "فروع الفقه المالكي": {"subject_id": "10", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=10"},
    "الفقه المقارن": {"subject_id": "13", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=13"},
    "فروع الفقه الحنبلي": {"subject_id": "16", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=16"},
    "فروع الفقه الظاهري": {"subject_id": "19", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=19"},
    "فروع الفقه الشافعي": {"subject_id": "22", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=22"},
    "الفتاوى": {"subject_id": "25", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=25"},
    "أصول الفقه": {"subject_id": "28", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=28"},
    "القضاء": {"subject_id": "31", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=31"},
    "القواعد الفقهية": {"subject_id": "34", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=34"},
    "السياسة الشرعية": {"subject_id": "37", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=37"},
    "الآداب الشرعية": {"subject_id": "40", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=40"},
    "لغة الفقه": {"subject_id": "43", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=43"},
    "آيات الأحكام": {"subject_id": "46", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=46"},
    "تفسير القرآن": {"subject_id": "49", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=49"},
    "شروح الحديث": {"subject_id": "52", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=52"},
    "السيرة النبوية": {"subject_id": "55", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=55"},
    "التاريخ والتراجم": {"subject_id": "58", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=58"},
    "علوم القرآن": {"subject_id": "61", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=61"},
    "علوم الحديث": {"subject_id": "64", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=64"},
    "العقيدة": {"subject_id": "67", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=67"},
    "الآداب والرقائق": {"subject_id": "70", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=70"},
    "كتب اللغة العربية": {"subject_id": "73", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=73"},
    "كتاب الأمة": {"subject_id": "76", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=76"},
    "فقه عام": {"subject_id": "79", "url": "https://www.islamweb.net/ar/library/index.php?page=bookslist&subject=79"}
}


# Function to fetch and process URLs
def process_subjects(subjects):   
    
    all_books = []
    
    # ✅ Initialize browser
    driver = create_human_like_browser()
    
    for subject_name, subject_info in subjects.items():
        # Get URL
        url = subject_info['url']
        subject_id = subject_info['subject_id']
        
        print(f"Processing {subject_name} (ID: {subject_id})")
        
        # ✅ Open target website
        driver.get(url)
        
        # Get the raw HTML
        raw_html = driver.page_source
                    
        # Process books (using your existing book processing logic)
        books = extract_book_details(raw_html, subject_name, subject_id, url)
        
        all_books = all_books + books 
        
        # Polite delay between requests
        time.sleep(2)         

    # ✅ Close browser
    driver.quit()    
    
    return all_books        

# # ✅ Close browser
# driver.quit()
 
book_list = process_subjects(subjects)
# book_list = process_subjects()
book_df = pd.DataFrame(book_list) 
to_csv(book_df, "./islamwebbooks/book_subject.csv")

set(book_df["publication_date"])


