from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })

    # Important: Set binary location for Chromium in Render
    options.binary_location = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def close_popup(driver):
    try:
        close_popup_button = driver.find_element(By.CSS_SELECTOR, "button.dba1b3bddf.e99c25fd33.aabf155f9a.f42ee7b31a.a86bcdb87f.b02ceec9d7")
        close_popup_button.click()
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
            print("Scrolled back to the bottom of the page")
        except Exception as e:
            print("Button is no longer available or an error occurred:", e)
            break
    print("Finished clicking the button")

def scrape_hotel_data(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    hotels = soup.find_all('div', {'data-testid': 'property-card'})
    hotels_data = []

    for hotel in hotels:
        name_element = hotel.find('div', {'data-testid': 'title'})
        name = name_element.text.strip() if name_element else None

        location_element = hotel.find('span', {'data-testid': 'address'})
        location = location_element.text.strip() if location_element else None

        price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price_str = price_element.text.strip() if price_element else None

        if price_str:
            price = int(re.findall(r'\d+', price_str.replace(',', ''))[0])
        else:
            price = None

        room_availability_element = hotel.find('div', {'data-testid': 'recommended-units'})
        if room_availability_element:
            inner_div = room_availability_element.find('div', class_='c6f064a3e8')
            room_availability = inner_div.text.strip() if inner_div else None
        else:
            room_availability = None

        today = datetime.now()
        checkin_date = today.strftime('%Y-%m-%d')

        hotels_data.append({
            'name': name,
            'location': location,
            'price(in rupees)': price,
            'room_availability': room_availability,
            'date': checkin_date
        })

    return hotels_data

def generate_url(city_name, checkin_date, checkout_date, adults, rooms, children):
    return f"https://www.booking.com/searchresults.html?ss={city_name}&checkin={checkin_date}&checkout={checkout_date}&group_adults={adults}&no_rooms={rooms}&group_children={children}"

def scrape_hotels(city, checkin, checkout, adults, children, rooms):
    driver = setup_driver()
    url = generate_url(city, checkin, checkout, adults, rooms, children)

    driver.get(url)
    time.sleep(10)

    close_popup(driver)
    driver.maximize_window()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - window.innerHeight / 6);")
    time.sleep(10)

    load_full_page(driver)

    page_source = driver.page_source
    hotels_data = scrape_hotel_data(page_source)

    driver.quit()
    return pd.DataFrame(hotels_data)
