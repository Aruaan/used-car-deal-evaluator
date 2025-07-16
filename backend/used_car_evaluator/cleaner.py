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
        
        # Clean engine info
        engine = item.get("engine")
        if engine:
            engine = engine.strip().upper()
        
        engine_type = item.get("engine_type")
        if engine_type:
            engine_type = engine_type.strip().lower()
        
        engine_size = item.get("engine_size")
        if engine_size:
            engine_size = engine_size.strip()
        
        # Clean transmission
        transmission = item.get("transmission")
        if transmission:
            transmission = transmission.strip().lower()
            if transmission in ['automatski', 'automatic', 'auto']:
                transmission = 'automatic'
            elif transmission in ['manuelni', 'manual', 'manuel']:
                transmission = 'manual'
        
        # Clean body type
        body_type = item.get("body_type")
        if body_type:
            body_type = body_type.strip().lower()
        
        # Clean other fields
        city = item.get("city")
        if city:
            city = city.strip().capitalize()
        
        seller_type = item.get("seller_type")
        if seller_type:
            seller_type = seller_type.strip().capitalize()
        
        fuel_type = item.get("fuel_type")
        if fuel_type:
            fuel_type = fuel_type.strip().lower()
        
        seller_info = item.get("seller_info")
        if seller_info:
            seller_info = seller_info.strip()
        
        url = item.get("url")
        
        # Clean new fields
        power = item.get("power")
        if power:
            power = power.strip()
        
        color = item.get("color")
        if color:
            color = color.strip().capitalize()
        
        doors = item.get("doors")
        if doors:
            doors = doors.strip()
        
        seats = item.get("seats")
        if seats:
            seats = seats.strip()
        
        # Clean keywords
        keywords = item.get("keywords", [])
        if keywords:
            keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
        
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
            "engine_type": engine_type,
            "engine_size": engine_size,
            "transmission": transmission,
            "body_type": body_type,
            "power": power,
            "color": color,
            "doors": doors,
            "seats": seats,
            "city": city,
            "seller_type": seller_type,
            "fuel_type": fuel_type,
            "seller_info": seller_info,
            "keywords": keywords,
            "url": url
        })
    return cleaned

