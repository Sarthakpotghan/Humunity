import re
from typing import Dict, List, Optional

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except (ImportError, OSError):
    nlp = None


SEASON_KEYWORDS = {
    "spring": ["spring", "mar", "apr", "may"],
    "summer": ["summer", "jun", "jul", "aug"],
    "autumn": ["autumn", "fall", "sep", "oct", "nov"],
    "winter": ["winter", "dec", "jan", "feb"],
}

CONDITION_KEYWORDS = {
    "new": ["new", "brand new", "unused", "sealed"],
    "good": ["good", "excellent", "very good", "like new"],
    "fair": ["fair", "okay", "average", "used", "worn"],
}

ITEM_TYPE_PATTERNS = [
    r"\b(\d+)\s*(jackets?|sweaters?|shirts?|pants?|trousers?|skirts?|dresses?|tops?|hoodies?|coats?)\b",
    r"\b(\d+)\s*(notebooks?|pens?|pencils?|erasers?|rulers?|backpacks?|bags?|geometry\s*boxes?|calculators?)\b",
    r"\b(\d+)\s*(books?|textbooks?|workbooks?|storybooks?)\b",
]


def extract_quantity(text: str) -> Optional[int]:
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "CARDINAL":
                try:
                    return int(ent.text)
                except ValueError:
                    pass
    
    for pattern in ITEM_TYPE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                pass
    return None


def extract_item_type(text: str) -> Optional[str]:
    text_lower = text.lower()
    
    clothes_keywords = ["jacket", "sweater", "shirt", "pant", "trouser", "skirt", "dress", "top", "hoodie", "coat", "t-shirt", "tshirt", "jeans", "shorts"]
    stationery_keywords = ["notebook", "pen", "pencil", "eraser", "ruler", "backpack", "bag", "geometry box", "calculator", "book", "textbook", "workbook", "storybook"]
    
    for kw in clothes_keywords:
        if kw in text_lower:
            return kw
    for kw in stationery_keywords:
        if kw in text_lower:
            return kw
    return None


def extract_age_group(text: str) -> Optional[str]:
    patterns = [
        r"(?:age|aged|ages?)\s*(\d+)[-\s]*(?:to|-)?\s*(\d+)?",
        r"(\d+)[-\s]*(?:to|-)?\s*(\d+)?\s*(?:years?|yrs?|y\.o\.)",
        r"(kids?|children|toddlers?|infants?|teens?|adolescents?|youth)",
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            if match.group(1).isdigit():
                start = match.group(1)
                end = match.group(2) if match.group(2) else start
                return f"{start}-{end}"
            return match.group(1)
    return None


def extract_gender(text: str) -> Optional[str]:
    text_lower = text.lower()
    if any(w in text_lower for w in ["boy", "boys", "male", "men", "he", "him", "his"]):
        return "male"
    if any(w in text_lower for w in ["girl", "girls", "female", "women", "she", "her", "hers"]):
        return "female"
    if any(w in text_lower for w in ["unisex", "both", "any", "all gender"]):
        return "unisex"
    return None


def extract_season(text: str) -> Optional[str]:
    text_lower = text.lower()
    for season, keywords in SEASON_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return season
    return None


def extract_condition(text: str) -> Optional[str]:
    text_lower = text.lower()
    for condition, keywords in CONDITION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return condition
    return None


def extract_donation_fields(text: str) -> Dict:
    if not text:
        return {}
    
    return {
        "quantity": extract_quantity(text),
        "item_type": extract_item_type(text),
        "age_group": extract_age_group(text),
        "gender": extract_gender(text),
        "season": extract_season(text),
        "condition": extract_condition(text),
    }


def extract_request_fields(text: str) -> Dict:
    return extract_donation_fields(text)