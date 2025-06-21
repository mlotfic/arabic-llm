# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 17:50:11 2025

@author: m
"""

def remove_date_duplicates(dict_list):
    """
    Remove duplicate dictionaries where date ranges are within ±1 day of each other.
    Keeps the first occurrence and removes subsequent duplicates.
    """
    if not dict_list:
        return []
    
    result = []
    
    for current_dict in dict_list:
        is_duplicate = False
        
        for existing_dict in result:
            # Check if all date fields are within ±1 day of each other
            hijri_end_match = abs(int(current_dict["hijri_range_end"]) - int(existing_dict["hijri_range_end"])) <= 1
            hijri_start_match = abs(int(current_dict["hijri_range_start"]) - int(existing_dict["hijri_range_start"])) <= 1
            gregorian_start_match = abs(int(current_dict["gregorian_start"]) - int(existing_dict["gregorian_start"])) <= 1
            gregorian_end_match = abs(int(current_dict["gregorian_end"]) - int(existing_dict["gregorian_end"])) <= 1
            
            # If all conditions are met, it's a duplicate
            if hijri_end_match and hijri_start_match and gregorian_start_match and gregorian_end_match:
                is_duplicate = True
                break
        
        # Only add if it's not a duplicate
        if not is_duplicate:
            result.append(current_dict)
    
    return result


# Example usage:
if __name__ == "__main__":
    # Example with integer dates (e.g., days since epoch)
    sample_data = [
        {
            "hijri_range_end": 100,
            "hijri_range_start": 90,
            "gregorian_start": 200,
            "gregorian_end": 210,
            "other_data": "first"
        },
        {
            "hijri_range_end": 101,  # Within ±1
            "hijri_range_start": 91,  # Within ±1
            "gregorian_start": 201,   # Within ±1
            "gregorian_end": 209,     # Within ±1
            "other_data": "duplicate"
        },
        {
            "hijri_range_end": 150,
            "hijri_range_start": 140,
            "gregorian_start": 300,
            "gregorian_end": 310,
            "other_data": "different"
        }
    ]
    
    cleaned_data = remove_date_duplicates(sample_data)
    print(f"Original: {len(sample_data)} items")
    print(f"After deduplication: {len(cleaned_data)} items")
    
    for item in cleaned_data:
        print(item)