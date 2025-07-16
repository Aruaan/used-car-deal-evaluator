def similarity_score(input_car, candidate):
    score = 0
    # Make/model (assume in title)
    if input_car['title'] and candidate['title']:
        input_parts = input_car['title'].lower().split()
        cand_title = candidate['title'].lower()
        if input_parts[0] in cand_title:
            score += 3
        if len(input_parts) > 1 and input_parts[1] in cand_title:
            score += 3
    # Year
    if input_car['year'] and candidate['year']:
        diff = abs(input_car['year'] - candidate['year'])
        if diff == 0:
            score += 2
        elif diff == 1:
            score += 1
    # Mileage
    if input_car['mileage'] and candidate['mileage']:
        diff = abs(input_car['mileage'] - candidate['mileage'])
        if diff < 20000:
            score += 2
        elif diff < 50000:
            score += 1
    # Engine
    if input_car.get('engine') and candidate.get('engine') and input_car['engine'] == candidate['engine']:
        score += 2
    # Transmission
    if input_car.get('transmission') and candidate.get('transmission') and input_car['transmission'] == candidate['transmission']:
        score += 1
    # Fuel type
    if input_car.get('fuel_type') and candidate.get('fuel_type') and input_car['fuel_type'] == candidate['fuel_type']:
        score += 1
    # City
    if input_car.get('city') and candidate.get('city') and input_car['city'] == candidate['city']:
        score += 1
    # Seller type
    if input_car.get('seller_type') and candidate.get('seller_type') and input_car['seller_type'] == candidate['seller_type']:
        score += 1
    # Seller info
    if input_car.get('seller_info') and candidate.get('seller_info') and input_car['seller_info'] == candidate['seller_info']:
        score += 1
    return score

def analyze_listing(input_car, listing_pool):
    # Score all candidates
    scored = []
    for car in listing_pool:
        score = similarity_score(input_car, car)
        if score > 0 and car['price']:
            scored.append((score, car))
    if not scored:
        return {
            "error": "No similar cars found (using similarity scoring).",
            "sample_listings": listing_pool[:5]
        }
    # Sort by score descending, then by price difference
    scored.sort(key=lambda x: (-x[0], abs((x[1]['price'] or 0) - (input_car['price'] or 0))))
    top = scored[:5]
    avg_price = sum(car['price'] for _, car in top) / len(top)
    percent_diff = 100 * (avg_price - input_car['price']) / avg_price
    is_cheaper = input_car['price'] < avg_price
    return {
        "average_price": round(avg_price, 2),
        "count_similar": len(top),
        "percent_diff": round(abs(percent_diff), 1),
        "is_cheaper": is_cheaper,
        "top_similar": [
            {
                "title": car['title'],
                "year": car['year'],
                "mileage": car['mileage'],
                "price": car['price'],
                "engine": car.get('engine'),
                "transmission": car.get('transmission'),
                "fuel_type": car.get('fuel_type'),
                "city": car.get('city'),
                "seller_type": car.get('seller_type'),
                "seller_info": car.get('seller_info'),
                "url": car.get('url'),
                "score": score
            } for score, car in top
        ]
    }

