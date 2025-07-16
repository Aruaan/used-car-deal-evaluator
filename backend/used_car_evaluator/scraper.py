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


def extract_engine_info(text):
    """Extract engine type and size from text, including BMW-style codes like 320d/320i."""
    if not text:
        return None, None
    
    text = text.lower()
    
    # Special case for Tesla
    if 'tesla' in text:
        engine_type = 'electric'
    else:
        engine_type = None
        # Engine types with their common designations
        engine_types = {
            'diesel': ['diesel', 'dizel', 'tdi', 'td', 'cdi', 'hdi', 'jtd', 'd4d', 'd5'],
            'petrol': ['benzin', 'petrol', 'gasoline', 'tsi', 'ts', 'gti', 'gtd', 'fsi', 'tfsi'],
            'lpg': ['lpg', 'gas', 'plin', 'cng'],
            'hybrid': ['hybrid', 'hibrid', 'hev'],
            'electric': ['electric', 'elektricni', 'ev', 'bev', 'phev']
        }
        for fuel_type, keywords in engine_types.items():
            if any(keyword in text for keyword in keywords):
                engine_type = fuel_type
                break
    engine_size = None
    # BMW-style code: e.g. 320d, 318i, 520d, 118d, 116i, etc.
    bmw_code_match = re.search(r'\b([1-9]\d{2})([di])\b', text)
    if bmw_code_match:
        code_num = bmw_code_match.group(1)
        code_type = bmw_code_match.group(2)
        # BMW codes: 320d means 2.0L diesel, 320i means 2.0L petrol
        try:
            size = float(code_num[1:]) / 10.0  # e.g. 320 -> 2.0
            if 0.5 <= size <= 8.0:
                engine_size = str(size)
        except Exception:
            pass
        if not engine_type:
            if code_type == 'd':
                engine_type = 'diesel'
            elif code_type == 'i':
                engine_type = 'petrol'
    # Engine size (look for patterns like 1.6, 2.0, etc.)
    if not engine_size:
        engine_size_match = re.search(r'(\d+\.?\d*)\s*(?:l|lit|liter|cc|cm³)', text, re.IGNORECASE)
        if engine_size_match:
            engine_size = engine_size_match.group(1)
        else:
            # Look for just numbers that could be engine size (before engine designations)
            size_match = re.search(r'(\d+\.?\d*)\s*(?:tdi|tsi|td|ts|gti|gtd|fsi|tfsi|cdi|hdi)', text, re.IGNORECASE)
            if size_match:
                engine_size = size_match.group(1)
            else:
                # Look for standalone numbers that could be engine size
                standalone_match = re.search(r'\b(\d+\.?\d*)\b', text)
                if standalone_match:
                    try:
                        size = float(standalone_match.group(1))
                        if 0.5 <= size <= 8.0:  # Reasonable engine size range
                            engine_size = standalone_match.group(1)
                    except ValueError:
                        pass
    return engine_type, engine_size


def extract_transmission(text):
    """Extract transmission type from text"""
    if not text:
        return None
    
    text = text.lower()
    
    if any(word in text for word in ['automatski', 'automatic', 'auto']):
        return 'automatic'
    elif any(word in text for word in ['manuelni', 'manual', 'manuel']):
        return 'manual'
    else:
        return None


def extract_body_type(text):
    """Extract body type from text"""
    if not text:
        return None
    
    text = text.lower()
    
    body_types = {
        'hatchback': ['hatchback', 'hecbek'],
        'sedan': ['sedan', 'limuzina'],
        'suv': ['suv', 'terenski', 'terrain'],
        'wagon': ['wagon', 'karavan', 'kombi'],
        'coupe': ['coupe', 'kupe'],
        'convertible': ['convertible', 'kabriolet', 'cabrio'],
        'van': ['van', 'kombi', 'minibus'],
        'pickup': ['pickup', 'pick-up']
    }
    
    for body_type, keywords in body_types.items():
        if any(keyword in text for keyword in keywords):
            return body_type
    
    return None


def extract_keywords(text):
    """Extract important keywords from text"""
    if not text:
        return []
    
    text = text.lower()
    keywords = []
    
    # Important keywords to look for
    important_keywords = [
        'registrovan', 'registracija', 'registrovan do',
        'može zamena', 'zamena', 'trade in',
        'neispravan', 'oštećen', 'havarija',
        'klima', 'klima uređaj', 'air conditioning',
        'navigacija', 'gps', 'satelitska navigacija',
        'led svetla', 'xenon', 'bi-xenon',
        'koža', 'kožna sedišta', 'leather',
        'panorama', 'panoramski krov',
        'aluminijumske felne', 'alu felne',
        'servisna knjiga', 'servisna istorija',
        'prvi vlasnik', 'drugi vlasnik',
        'garancija', 'warranty',
        'test vožnja', 'test drive'
    ]
    
    for keyword in important_keywords:
        if keyword in text:
            keywords.append(keyword)
    
    return keywords


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
                    
                    # Extract basic info from subtitle
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
                    body_type = None
                    engine_type = None
                    engine_size = None
                    power = None
                    color = None
                    doors = None
                    seats = None
                    keywords = []
                    
                    if detail_url:
                        try:
                            detail_page.goto(detail_url, timeout=60000)
                            detail_page.wait_for_selector("body", timeout=15000)
                            
                            # Wait a bit for dynamic content to load
                            detail_page.wait_for_timeout(2000)
                            
                            # Extract from detail page using more reliable selectors
                            # Look for specification tables or lists
                            spec_selectors = [
                                "dl.specifications dt, dl.specifications dd",
                                "table.specifications td",
                                ".car-details dt, .car-details dd",
                                ".specs dt, .specs dd",
                                "ul.specifications li",
                                ".technical-data dt, .technical-data dd"
                            ]
                            
                            specs_found = False
                            for selector in spec_selectors:
                                try:
                                    spec_elements = detail_page.query_selector_all(selector)
                                    if spec_elements:
                                        specs_found = True
                                        # Parse specifications
                                        for i in range(0, len(spec_elements) - 1, 2):
                                            if i + 1 < len(spec_elements):
                                                label = spec_elements[i].inner_text().strip().lower()
                                                value = spec_elements[i + 1].inner_text().strip()
                                                
                                                if 'gorivo' in label or 'fuel' in label:
                                                    fuel_type = value
                                                elif 'kubikaža' in label or 'engine' in label or 'motor' in label:
                                                    engine_detail = value
                                                elif 'menjač' in label or 'transmission' in label or 'gearbox' in label:
                                                    transmission_detail = value
                                                elif 'karoserija' in label or 'body' in label or 'type' in label:
                                                    body_type = value
                                                elif 'snaga' in label or 'power' in label or 'kw' in label:
                                                    power = value
                                                elif 'boja' in label or 'color' in label:
                                                    color = value
                                                elif 'vrata' in label or 'doors' in label:
                                                    doors = value
                                                elif 'sedišta' in label or 'seats' in label:
                                                    seats = value
                                        break
                                except Exception:
                                    continue
                            
                            # If no structured specs found, try alternative methods
                            if not specs_found:
                                # Try XPath selectors as fallback
                                try:
                                    fuel_el = detail_page.query_selector("//dt[contains(text(),'Gorivo')]/following-sibling::dd[1]")
                                    if fuel_el:
                                        fuel_type = fuel_el.inner_text().strip()
                                except:
                                    pass
                                
                                try:
                                    engine_el = detail_page.query_selector("//dt[contains(text(),'Kubikaža')]/following-sibling::dd[1]")
                                    if engine_el:
                                        engine_detail = engine_el.inner_text().strip()
                                except:
                                    pass
                                
                                try:
                                    trans_el = detail_page.query_selector("//dt[contains(text(),'Menjač')]/following-sibling::dd[1]")
                                    if trans_el:
                                        transmission_detail = trans_el.inner_text().strip()
                                except:
                                    pass
                                
                                try:
                                    body_el = detail_page.query_selector("//dt[contains(text(),'Karoserija')]/following-sibling::dd[1]")
                                    if body_el:
                                        body_type = body_el.inner_text().strip()
                                except:
                                    pass
                            
                            # Extract seller info
                            seller_selectors = [
                                ".seller-info",
                                ".advertiser-info",
                                ".contact-info",
                                "//dt[contains(text(),'Ime prodavca')]/following-sibling::dd[1]"
                            ]
                            
                            for selector in seller_selectors:
                                try:
                                    seller_el = detail_page.query_selector(selector)
                                    if seller_el:
                                        seller_info = seller_el.inner_text().strip()
                                        break
                                except:
                                    continue
                            
                            # Get description text for keywords
                            desc_selectors = [
                                ".description",
                                ".ad-description",
                                ".car-description",
                                ".details-text"
                            ]
                            
                            for selector in desc_selectors:
                                try:
                                    desc_el = detail_page.query_selector(selector)
                                    if desc_el:
                                        description = desc_el.inner_text().strip()
                                        keywords = extract_keywords(description)
                                        break
                                except:
                                    continue
                            
                            # Also extract keywords from the entire page content
                            page_content = detail_page.content()
                            page_keywords = extract_keywords(page_content)
                            keywords.extend(page_keywords)
                            
                        except PlaywrightTimeoutError:
                            print(f"[WARN] Timeout loading detail page: {detail_url}")
                        except Exception as e:
                            print(f"[DEBUG] Error loading detail page {detail_url}: {e}")
                    
                    # Extract engine info from title and subtitle
                    title_subtitle_text = f"{title or ''} {subtitle or ''}"
                    extracted_engine_type, extracted_engine_size = extract_engine_info(title_subtitle_text)
                    
                    # Extract transmission from title and subtitle
                    extracted_transmission = extract_transmission(title_subtitle_text)
                    
                    # Extract body type from title
                    extracted_body_type = extract_body_type(title or "")
                    
                    # Extract keywords from title
                    title_keywords = extract_keywords(title or "")
                    keywords.extend(title_keywords)
                    
                    # Use detail page info if available, otherwise use extracted info
                    final_engine_type = fuel_type or extracted_engine_type
                    final_engine_size = engine_detail or extracted_engine_size
                    final_transmission = transmission_detail or transmission or extracted_transmission
                    final_body_type = body_type or extracted_body_type
                    
                    all_listings.append({
                        "title": title,
                        "year": year,
                        "mileage": mileage,
                        "price": price,
                        "engine": engine_detail or engine,
                        "engine_type": final_engine_type,
                        "engine_size": final_engine_size,
                        "transmission": final_transmission,
                        "body_type": final_body_type,
                        "power": power,
                        "color": color,
                        "doors": doors,
                        "seats": seats,
                        "city": city,
                        "seller_type": seller_type,
                        "fuel_type": fuel_type,
                        "seller_info": seller_info,
                        "keywords": list(set(keywords)),  # Remove duplicates
                        "url": detail_url
                    })
                except Exception as e:
                    print(f"[DEBUG] Error parsing ad: {e}")
        browser.close()
    return all_listings

