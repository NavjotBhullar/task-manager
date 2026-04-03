import re

def clean_price(price_text):
    try:
        
        match = re.search(r"\d+\.\d+", price_text)
        if match:
            return float(match.group())
        return 0.0
    except:
        return 0.0


def get_rating(class_list):
    ratings = ["One", "Two", "Three", "Four", "Five"]
    for r in ratings:
        if r in class_list:
            return r
    return "Unknown"