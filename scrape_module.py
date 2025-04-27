import time
import datetime
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_stealth import stealth
import random
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Setup user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
]

def scrape_autotrader(cars, criteria, st):
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(options=chrome_options)
    stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32", webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)

    data = []
    st.write("Starting scraping...")

    try:
        for car in cars:
            url = f"https://www.autotrader.co.uk/car-search?make={car['make']}&model={car['model']}&postcode={criteria['postcode'].replace(' ', '+')}&radius={criteria['radius']}&sort=most-recent"
            driver.get(url)
            st.write(f"Searching: {car['make']} {car['model']} at {url}")
            time.sleep(5)

            page_text = driver.find_element(By.TAG_NAME, "body").text
            if any(phrase in page_text for phrase in ["No results found", "No cars found"]):
                st.warning("No cars found for this search.")
                continue

            listings = driver.find_elements(By.CSS_SELECTOR, "div.search-page__result")
            st.write(f"Found {len(listings)} listings.")

            for listing in listings:
                try:
                    name = listing.find_element(By.TAG_NAME, "h3").text
                    price = listing.find_element(By.CSS_SELECTOR, ".vehicle-card-price").text
                    link = listing.find_element(By.TAG_NAME, "a").get_attribute("href")
                    data.append({"name": name, "price": price, "link": link})
                except Exception as e:
                    st.error(f"Error reading a listing: {e}")

            time.sleep(2)
    except Exception as e:
        st.error(f"General scraping error: {e}")
    finally:
        driver.quit()

    if not data:
        st.warning("No data scraped.")
        return pd.DataFrame(), {}, datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    df = pd.DataFrame(data)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Some simple analysis
    try:
        df['price_numeric'] = df['price'].str.replace("£", "", regex=False).str.replace(",", "", regex=False).astype(float)
    except:
        st.warning("Price parsing failed.")

    avg_mileage = 0
    competition_index = random.randint(30, 70)  # Placeholder

    metrics = {
        "average_mileage": avg_mileage,
        "competition_index": competition_index,
    }

    return df, metrics, timestamp


def create_price_trend_graph(monthly_data, timestamp, car_make, car_model):
    if not monthly_data or len(monthly_data) < 2:
        return

    months = [item['month'] for item in monthly_data]
    avg_prices = [item['avg_price'] for item in monthly_data]

    plt.figure(figsize=(10, 6))
    plt.plot(months, avg_prices, 'o-', linewidth=2)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'£{x:,.0f}'))
    plt.xlabel('Month')
    plt.ylabel('Average Price')
    plt.title(f'{car_make} {car_model} Price Trend')
    plt.grid(True)
    plt.tight_layout()
    filename = f"average_price_trend_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
