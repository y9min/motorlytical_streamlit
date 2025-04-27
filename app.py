import streamlit as st
import pandas as pd
import datetime
import time
import os
from scrape_module import scrape_autotrader, create_price_trend_graph

# Sidebar - Input criteria
st.sidebar.title("Search Criteria")

postcode = st.sidebar.text_input("Postcode", "BB7 3BB")
radius = st.sidebar.selectbox("Search Radius (miles)", [5, 10, 20, 30, 50], index=1)
car_make = st.sidebar.text_input("Car Make", "BMW")
car_model = st.sidebar.text_input("Car Model", "")
variant = st.sidebar.text_input("Variant (Optional)", "")
price_from = st.sidebar.text_input("Price From", "")
price_to = st.sidebar.text_input("Price To", "")

start_scraping = st.sidebar.button("Start Scraping")

# Main app
st.title("AutoTrader Scraper App")
st.write("Set your search criteria on the left and click 'Start Scraping'!")

if start_scraping:
    with st.spinner("Scraping in progress, please wait..."):
        start_time = time.time()
        try:
            criteria = {
                "postcode": postcode,
                "radius": radius,
                "price_from": price_from,
                "price_to": price_to,
                "exclude_writeoff": False,
                "only_writeoff": False,
                "only_n_ireland": False
            }

            cars = [{"make": car_make, "model": car_model, "variant": variant}]

            # Run scraping
            df, metrics, timestamp = scrape_autotrader(cars, criteria, st)

            end_time = time.time()
            elapsed_time = end_time - start_time

            st.success(f"Scraping completed in {elapsed_time:.2f} seconds!")

            # Display metrics
            "average_mileage": avg_mileage,  # 0 if unknown
            "competition_index": competition_index,

            # Show DataFrame
            st.dataframe(df)

            # Download button
            csv_filename = f"autotrader_results_{timestamp}.csv"
            df.to_csv(csv_filename, index=False)
            with open(csv_filename, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name=csv_filename,
                    mime="text/csv"
                )

            # Show graph
            if os.path.exists(f"average_price_trend_{timestamp}.png"):
                st.image(f"average_price_trend_{timestamp}.png", caption="Price Trend Graph")

        except Exception as e:
            st.error(f"An error occurred during scraping: {e}")


