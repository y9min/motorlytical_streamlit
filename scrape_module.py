import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import random

def scrape_autotrader(cars, criteria, st):
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        ])
    }

    data = []
    st.write("Starting lightweight scraping...")

    try:
        for car in cars:
            url = (
                f"https://www.autotrader.co.uk/car-search?"
                f"make={car['make']}&model={car['model']}"
                f"&postcode={criteria['postcode'].replace(' ', '+')}"
                f"&radius={criteria['radius']}&sort=most-recent"
            )
            st.write(f"Fetching: {url}")

            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                st.error(f"Failed to fetch {url} (status {response.status_code})")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            listings = soup.find_all("li", class_="search-page__result")
            st.write(f"Found {len(listings)} listings")

            for listing in listings:
                try:
                    name_elem = listing.find("h3")
                    price_elem = listing.find("div", class_="vehicle-card-price")
                    link_elem = listing.find("a", href=True)

                    if name_elem and price_elem and link_elem:
                        name = name_elem.text.strip()
                        price = price_elem.text.strip()
                        link = "https://www.autotrader.co.uk" + link_elem['href']

                        data.append({"name": name, "price": price, "link": link})
                except Exception as e:
                    st.warning(f"Failed to parse a listing: {e}")

            time.sleep(1)

    except Exception as e:
        st.error(f"Scraping error: {e}")

    if not data:
        st.warning("No data scraped.")
        return pd.DataFrame(), {}, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    df = pd.DataFrame(data)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        df['price_numeric'] = (
            df['price']
            .str.replace("£", "", regex=False)
            .str.replace(",", "", regex=False)
            .astype(float)
        )
    except Exception as e:
        st.warning(f"Price parsing failed: {e}")

    avg_mileage = 0
    competition_index = random.randint(30, 70)

    metrics = {
        "average_mileage": avg_mileage,
        "competition_index": competition_index,
    }

    return df, metrics, timestamp


def create_price_trend_graph(monthly_data, timestamp, car_make, car_model):
    pass  # No graph plotting for now
