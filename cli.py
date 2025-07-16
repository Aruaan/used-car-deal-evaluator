import click
from used_car_evaluator.scraper import scrape_listings
from used_car_evaluator.cleaner import clean_data
from used_car_evaluator.analyzer import analyze_listing
import pandas as pd

@click.command()
@click.option('--make', prompt='Car make')
@click.option('--model', prompt='Car model')
@click.option('--year', prompt='Year', type=int)
@click.option('--mileage', prompt='Mileage (km)', type=int)
@click.option('--price', prompt='Price (EUR)', type=int)
def evaluate(make, model, year, mileage, price):
    title = f"{make} {model}"
    click.echo(f"Evaluating: {title}, {year}, {mileage}km, {price}€")
    click.echo("Scraping listings from polovniautomobili.com...")
    try:
        # Only scrape relevant listings for this make/model/price
        raw_listings = scrape_listings(make, model, price_to=price, pages=None)
        cleaned_listings = clean_data(raw_listings)
        df = pd.DataFrame(cleaned_listings)
        df.to_csv("listings.csv", index=False)
        print("")
        input_car = {"title": title, "year": year, "mileage": mileage, "price": price}
        result = analyze_listing(input_car, cleaned_listings)
        if "error" in result:
            click.echo(f"[!] {result['error']}")
            if "sample_titles" in result:
                click.echo("Sample similar titles:")
                for t in result["sample_titles"]:
                    click.echo(f"  - {t}")
            elif "sample_listings" in result:
                click.echo("Sample listings:")
                for car in result["sample_listings"]:
                    if isinstance(car, dict):
                        click.echo(f"  - {car.get('title', '')} | {car.get('year', '')} | {car.get('mileage', '')}km | {car.get('price', '')}€")
                    else:
                        click.echo(f"  - {car}")
        else:
            avg = result['average_price']
            count = result['count_similar']
            pct = result['percent_diff']
            cheaper = result['is_cheaper']
            if cheaper:
                click.echo(f"Your car is {pct}% cheaper than the average of {count} most similar listings (avg: {avg}€). Good deal!")
            else:
                click.echo(f"Your car is {pct}% more expensive than the average of {count} most similar listings (avg: {avg}€). Not a great deal.")
            if "top_similar" in result:
                click.echo("Top 5 most similar listings:")
                for car in result["top_similar"]:
                    click.echo(f"  - {car['title']} | {car['year']} | {car['mileage']}km | {car['price']}€ | Engine: {car.get('engine','')} | Transmission: {car.get('transmission','')} | Fuel: {car.get('fuel_type','')} | City: {car.get('city','')} | Seller: {car.get('seller_type','')} | Seller info: {car.get('seller_info','')} | [View Ad]({car.get('url','')}) | Similarity score: {car['score']}")
    except Exception as e:
        click.echo(f"[!] Error: {e}")

if __name__ == "__main__":
    evaluate()
