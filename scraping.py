import os
import time
import re
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })

    # ✅ Set correct path to Chromium and Chromedriver on Render
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN", "/usr/bin/chromium")
    driver = webdriver.Chrome(
        service=Service(os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")),
        options=chrome_options
    )
    return driver

def close_popup(driver):
    try:
        button = driver.find_element(By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.b02ceec9d7")
        button.click()
        print("Popup closed")
    except:
        print("No popup found")

def load_full_page(driver):
    while True:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.ea757ee64b.f1c8772a7d.ea220f5cdc.f870aa1234"))
            )
            button.click()
            print("Button clicked ..")
            time.sleep(20)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("Scrolled to bottom again")
        except Exception as e:
            print("No more button or error:", e)
            break

def scrape_hotel_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    hotels = soup.find_all('div', {'data-testid': 'property-card'})
    hotels_data = []

    for hotel in hotels:
        name = hotel.find('div', {'data-testid': 'title'})
        location = hotel.find('span', {'data-testid': 'address'})
        price_elem = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        availability = hotel.find('div', {'data-testid': 'recommended-units'})

        price_str = price_elem.text.strip() if price_elem else None
        price = int(re.findall(r'\d+', price_str.replace(',', ''))[0]) if price_str else None

        inner_div = availability.find('div', class_='c6f064a3e8') if availability else None
        availability_text = inner_div.text.strip() if inner_div else None

        hotels_data.append({
            'name': name.text.strip() if name else None,
            'location': location.text.strip() if location else None,
            'price(in rupees)': price,
            'room_availability': availability_text,
            'date': datetime.now().strftime('%Y-%m-%d')
        })

    return hotels_data

def generate_url(city, checkin, checkout, adults, rooms, children):
    return f"https://www.booking.com/searchresults.html?ss={city}&checkin={checkin}&checkout={checkout}&group_adults={adults}&no_rooms={rooms}&group_children={children}"

def scrape_hotels(city, checkin, checkout, adults, children, rooms):
    driver = setup_driver()
    driver.get(generate_url(city, checkin, checkout, adults, rooms, children))

    time.sleep(10)
    close_popup(driver)
    driver.maximize_window()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - window.innerHeight / 6);")
    time.sleep(10)

    load_full_page(driver)

    data = scrape_hotel_data(driver.page_source)
    driver.quit()
    return pd.DataFrame(data)