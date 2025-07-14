from playwright.sync_api import sync_playwright
import re
from urllib.parse import quote_plus

BASE_URL = "https://www.polovniautomobili.com/auto-oglasi/pretraga"

def build_url(make, model, price_to, page):
    params = [
        f"brand={quote_plus(make.lower())}",
        f"model[]={quote_plus(model.lower())}",
    ]
    if price_to:
        params.append(f"price_to={price_to}")
    params.append(f"page={page}")
    return f"{BASE_URL}?{'&'.join(params)}"


def scrape_listings(make, model, price_to=None, pages=5):
    all_listings = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for i in range(1, pages + 1):
            url = build_url(make, model, price_to, i)
            print(f"[DEBUG] Loading {url}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("a.ga-title", timeout=15000)

                ads = page.query_selector_all("article.classified")
                print(f"[DEBUG] Page {i}: found {len(ads)} listings")

                for ad in ads:
                    try:
                        title_el = ad.query_selector("a.ga-title")
                        title = title_el.inner_text().strip() if title_el else None
                        year = None
                        mileage = None
                        top_divs = ad.query_selector_all("div.top")
                        for txt in top_divs:
                            txt = txt.inner_text().strip()
                            if not year:
                                m = re.search(r"(19|20)\d{2}", txt)
                                if m:
                                    year = m.group(0)
                            if not mileage and "km" in txt:
                                mileage = txt
                        # Robust price extraction: look for span containing '€'
                        price = None
                        price_el = ad.query_selector("span")
                        if price_el and "€" in price_el.inner_text():
                            price = price_el.inner_text().strip()
                        else:
                            # Fallback: find any span with '€'
                            for span in ad.query_selector_all("span"):
                                txt = span.inner_text().strip()
                                if "€" in txt:
                                    price = txt
                                    break
                        all_listings.append({
                            "title": title,
                            "year": year,
                            "mileage": mileage,
                            "price": price
                        })
                    except Exception as e:
                        print(f"[DEBUG] Error parsing ad: {e}")
            except Exception as e:
                print(f"[DEBUG] Error loading page {i}: {e}")
        browser.close()
    return all_listings

