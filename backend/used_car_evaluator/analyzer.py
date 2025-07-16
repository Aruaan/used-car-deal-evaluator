import re

def similarity_score(input_car, candidate):
    score = 0
    match_quality = {
        'engine_type': False,
        'transmission': False,
        'body_type': False,
        'engine_size': False,
        'power': False,
        'color': False,
        'doors': False,
        'seats': False,
        'year': False,
        'mileage': False
    }
    
    # Make/model (assume in title) - highest weight
    if input_car['title'] and candidate['title']:
        input_parts = input_car['title'].lower().split()
        cand_title = candidate['title'].lower()
        if input_parts[0] in cand_title:
            score += 5
        if len(input_parts) > 1 and input_parts[1] in cand_title:
            score += 5
    
    # Engine type - very important for comparison
    if input_car.get('engine_type') and candidate.get('engine_type'):
        if input_car['engine_type'] == candidate['engine_type']:
            score += 4
            match_quality['engine_type'] = True
        elif input_car['engine_type'] in ['petrol', 'diesel'] and candidate['engine_type'] in ['petrol', 'diesel']:
            # Similar fuel types get partial credit
            score += 2
    
    # Transmission - important for comparison
    if input_car.get('transmission') and candidate.get('transmission'):
        if input_car['transmission'] == candidate['transmission']:
            score += 3
            match_quality['transmission'] = True
        elif input_car['transmission'] in ['automatic', 'manual'] and candidate['transmission'] in ['automatic', 'manual']:
            # Different transmission types get negative points
            score -= 1
    
    # Body type - important for comparison
    if input_car.get('body_type') and candidate.get('body_type'):
        if input_car['body_type'] == candidate['body_type']:
            score += 3
            match_quality['body_type'] = True
        elif input_car['body_type'] in ['hatchback', 'sedan'] and candidate['body_type'] in ['hatchback', 'sedan']:
            # Similar body types get partial credit
            score += 1
    
    # Engine size - good for comparison
    if input_car.get('engine_size') and candidate.get('engine_size'):
        try:
            input_size = float(input_car['engine_size'])
            cand_size = float(candidate['engine_size'])
            size_diff = abs(input_size - cand_size)
            if size_diff == 0:
                score += 2
                match_quality['engine_size'] = True
            elif size_diff <= 0.2:
                score += 1
        except (ValueError, TypeError):
            pass
    
    # Power - good for comparison
    if input_car.get('power') and candidate.get('power'):
        try:
            # Extract numbers from power strings (e.g., "90 kW" -> 90)
            input_power = re.search(r'(\d+)', input_car['power'])
            cand_power = re.search(r'(\d+)', candidate['power'])
            if input_power and cand_power:
                input_power_val = int(input_power.group(1))
                cand_power_val = int(cand_power.group(1))
                power_diff = abs(input_power_val - cand_power_val)
                if power_diff == 0:
                    score += 2
                    match_quality['power'] = True
                elif power_diff <= 10:
                    score += 1
        except (ValueError, TypeError):
            pass
    
    # Color - minor factor but exact match is good
    if input_car.get('color') and candidate.get('color'):
        if input_car['color'].lower() == candidate['color'].lower():
            score += 1
            match_quality['color'] = True
    
    # Doors - exact match is good
    if input_car.get('doors') and candidate.get('doors'):
        if input_car['doors'] == candidate['doors']:
            score += 1
            match_quality['doors'] = True
    
    # Seats - exact match is good
    if input_car.get('seats') and candidate.get('seats'):
        if input_car['seats'] == candidate['seats']:
            score += 1
            match_quality['seats'] = True
    
    # Year - important but not as critical as technical specs
    if input_car['year'] and candidate['year']:
        diff = abs(input_car['year'] - candidate['year'])
        if diff == 0:
            score += 3
            match_quality['year'] = True
        elif diff == 1:
            score += 2
        elif diff == 2:
            score += 1
    
    # Mileage - important but not as critical as technical specs
    if input_car['mileage'] and candidate['mileage']:
        diff = abs(input_car['mileage'] - candidate['mileage'])
        if diff < 10000:
            score += 3
            match_quality['mileage'] = True
        elif diff < 20000:
            score += 2
        elif diff < 50000:
            score += 1
    
    # Fuel type (legacy field)
    if input_car.get('fuel_type') and candidate.get('fuel_type') and input_car['fuel_type'] == candidate['fuel_type']:
        score += 1
    
    # Engine (legacy field)
    if input_car.get('engine') and candidate.get('engine') and input_car['engine'] == candidate['engine']:
        score += 2
    
    # City - minor factor
    if input_car.get('city') and candidate.get('city') and input_car['city'] == candidate['city']:
        score += 1
    
    # Seller type - minor factor
    if input_car.get('seller_type') and candidate.get('seller_type') and input_car['seller_type'] == candidate['seller_type']:
        score += 1
    
    # Keywords - bonus for matching features
    if input_car.get('keywords') and candidate.get('keywords'):
        input_keywords = set(input_car['keywords'])
        cand_keywords = set(candidate['keywords'])
        common_keywords = input_keywords.intersection(cand_keywords)
        score += len(common_keywords) * 0.5
    
    return score, match_quality


def analyze_listing(input_car, listing_pool):
    # Score all candidates
    scored = []
    for car in listing_pool:
        score, match_quality = similarity_score(input_car, car)
        if score > 0 and car['price']:
            scored.append((score, car, match_quality))
    
    if not scored:
        return {
            "error": "No similar cars found (using similarity scoring).",
            "sample_listings": listing_pool[:5]
        }
    
    # Sort by score descending, then by price difference
    scored.sort(key=lambda x: (-x[0], abs((x[1]['price'] or 0) - (input_car['price'] or 0))))
    
    # Get top matches
    top = scored[:5]
    avg_price = sum(car['price'] for _, car, _ in top) / len(top)
    percent_diff = 100 * (avg_price - input_car['price']) / avg_price
    is_cheaper = input_car['price'] < avg_price
    
    # Calculate overall match quality
    total_matches = len(top)
    high_quality_matches = 0
    medium_quality_matches = 0
    
    for _, car, match_quality in top:
        # Count how many key attributes match
        key_matches = sum([
            match_quality['engine_type'],
            match_quality['transmission'],
            match_quality['body_type'],
            match_quality['power']
        ])
        
        if key_matches >= 3:
            high_quality_matches += 1
        elif key_matches >= 2:
            medium_quality_matches += 1
    
    # Determine comparison quality
    if high_quality_matches >= 2:
        comparison_quality = "high"
        quality_note = None
    elif medium_quality_matches >= 2:
        comparison_quality = "medium"
        quality_note = "Some technical specifications don't match exactly"
    else:
        comparison_quality = "low"
        quality_note = "Limited matches on technical specifications - comparing mainly by brand/model/year"
    
    return {
        "average_price": round(avg_price, 2),
        "count_similar": len(top),
        "percent_diff": round(abs(percent_diff), 1),
        "is_cheaper": is_cheaper,
        "comparison_quality": comparison_quality,
        "quality_note": quality_note,
        "high_quality_matches": high_quality_matches,
        "medium_quality_matches": medium_quality_matches,
        "top_similar": [
            {
                "title": car['title'],
                "year": car['year'],
                "mileage": car['mileage'],
                "price": car['price'],
                "engine": car.get('engine'),
                "engine_type": car.get('engine_type'),
                "engine_size": car.get('engine_size'),
                "transmission": car.get('transmission'),
                "body_type": car.get('body_type'),
                "power": car.get('power'),
                "color": car.get('color'),
                "doors": car.get('doors'),
                "seats": car.get('seats'),
                "fuel_type": car.get('fuel_type'),
                "city": car.get('city'),
                "seller_type": car.get('seller_type'),
                "seller_info": car.get('seller_info'),
                "keywords": car.get('keywords', []),
                "url": car.get('url'),
                "score": score,
                "match_quality": match_quality
            } for score, car, match_quality in top
        ]
    }

