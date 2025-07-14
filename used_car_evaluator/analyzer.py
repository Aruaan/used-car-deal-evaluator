def analyze_listing(input_car, listing_pool):
    year = input_car.get("year")
    mileage = input_car.get("mileage")
    price = input_car.get("price")
    title = input_car.get("title")
    if not (year and mileage and price):
        return {"error": "Input car missing year, mileage, or price."}

    # Extract make and model from input title
    parts = title.lower().split()
    make = parts[0] if len(parts) > 0 else ""
    model = parts[1] if len(parts) > 1 else ""

    # Try to match make and model, but fallback to just make if needed
    similar = [
        car for car in listing_pool
        if car["title"] and make in car["title"].lower() and model in car["title"].lower()
        and car["year"] and abs(car["year"] - year) <= 2
        and car["mileage"] and abs(car["mileage"] - mileage) <= 50000
        and car["price"]
    ]
    if not similar:
        # Fallback: match only make
        similar = [
            car for car in listing_pool
            if car["title"] and make in car["title"].lower()
            and car["year"] and abs(car["year"] - year) <= 2
            and car["mileage"] and abs(car["mileage"] - mileage) <= 50000
            and car["price"]
        ]
    if not similar:
        # Fallback: show first 5 listings for user feedback
        return {
            "error": f"No similar cars found for {make} {model}.",
            "sample_listings": listing_pool[:5]
        }

    avg_price = sum(car["price"] for car in similar) / len(similar)
    percent_diff = 100 * (avg_price - price) / avg_price
    is_cheaper = price < avg_price
    return {
        "average_price": round(avg_price, 2),
        "count_similar": len(similar),
        "percent_diff": round(abs(percent_diff), 1),
        "is_cheaper": is_cheaper,
        "sample_titles": [car["title"] for car in similar[:5]]
    }

