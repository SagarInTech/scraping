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

    # ✅ Correct paths set from Render environment
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(
        service=Service(os.environ.get("CHROMEDRIVER_PATH")),
        options=chrome_options
    )
    return driver

def close_popup(driver):
    try:
        close_button = driver.find_element(By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.b02ceec9d7")
        close_button.click()
        print("Popup closed")
    except:
        print("No popup to close")

def load_full_page(driver):
    while True:
        try:
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.ea757ee64b.f1c8772a7d.ea220f5cdc.f870aa1234"))
            )
            button.click()
            print("Clicked show more")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception as e:
            print("No more show more button or error:", e)
            break
    print("Fully loaded page")

def scrape_hotel_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    hotels = soup.find_all('div', {'data-testid': 'property-card'})
    results = []

    for hotel in hotels:
        name_el = hotel.find('div', {'data-testid': 'title'})
        name = name_el.text.strip() if name_el else None

        location_el = hotel.find('span', {'data-testid': 'address'})
        location = location_el.text.strip() if location_el else None

        price_el = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price_text = price_el.text.strip() if price_el else None
        price = int(re.findall(r'\d+', price_text.replace(',', ''))[0]) if price_text else None

        room_el = hotel.find('div', {'data-testid': 'recommended-units'})
        room_info = room_el.find('div', class_='c6f064a3e8') if room_el else None
        room = room_info.text.strip() if room_info else None

        results.append({
            'name': name,
            'location': location,
            'price(in rupees)': price,
            'room_availability': room,
            'date': datetime.now().strftime('%Y-%m-%d')
        })

    return results

def generate_url(city, checkin, checkout, adults, rooms, children):
    return (
        f"https://www.booking.com/searchresults.html?"
        f"ss={city}&checkin={checkin}&checkout={checkout}"
        f"&group_adults={adults}&no_rooms={rooms}&group_children={children}"
    )

def scrape_hotels(city, checkin, checkout, adults, children, rooms):
    driver = setup_driver()
    url = generate_url(city, checkin, checkout, adults, rooms, children)

    driver.get(url)
    time.sleep(5)

    close_popup(driver)
    driver.maximize_window()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - window.innerHeight / 6);")
    time.sleep(5)

    load_full_page(driver)

    html = driver.page_source
    data = scrape_hotel_data(html)

    driver.quit()
    return pd.DataFrame(data)
