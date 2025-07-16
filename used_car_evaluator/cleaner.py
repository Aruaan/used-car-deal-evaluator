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
    Also normalizes engine, transmission, city, seller_type, fuel_type, seller_info, url.
    Returns a list of dicts with cleaned fields.
    """
    cleaned = []
    for item in raw_listings:
        title = item.get("title")
        year = parse_int(item.get("year"))
        mileage = parse_int(item.get("mileage"))
        price = parse_int(item.get("price"))
        engine = item.get("engine")
        if engine:
            engine = engine.strip().upper()
        transmission = item.get("transmission")
        if transmission:
            transmission = transmission.strip().capitalize()
        city = item.get("city")
        if city:
            city = city.strip().capitalize()
        seller_type = item.get("seller_type")
        if seller_type:
            seller_type = seller_type.strip().capitalize()
        fuel_type = item.get("fuel_type")
        if fuel_type:
            fuel_type = fuel_type.strip().capitalize()
        seller_info = item.get("seller_info")
        if seller_info:
            seller_info = seller_info.strip()
        url = item.get("url")
        # Try to extract year from title if missing
        if not year and title:
            year_match = re.search(r"(19|20)\d{2}", title)
            if year_match:
                year = int(year_match.group(0))
        cleaned.append({
            "title": title,
            "year": year,
            "mileage": mileage,
            "price": price,
            "engine": engine,
            "transmission": transmission,
            "city": city,
            "seller_type": seller_type,
            "fuel_type": fuel_type,
            "seller_info": seller_info,
            "url": url
        })
    return cleaned

