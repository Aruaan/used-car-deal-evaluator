from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re
from urllib.parse import quote_plus

BASE_URL = "https://www.polovniautomobili.com/auto-oglasi/pretraga"
SITE_BASE = "https://www.polovniautomobili.com"

def build_url(make, model, price_to, page):
    params = [
        f"brand={quote_plus(make.lower())}",
        f"model[]={quote_plus(model.lower())}",
    ]
    if price_to:
        params.append(f"price_to={price_to}")
    params.append(f"page={page}")
    return f"{BASE_URL}?{'&'.join(params)}"


def get_total_pages(page):
    # Try to find the last page number from pagination controls
    try:
        pagination = page.query_selector_all("ul.pagination li a")
        page_numbers = []
        for a in pagination:
            txt = a.inner_text().strip()
            if txt.isdigit():
                page_numbers.append(int(txt))
        if page_numbers:
            return max(page_numbers)
    except Exception as e:
        print(f"[DEBUG] Could not determine total pages: {e}")
    return 1


def scrape_listings(make, model, price_to=None, pages=None):
    all_listings = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        detail_page = browser.new_page()
        # First, load the first page to determine total pages
        url = build_url(make, model, price_to, 1)
        print(f"[DEBUG] Loading {url}")
        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector("a.ga-title", timeout=15000)
        except PlaywrightTimeoutError:
            print(f"[WARN] Timeout loading first page: {url}")
            browser.close()
            return []
        except Exception as e:
            print(f"[WARN] Error loading first page: {e}")
            browser.close()
            return []
        total_pages = get_total_pages(page) if pages is None else pages
        print(f"[DEBUG] Detected {total_pages} pages of results.")
        for i in range(1, total_pages + 1):
            url = build_url(make, model, price_to, i)
            print(f"[DEBUG] Loading {url}")
            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("a.ga-title", timeout=15000)
            except PlaywrightTimeoutError:
                print(f"[WARN] Timeout loading page {i}: {url}")
                continue
            except Exception as e:
                print(f"[WARN] Error loading page {i}: {e}")
                continue
            ads = page.query_selector_all("article.classified")
            print(f"[DEBUG] Page {i}: found {len(ads)} listings")
            for ad in ads:
                try:
                    title_el = ad.query_selector("a.ga-title")
                    title = title_el.inner_text().strip() if title_el else None
                    href = title_el.get_attribute("href") if title_el else None
                    detail_url = SITE_BASE + href if href and href.startswith("/") else href
                    subtitle_el = ad.query_selector("div.subtitle")
                    subtitle = subtitle_el.inner_text().strip() if subtitle_el else ""
                    engine = None
                    transmission = None
                    if subtitle:
                        m = re.search(r"\d\.\d+\s?[A-Za-z]+", subtitle)
                        if m:
                            engine = m.group(0)
                        if "automatski" in subtitle.lower():
                            transmission = "Automatski"
                        elif "manuelni" in subtitle.lower():
                            transmission = "Manuelni"
                    city_el = ad.query_selector("div.city")
                    city = city_el.inner_text().strip() if city_el else None
                    seller_type = None
                    adv_text = ad.query_selector("div.advertiserText")
                    if adv_text and "OGLASIVAČ" in adv_text.inner_text():
                        seller_type = "Dealer"
                    badge_el = ad.query_selector("div.badge span")
                    if badge_el and "Domaće tablice" in badge_el.inner_text():
                        seller_type = "Private"
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
                    price = None
                    price_el = ad.query_selector("span")
                    if price_el and "€" in price_el.inner_text():
                        price = price_el.inner_text().strip()
                    else:
                        for span in ad.query_selector_all("span"):
                            txt = span.inner_text().strip()
                            if "€" in txt:
                                price = txt
                                break
                    # --- Visit detail page for more info ---
                    fuel_type = None
                    engine_detail = None
                    transmission_detail = None
                    seller_info = None
                    if detail_url:
                        try:
                            detail_page.goto(detail_url, timeout=60000)
                            detail_page.wait_for_selector("body", timeout=15000)
                            # Try to extract fuel type, engine, transmission, seller info
                            fuel_el = detail_page.query_selector("//dt[contains(text(),'Gorivo')]/following-sibling::dd[1]")
                            if fuel_el:
                                fuel_type = fuel_el.inner_text().strip()
                            engine_el = detail_page.query_selector("//dt[contains(text(),'Kubikaža')]/following-sibling::dd[1]")
                            if engine_el:
                                engine_detail = engine_el.inner_text().strip()
                            trans_el = detail_page.query_selector("//dt[contains(text(),'Menjač')]/following-sibling::dd[1]")
                            if trans_el:
                                transmission_detail = trans_el.inner_text().strip()
                            seller_el = detail_page.query_selector("//dt[contains(text(),'Ime prodavca')]/following-sibling::dd[1]")
                            if seller_el:
                                seller_info = seller_el.inner_text().strip()
                        except PlaywrightTimeoutError:
                            print(f"[WARN] Timeout loading detail page: {detail_url}")
                        except Exception as e:
                            print(f"[DEBUG] Error loading detail page {detail_url}: {e}")
                    all_listings.append({
                        "title": title,
                        "year": year,
                        "mileage": mileage,
                        "price": price,
                        "engine": engine_detail or engine,
                        "transmission": transmission_detail or transmission,
                        "city": city,
                        "seller_type": seller_type,
                        "fuel_type": fuel_type,
                        "seller_info": seller_info,
                        "url": detail_url
                    })
                except Exception as e:
                    print(f"[DEBUG] Error parsing ad: {e}")
        browser.close()
    return all_listings

