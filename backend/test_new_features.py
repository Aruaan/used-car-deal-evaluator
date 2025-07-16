#!/usr/bin/env python3


from used_car_evaluator.scraper import extract_engine_info, extract_transmission, extract_body_type, extract_keywords
from used_car_evaluator.analyzer import similarity_score, analyze_listing

def test_metadata_extraction():
    """Test the new metadata extraction functions"""
    print("Testing metadata extraction...")
    
    
    test_cases = [
        ("Opel Corsa 1.6 TDI", ("diesel", "1.6")),
        ("VW Golf 2.0 TSI", ("petrol", "2.0")),
        ("Toyota Prius Hybrid", ("hybrid", None)),
        ("Tesla Model 3", ("electric", None)),
        ("BMW 320d", ("diesel", "2.0")),
        ("Audi A4 1.8 TFSI", ("petrol", "1.8")),
    ]
    
    for text, expected in test_cases:
        engine_type, engine_size = extract_engine_info(text)
        print(f"'{text}' -> engine_type: {engine_type}, engine_size: {engine_size}")
        assert engine_type == expected[0], f"Expected {expected[0]}, got {engine_type}"
        if expected[1]:
            assert engine_size == expected[1], f"Expected {expected[1]}, got {engine_size}"
    
    
    transmission_tests = [
        ("Opel Corsa Automatski", "automatic"),
        ("VW Golf Manuelni", "manual"),
        ("BMW 3 Series", None),
    ]
    
    for text, expected in transmission_tests:
        transmission = extract_transmission(text)
        print(f"'{text}' -> transmission: {transmission}")
        assert transmission == expected, f"Expected {expected}, got {transmission}"
    
    
    body_tests = [
        ("Opel Corsa Hatchback", "hatchback"),
        ("VW Passat Limuzina", "sedan"),
        ("BMW X5 SUV", "suv"),
        ("Audi A4", None),
    ]
    
    for text, expected in body_tests:
        body_type = extract_body_type(text)
        print(f"'{text}' -> body_type: {body_type}")
        assert body_type == expected, f"Expected {expected}, got {body_type}"
    
   
    keyword_tests = [
        ("Opel Corsa registrovan do 2025", ["registrovan"]),
        ("VW Golf klima navigacija", ["klima", "navigacija"]),
        ("BMW 3 Series", []),
    ]
    
    for text, expected in keyword_tests:
        keywords = extract_keywords(text)
        print(f"'{text}' -> keywords: {keywords}")
        for keyword in expected:
            assert keyword in keywords, f"Expected {keyword} in keywords"
    
    print("✅ All metadata extraction tests passed!")

def test_similarity_scoring():
    """Test the new similarity scoring with metadata"""
    print("\nTesting similarity scoring...")
    
    input_car = {
        'title': 'Opel Corsa',
        'year': 2010,
        'mileage': 150000,
        'price': 5000,
        'engine_type': 'diesel',
        'transmission': 'manual',
        'body_type': 'hatchback',
        'engine_size': '1.6',
        'power': '90 kW',
        'color': 'White',
        'doors': '5',
        'seats': '5'
    }
    
    # Test case 1: Perfect match
    perfect_match = {
        'title': 'Opel Corsa 1.6 TDI',
        'year': 2010,
        'mileage': 150000,
        'price': 5500,
        'engine_type': 'diesel',
        'transmission': 'manual',
        'body_type': 'hatchback',
        'engine_size': '1.6',
        'power': '90 kW',
        'color': 'White',
        'doors': '5',
        'seats': '5'
    }
    
    # Test case 2: Partial match
    partial_match = {
        'title': 'Opel Corsa 1.4',
        'year': 2010,
        'mileage': 160000,
        'price': 4800,
        'engine_type': 'petrol',
        'transmission': 'manual',
        'body_type': 'hatchback',
        'engine_size': '1.4',
        'power': '75 kW',
        'color': 'Blue',
        'doors': '5',
        'seats': '5'
    }
    
    # Test case 3: Poor match
    poor_match = {
        'title': 'VW Golf',
        'year': 2015,
        'mileage': 80000,
        'price': 12000,
        'engine_type': 'petrol',
        'transmission': 'automatic',
        'body_type': 'hatchback',
        'engine_size': '2.0',
        'power': '150 kW',
        'color': 'Red',
        'doors': '5',
        'seats': '5'
    }
    
    score1, quality1 = similarity_score(input_car, perfect_match)
    score2, quality2 = similarity_score(input_car, partial_match)
    score3, quality3 = similarity_score(input_car, poor_match)
    
    print(f"Perfect match score: {score1}, quality: {quality1}")
    print(f"Partial match score: {score2}, quality: {quality2}")
    print(f"Poor match score: {score3}, quality: {quality3}")
    
    # Verify that perfect match has higher score
    assert score1 > score2 > score3, "Scores should be in descending order"
    
    # Verify quality indicators
    assert quality1['engine_type'] == True, "Perfect match should have matching engine type"
    assert quality1['transmission'] == True, "Perfect match should have matching transmission"
    assert quality1['body_type'] == True, "Perfect match should have matching body type"
    assert quality1['power'] == True, "Perfect match should have matching power"
    assert quality1['color'] == True, "Perfect match should have matching color"
    assert quality1['doors'] == True, "Perfect match should have matching doors"
    assert quality1['seats'] == True, "Perfect match should have matching seats"
    
    print("✅ All similarity scoring tests passed!")

def test_analysis():
    """Test the complete analysis function"""
    print("\nTesting complete analysis...")
    
    input_car = {
        'title': 'Opel Corsa',
        'year': 2010,
        'mileage': 150000,
        'price': 5000,
        'engine_type': 'diesel',
        'transmission': 'manual',
        'body_type': 'hatchback',
        'engine_size': '1.6'
    }
    
    # Create test listings
    listings = [
        {
            'title': 'Opel Corsa 1.6 TDI',
            'year': 2010,
            'mileage': 150000,
            'price': 5500,
            'engine_type': 'diesel',
            'transmission': 'manual',
            'body_type': 'hatchback',
            'engine_size': '1.6',
            'power': '90 kW',
            'color': 'White',
            'doors': '5',
            'seats': '5',
            'keywords': ['registrovan', 'klima']
        },
        {
            'title': 'Opel Corsa 1.4',
            'year': 2010,
            'mileage': 160000,
            'price': 4800,
            'engine_type': 'petrol',
            'transmission': 'manual',
            'body_type': 'hatchback',
            'engine_size': '1.4',
            'power': '75 kW',
            'color': 'Blue',
            'doors': '5',
            'seats': '5',
            'keywords': ['registrovan']
        },
        {
            'title': 'VW Golf',
            'year': 2015,
            'mileage': 80000,
            'price': 12000,
            'engine_type': 'petrol',
            'transmission': 'automatic',
            'body_type': 'hatchback',
            'engine_size': '2.0',
            'power': '150 kW',
            'color': 'Red',
            'doors': '5',
            'seats': '5',
            'keywords': ['navigacija']
        }
    ]
    
    result = analyze_listing(input_car, listings)
    
    print(f"Analysis result: {result}")
    
    # Verify the result structure
    assert 'average_price' in result, "Result should contain average_price"
    assert 'comparison_quality' in result, "Result should contain comparison_quality"
    assert 'top_similar' in result, "Result should contain top_similar"
    assert len(result['top_similar']) > 0, "Should have at least one similar listing"
    
    # Verify that the first listing (perfect match) is ranked highest
    assert result['top_similar'][0]['title'] == 'Opel Corsa 1.6 TDI', "Perfect match should be ranked first"
    
    print("✅ All analysis tests passed!")

if __name__ == "__main__":
    test_metadata_extraction()
    test_similarity_scoring()
    test_analysis()
    print("\n🎉 All tests passed! The new features are working correctly.") 