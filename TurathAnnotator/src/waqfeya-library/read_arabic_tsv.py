# -*- coding: utf-8 -*-
"""
Created on Sun May  4 22:14:01 2025

@author: m
"""

import pandas as pd
import numpy as np
import os
import re
import chardet
import ast

def to_csv(df, csv_path):
    """Save DF to file with proper encoding for Arabic text"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)    
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

# Arabic numeral conversion (optional)
arabic_digit_map = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
                    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}

def parse_path(path):
    """
    Extracts metadata from a structured file path.

    Args:
        path (str): The file path to parse.

    Returns:
        dict: A dictionary with extracted metadata, or None if parsing fails.
    """
    try:
        path = str(path)
        if path == '[]' or  path == []:
            
            print(f"Error parsing Empty path: {path}")
            return {
                "path_title": np.nan,
                "path_author": np.nan,
                "path_id_book": np.nan,
                "path_cat_path": np.nan,
                "path_cat_id": np.nan,
                "path_cat_code": np.nan            
            }
        # Split the path into its components
        parts = path.strip().split('/')
        if len(parts) < 4:
            print(f"Path does not have enough components.: {path}")
            return {
                "path_title": np.nan,
                "path_author": np.nan,
                "path_id_book": np.nan,
                "path_cat_path": np.nan,
                "path_cat_id": np.nan,
                "path_cat_code": np.nan            
            }
            # raise ValueError("Path does not have enough components.")

        # Extract and parse the category information
        category_info = parts[2]
        # Split by '(' and then by ')', flattening the results
        category_parts = []
        for part in re.split(r'\(', category_info):
            category_parts += re.split(r'\)', part)
        # Clean up and remove empty strings
        category_parts = [s.strip() for s in category_parts if s.strip()]
        if len(category_parts) < 3:
            raise ValueError("Category information is incomplete.")

        cat_code, cat_id, cat_name = category_parts[0], category_parts[1], category_parts[2]

        # Extract book metadata from the filename
        filename = parts[3]
        match = re.match(r"(\d+)ـ (.+) ---(?: (.+))?\.PDF", filename)


        # match = re.match(r"(\d+)ـ (.+) --- (.+)\.PDF", filename)
        if not match:            
            raise ValueError("Filename does not match expected format.", path)

        id_book, title, author = match.groups()

        return {
            "path_title": title.strip(),
            "path_author": author.strip() if author else np.nan,
            "path_id_book": id_book.strip(),
            "path_cat_path": cat_name,
            "path_cat_id": cat_id,
            "path_cat_code": cat_code
        }

    except Exception as e:
        # Optionally, log the error or handle it as needed
        print(f"Error parsing path: {e}")
        return {
            "path_title": np.nan,
            "path_author": np.nan,
            "path_id_book": np.nan,
            "path_cat_path": np.nan,
            "path_cat_book_count": np.nan,
            "path_cat_code": np.nan
        }

path = './txt/1ـ 211.0 (267) علوم القرآن/00031ـ كتب غريب القرآن الكريم --- حسين بن محمد نصار.PDF/الكتاب.txt'
result = parse_path(path)
print(result)

path = "['./txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 01.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 02.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 03.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 04.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الواجهة.txt']"
result = parse_path(path)
print(result)

path = ['./txt/1ـ 211.0 (267) علوم القرآن/00031ـ كتب غريب القرآن الكريم --- حسين بن محمد نصار.PDF/الكتاب.txt']
result = parse_path(path)
print(result)


path = ['./txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 01.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 02.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 03.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الجزء 04.txt', './txt/2ـ 213.4 (232) الحديث الستة/02406ـ السنن وبحاشيته مصباح الزجاجة في زوائد ابن ماجه (سنن ابن ماجه) (سنن ابن ماجة) (ت_ الألباني والحلبي) ---.PDF/الواجهة.txt']
result = parse_path(path)
print(result)

path = ['./txt/2ـ 213.7 (577) باقي مجموعات الحديث/00100ـ جزء فيه من حديث أبي الحسين عبد الوهاب بن الحسن الكلابي المعروف بأخي تبوك عن شيوخه ---.PDF/الكتاب.txt']
result = parse_path(path)
print(result)

path = "./txt/2ـ 213.7 (577) باقي مجموعات الحديث/00100ـ جزء فيه من حديث أبي الحسين عبد الوهاب بن الحسن الكلابي المعروف بأخي تبوك عن شيوخه ---.PDF/الكتاب.txt"
result = parse_path(path)
print(result)

# import pandas as pd

# df = pd.DataFrame({
#     'A': [[1, 2, 3], ['a', 'b']],
#     'B': [1, 2]
# })

# exploded_df = df.explode('A')
# print(exploded_df)



def extract_title_and_splits(text):
    text_splited = []
    for part in re.split(r'\(', text):
        text_splited += re.split(r'\)', part)
    text_splited = [s.strip() for s in text_splited if s.strip()]
    result = {'main_title': text_splited[0]}
    for i, s in enumerate(text_splited[1:], 1):
        result[f'split{i}'] = s
    return result

# https://huggingface.co/datasets/ieasybooks-org/prophet-mosque-library
# https://waqfeya.net/
# https://huggingface.co/datasets/ieasybooks-org/shamela-waqfeya-library
# https://shamela.ws/
# https://huggingface.co/datasets/ieasybooks-org/waqfeya-library

# Example usage
if __name__ == "__main__":
    # File path to your Arabic TSV
    file_path = "index.tsv"  # Replace with your actual file path
    # Read TSV file
    df = pd.read_csv(file_path, sep='\t')
    
    df.columns
    df = df[['category', 'author', 'title', 'pages', 'volumes', 'txt_paths']]
    
    df['txt_paths'] = df['txt_paths'].apply(ast.literal_eval)
    df = df.explode('txt_paths').reset_index(drop=True)
    
    df['txt_paths'] = df['txt_paths'].astype(str)

    # df = pd.DataFrame({
    #     'col': ['[1, 2, 3]', '[4, 5]']
    # })
    
    # df['col'] = df['col'].apply(ast.literal_eval)
    # df = df.explode('col').reset_index(drop=True)
    # print(df)
    
    # Apply the function
    parsed_data = df['txt_paths'].apply(parse_path)
    # # Apply the function
    # parsed_data = df['docx_paths'].apply(parse_path)
    # # Apply the function
    # parsed_data = df['pdf_paths'].apply(parse_path)
    
    # Convert the list of dicts into a DataFrame
    parsed_df = pd.DataFrame(parsed_data.tolist())
    
    # Concatenate with original df (optional)
    df = pd.concat([df, parsed_df], axis=1)
    
    df.columns
    
    ['category', 'author', 'title', 'pages', 'volumes', 'txt_paths',
           'path_title', 'path_author', 'path_id_book', 'path_cat_path',
           'path_cat_book_count', 'path_cat_code', 'path_cat_id']

    # Check if values are equal
    df['is_equal_category'] = df['category'] == df['path_cat_path']
    sum(df['is_equal_category'])  - df.shape[0]
    df['is_equal_author'] = df['author'] == df['path_author']
    sum(df['is_equal_author'])  - df.shape[0]
    
    df['is_equal_title'] = df['title'] == df['path_title']
    sum(df['is_equal_title'])  - df.shape[0]
    
    df_is_equal_author = df[df['is_equal_author'] == False]
    
    
    # Apply the function and expand the result into new columns
    df = df.join(df['title'].apply(lambda x: pd.Series(extract_title_and_splits(x))))
    
    
    # Split column by "-" into exactly 2 columns
    df[['book_title', 'titles']] = df['main_title'].str.split('-', n=1, expand=True)

    # Save to CSV        
    csv_path = "./index.csv"
    to_csv(df, csv_path)
    df.columns  
    
    # Filter items that contain at least one digit
    filtered_list = [item for item in category_title if re.search(r"\d+", str(item))]
    
    # Sample list with mixed data types
    data_list = ["abc", "123", 456, "78xyz", 89, "hello", 90.5, None, "", "42"]

    # Filter items that contain at least one digit
    filtered_list = [item for item in data_list if re.search(r"\d+", str(item))]

    print(filtered_list)  # Output: [123, 456, 89, 90.5, '42']
    
    
    
    
    
    xcategory_split3 = list(df['split3'].unique())
    xcategory_split2 = list(df['split2'].unique())
    xcategory_split1 = list(df['split1'].unique())
    xcategory_title = list(df['titlex'].unique())
    

    
    
    # Split column by "-" - expand=True creates separate columns
    #df_split = df['title'].str.split('-', n=2, expand=True)

الرحلة التتويجية إلى عاصمة البلاد الإنجليزية 1902
ت_ الأرناؤوط، ط 1405
قاموس المورد - عربي -انجليزي (ط. 1995)
المجموعة 01_ 1419 ھ = 001-007
648 - 923ھ-1250 - 1517م
الكتب والمكتبات في جنوب المملكة العربية السعودية 1215 - 1373 حركتها ووقفها عامرها وموفيها
جهود علماء الدعوة السلفية في نجد في الرد على المخالفين من 1200 1350ھ
['./txt/1ـ 211.0 (267) علوم القرآن/00031ـ كتب غريب القرآن الكريم --- حسين بن محمد نصار.PDF/الكتاب.txt']

رحلة الحاج المعاصر إلى مكة عام 1908 م    
تاريخ الفاطميين في شمالي إفريقية ومصر وبلاد الشام 297-567ھ    
    category_books = list(df['category'].unique())
    category_author = list(df['author'].unique())
    category_title = list(df['title'].unique())
مرافق الحج وخدماتها المدنية في عهد الملك عبد العزيز 1343 - 1373 ھ = 1924 - 1953 م    
ذيل الأعلام (ج 1)    
    بعثة إلى نجد 1336 1337 ھ __ 1917 - 1918 م
قضاة المدينة المنورة من عام 963 ھ إلى عام 1418 ھ    
    تكملة معجم المؤلفين (وفيات 1397 - 1415ھ = 1977 - 1995م)