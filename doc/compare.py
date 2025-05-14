from typing import Dict
import re

def compare_data(user_input: Dict, extracted_data: Dict) -> Dict[str, str]:
    """Compare user input with extracted data"""
    comparison = {}
    
    for field in ['Name', 'DOB', 'Aadhar', 'Mobile']:
        user_value = str(user_input.get(field, '')).strip()
        extracted_value = str(extracted_data.get(field, '')).strip()
        
        # Handle None values
        if not user_value or not extracted_value or extracted_value == 'None':
            comparison[field] = 'Missing'
            continue
        
        # Special handling for mobile numbers
        if field == 'Mobile':
            # Normalize mobile numbers for comparison
            user_mobile = _normalize_mobile(user_value)
            extracted_mobile = _normalize_mobile(extracted_value)
            
            if user_mobile == extracted_mobile:
                comparison[field] = '✅ Match'
            else:
                comparison[field] = '❌ Mismatch'
        # Special handling for Names
        elif field == 'Name':
            user_name = user_value.lower().strip()
            extracted_name = extracted_value.lower().strip()
            
            if user_name == extracted_name:
                comparison[field] = '✅ Match'
            else:
                # Check for partial match
                user_words = set(word for word in user_name.split() if len(word) > 2)
                extracted_words = set(word for word in extracted_name.split() if len(word) > 2)
                
                # Check if at least half of the words match
                if user_words and extracted_words:
                    common_words = user_words.intersection(extracted_words)
                    match_ratio = len(common_words) / max(len(user_words), len(extracted_words))
                    
                    if match_ratio >= 0.5:
                        comparison[field] = '⚠ Partial Match'
                    else:
                        comparison[field] = '❌ Mismatch'
                else:
                    comparison[field] = '❌ Mismatch'
        # Special handling for Aadhaar
        elif field == 'Aadhar':
            # Normalize Aadhaar numbers (remove spaces and dashes)
            user_aadhar = re.sub(r'[\s-]', '', user_value)
            extracted_aadhar = re.sub(r'[\s-]', '', extracted_value)
            
            if user_aadhar == extracted_aadhar:
                comparison[field] = '✅ Match'
            else:
                comparison[field] = '❌ Mismatch'
        # Handle other fields (DOB, etc.)
        else:
            if user_value.lower() == extracted_value.lower():
                comparison[field] = '✅ Match'
            else:
                comparison[field] = '❌ Mismatch'
    
    return comparison

def _normalize_mobile(mobile: str) -> str:
    """Normalize mobile number for comparison"""
    if not mobile:
        return ""
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', mobile)
    
    # Handle Indian mobile numbers
    if len(digits) == 10:
        # 10 digit number
        return digits
    elif len(digits) == 12 and digits.startswith('91'):
        # Remove country code (91)
        return digits[2:]
    elif len(digits) == 11 and digits.startswith('0'):
        # Remove leading 0
        return digits[1:]
    
    return digits