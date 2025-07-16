
from flask import Flask, request, jsonify
from flask_cors import CORS
from used_car_evaluator.scraper import scrape_listings
from used_car_evaluator.cleaner import clean_data
from used_car_evaluator.analyzer import analyze_listing

app = Flask(__name__)
CORS(app)

@app.route('/api/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    make = data.get('make')
    model = data.get('model')
    price_to = data.get('price_to')
    pages = data.get('pages', 3)
    if not (make and model):
        return jsonify({'error': 'Missing make or model'}), 400
    listings = scrape_listings(make, model, price_to=price_to, pages=pages)
    cleaned = clean_data(listings)
    return jsonify(cleaned)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400
    input_car = data.get('input_car')
    listings = data.get('listings')
    if not (input_car and listings):
        return jsonify({'error': 'Missing input_car or listings'}), 400
    result = analyze_listing(input_car, listings)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
