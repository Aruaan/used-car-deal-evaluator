import click

@click.command()
@click.option('--make', prompt='Car make')
@click.option('--model', prompt='Car model')
@click.option('--year', prompt='Year', type=int)
@click.option('--mileage', prompt='Mileage (km)', type=int)
@click.option('--price', prompt='Price (EUR)', type=int)
def evaluate(make, model, year, mileage, price):
    click.echo(f"Evaluating: {make} {model}, {year}, {mileage}km, {price}€")

if __name__ == "__main__":
    evaluate()
