from typing import Optional, Dict, Any
from datetime import date, datetime
import re

def extract_info_from_input(user_input: str, state: Any = None) -> Dict[str, Any]:
    """
    Extract relevant appointment information from user input.
    Uses conversation context (last_question_field) for better extraction.
    
    Args:
        user_input: Natural language input from the user
        state: Optional current state to provide context
        
    Returns:
        Dictionary with extracted field names as keys and values
    """
    extracted = {}
    input_lower = user_input.lower().strip()
    
    # If we have context about what was just asked, prioritize that
    if state and state.last_question_field:
        context_field = state.last_question_field
        
        # Simple one-word or short answers - map directly to the expected field
        if len(user_input.split()) <= 5:  # Short answer, likely responding to last question
            if context_field == "full_name":
                # if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', user_input.strip()):
                name = user_input.strip()
                name = re.sub(r'(?i)\s+(my|name|is)$', '', name)
                extracted["full_name"] = name.title()
                return extracted
            
            elif context_field == "payer_name":
                # Clean and extract insurance name
                payer = user_input.strip()
                payer = re.sub(r'(?i)\s+(insurance|health|plan|coverage)$', '', payer)
                extracted["payer_name"] = payer.title()
                return extracted
            
            elif context_field == "insurance_id":
                # Extract any alphanumeric string
                match = re.search(r'[a-z0-9]+', input_lower)
                if match:
                    extracted["insurance_id"] = match.group(0).upper()
                    return extracted
            
            elif context_field == "chief_complaint":
                extracted["chief_complaint"] = user_input.strip()
                return extracted
            
            elif context_field == "street":
                extracted["street"] = user_input.strip().title()
                return extracted
            
            elif context_field == "city":
                extracted["city"] = user_input.strip().title()
                return extracted
            
            elif context_field == "state":
                state_input = user_input.strip().upper()
                # Handle full state names or abbreviations
                extracted["state"] = state_input[:2] if len(state_input) <= 2 else state_input
                return extracted
            
            elif context_field == "zip_code":
                match = re.search(r'\d{5}', user_input)
                if match:
                    extracted["zip_code"] = match.group(0)
                    return extracted
            
            elif context_field == "date_of_birth":
                from dateutil import parser
                try:
                    # try using dateutil parser first
                    parsed_date = parser.parse(user_input, fuzzy=True)
                    extracted["date_of_birth"] = parsed_date.date()
                    return extracted
                except (ValueError, parser.ParserError):
                    # Try to parse date
                    dob_patterns = [
                        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
                        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
                    ]
                    for pattern in dob_patterns:
                        match = re.search(pattern, user_input)
                        if match:
                            try:
                                if len(match.group(1)) == 4:
                                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                                else:
                                    month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                                extracted["date_of_birth"] = date(year, month, day)
                                return extracted
                            except (ValueError, TypeError):
                                pass
    
    # Fall back to regular pattern matching if context didn't help
    # Extract full name - ONLY if explicitly stated with keywords
    name_patterns = [
        r"(?:my name is|i'm|i am called|call me|name:?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            extracted["full_name"] = match.group(1).strip()
            break
    
    # Extract date of birth
    dob_patterns = [
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
    ]
    for pattern in dob_patterns:
        match = re.search(pattern, user_input)
        if match:
            try:
                if len(match.group(1)) == 4:
                    year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                else:
                    month, day, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                extracted["date_of_birth"] = date(year, month, day)
                break
            except (ValueError, TypeError):
                pass
    
    # Extract insurance payer name
    insurance_patterns = [
        r"(?:insurance|payer|carrier)\s+(?:is|name is)\s+([a-z][a-z\s&]+?)(?:\s+insurance|\s+health|$)",
        r"(?:have|insured by|covered by|with)\s+([a-z][a-z\s&]+?)\s+(?:insurance|health|coverage|plan)",
        r"my\s+insurance\s+is\s+([a-z][a-z\s&]+?)(?:\s+insurance|\s+health|$)",
    ]
    for pattern in insurance_patterns:
        match = re.search(pattern, input_lower)
        if match:
            payer = match.group(1).strip()
            payer = re.sub(r'\s+(plan|coverage|policy)$', '', payer)
            extracted["payer_name"] = payer.title()
            break
    
    # Extract insurance ID
    id_patterns = [
        r"(?:insurance\s+)?(?:id|number|policy\s+number|member\s+id)[\s:]+([a-z0-9]+)",
    ]
    for pattern in id_patterns:
        match = re.search(pattern, input_lower)
        if match:
            extracted["insurance_id"] = match.group(1).upper()
            break
    
    # Extract chief complaint
    complaint_patterns = [
        r"(?:here for|coming in for|reason|complaint|visit for|seeing doctor for|need to see doctor for)[\s:]+(.+)",
        r"(?:i have|experiencing|suffering from)[\s:]+(.+)",
    ]
    for pattern in complaint_patterns:
        match = re.search(pattern, input_lower)
        if match:
            complaint = match.group(1).strip()
            complaint = re.sub(r'[.!?]+$', '', complaint)
            extracted["chief_complaint"] = complaint
            break
    
    # Extract address components
    street_patterns = [
        r"(?:live at|address is|street is|address:)\s+(.+?)(?:,|\s+in\s+|$)",
        r"(\d+\s+[a-z0-9\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|boulevard|blvd|way|court|ct|circle|cir))",
    ]
    for pattern in street_patterns:
        match = re.search(pattern, input_lower)
        if match:
            extracted["street"] = match.group(1).strip().title()
            break
    
    city_patterns = [
        r"(?:city is|city:)\s+([a-z\s]+)",
        r"(?:in|from)\s+([a-z\s]+),\s+[a-z]{2}",
    ]
    for pattern in city_patterns:
        match = re.search(pattern, input_lower)
        if match:
            extracted["city"] = match.group(1).strip().title()
            break
    
    state_patterns = [
        r"(?:state is|state:)\s+([a-z]{2}|[a-z\s]+)",
        r",\s+([A-Z]{2})(?:\s+\d{5})?",
    ]
    for pattern in state_patterns:
        match = re.search(pattern, user_input)
        if match:
            extracted["state"] = match.group(1).strip().upper()
            break
    
    zip_patterns = [
        r"(?:zip|zipcode|zip code)[\s:]+(\d{5})",
        r"\b(\d{5})(?:-\d{4})?\b",
    ]
    for pattern in zip_patterns:
        match = re.search(pattern, user_input)
        if match:
            extracted["zip_code"] = match.group(1)
            break
    
    provider_patterns = [
        r"(?:doctor|dr\.?|provider)\s+([a-z\s]+)",
        r"(?:see|appointment with|schedule with)\s+(?:doctor|dr\.?)\s+([a-z\s]+)",
    ]
    for pattern in provider_patterns:
        match = re.search(pattern, input_lower)
        if match:
            extracted["selected_provider"] = match.group(1).strip().title()
            break
    
    time_patterns = [
        r"(\d{1,2}):(\d{2})\s*(am|pm)",
        r"(\d{1,2})\s*(am|pm)",
    ]
    for pattern in time_patterns:
        match = re.search(pattern, input_lower)
        if match:
            if len(match.groups()) == 3:
                time_str = f"{match.group(1)}:{match.group(2)} {match.group(3)}"
            else:
                time_str = f"{match.group(1)}:00 {match.group(2)}"
            extracted["selected_appointment_time"] = time_str
            break
    
    return extracted