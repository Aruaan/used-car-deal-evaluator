import re

def parse_int(value):
    if not value:
        return None
    value = value.replace(".", "").replace(",", "").replace("€", "").replace("km", "").strip()
    digits = re.findall(r"\d+", value)
    if digits:
        return int(digits[0])
    return None

def clean_data(raw_listings):
    """
    Cleans raw listings: parses price, mileage, year into integers.
    Returns a list of dicts with cleaned fields.
    """
    cleaned = []
    for item in raw_listings:
        title = item.get("title")
        year = parse_int(item.get("year"))
        mileage = parse_int(item.get("mileage"))
        price = parse_int(item.get("price"))
        # Try to extract year from title if missing
        if not year and title:
            year_match = re.search(r"(19|20)\d{2}", title)
            if year_match:
                year = int(year_match.group(0))
        cleaned.append({
            "title": title,
            "year": year,
            "mileage": mileage,
            "price": price
        })
    return cleaned

