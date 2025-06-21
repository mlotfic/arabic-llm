#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arabic Text File Processing Script

This script opens an Arabic text file, splits it by "PAGE_SEPARATOR",
and extracts the line before each separator as the page number.

Features:
- Opens and processes Arabic text files with proper encoding
- Splits content by the "PAGE_SEPARATOR" delimiter
- Extracts page numbers from lines preceding the separators
- Handles Arabic text with proper encoding
"""

import re
import os
import sys

def process_arabic_file(file_path):
    """
    Open an Arabic text file, split by PAGE_SEPARATOR, and extract page numbers.
    
    Args:
        file_path (str): Path to the Arabic text file
        
    Returns:
        list: List of dictionaries containing page number and content
    """
    try:
        # Open file with UTF-8 encoding which handles Arabic text properly
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split the content by PAGE_SEPARATOR
        pages = content.split("PAGE_SEPARATOR")
        
        result = []
        page_number = None
        
        # Process each page section
        for i, page_content in enumerate(pages):
            if i == 0:  # First section (before first PAGE_SEPARATOR)
                # This might not have a page number line
                page_content = page_content.strip()
                if page_content:
                    result.append({
                        "page_number": "1",  # Default to page 1 for first content
                        "content": page_content
                    })
            else:
                # For subsequent sections, get the preceding page content
                previous_page_content = pages[i-1].strip()
                
                # Extract the last line from the previous section as page number
                lines = previous_page_content.split('\n')
                if lines:
                    last_line = lines[-1].strip()
                    
                    # Check if the last line contains a number
                    numbers = re.findall(r'\d+', last_line)
                    page_number = numbers[-1] if numbers else f"unknown_{i}"
                else:
                    page_number = f"unknown_{i}"
                
                # Add to results if there's content
                page_content = page_content.strip()
                if page_content:
                    result.append({
                        "page_number": page_number,
                        "content": page_content
                    })
        
        return result
    
    except UnicodeDecodeError:
        print("Error: File encoding issue. Try different encoding.")
        return []
    except Exception as e:
        print(f"Error processing file: {e}")
        return []

def main():
    """Main function to run when script is executed directly."""
    
    # Check if file path is provided as command line argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_arabic_file>")
        print("Example: python script.py arabic_text.txt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    # Process the file
    pages = process_arabic_file(file_path)
    
    # Display results
    print(f"Found {len(pages)} pages in the file.")
    
    for i, page in enumerate(pages):
        print("\n" + "=" * 50)
        print(f"Page {page['page_number']}:")
        print("-" * 50)
        # Print first 100 characters of content (or less if content is shorter)
        preview = page['content'][:100] + "..." if len(page['content']) > 100 else page['content']
        print(preview)
    
    print("\n" + "=" * 50)
    
    # Example of accessing specific pages by their number
    if pages:
        print("\nYou can access pages by their number using the returned data structure.")
        print("Example usage in code:")
        print("pages = process_arabic_file('your_file.txt')")
        print("for page in pages:")
        print("    if page['page_number'] == '5':")  # Example page number
        print("        # Process page 5 content")
        print("        print(page['content'])")

# Example of how to use this as a module
def extract_pages_from_file(file_path):
    """
    Extract pages from an Arabic file with PAGE_SEPARATOR delimiters.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        dict: Dictionary with page numbers as keys and content as values
    """
    pages_list = process_arabic_file(file_path)
    pages_dict = {page['page_number']: page['content'] for page in pages_list}
    return pages_dict

# Run main function if script is executed directly
if __name__ == "__main__":
    model = "gemma3"
    file_path = "./txt/1ـ 211.0 (267) علوم القرآن/00031ـ كتب غريب القرآن الكريم --- حسين بن محمد نصار.PDF/الكتاب.txt"
   
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    # Process the file
    pages = process_arabic_file(file_path)
    
    # Display results
    print(f"Found {len(pages)} pages in the file.")
    
    for i, page in enumerate(pages):
        print("\n" + "=" * 50)
        print(f"Page {page['page_number']}:")
        print("-" * 50)
        # Print first 100 characters of content (or less if content is shorter)
        preview = page['content'][:100] + "..." if len(page['content']) > 100 else page['content']
        print(preview)
    
    print("\n" + "=" * 50)
    
    # Example of accessing specific pages by their number
    if pages:
        print("\nYou can access pages by their number using the returned data structure.")
        print("Example usage in code:")
        print("pages = process_arabic_file('your_file.txt')")
        print("for page in pages:")
        print("    if page['page_number'] == '5':")  # Example page number
        print("        # Process page 5 content")
        print("        print(page['content'])")