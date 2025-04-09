from flask import Flask, render_template, request, send_from_directory
import os
import pandas as pd
from scraping import scrape_hotels  # ✅ Make sure the filename is 'scraping.py'

app = Flask(__name__)

# ✅ Directory to store scraped CSV files
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # ✅ Get form data
    city_name = request.form['city_name']
    checkin_date = request.form['checkin_date']
    checkout_date = request.form['checkout_date']
    adults = request.form['adults']
    children = request.form['children']
    rooms = request.form['rooms']

    # ✅ Scrape data
    hotel_data = scrape_hotels(
        city=city_name,
        checkin=checkin_date,
        checkout=checkout_date,
        adults=adults,
        children=children,
        rooms=rooms
    )

    # ✅ Save scraped data to CSV
    filename = f"{city_name.replace(' ', '_')}_hotels.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    hotel_data.to_csv(filepath, index=False)

    return render_template('index.html', filename=filename, message="✅ Scraping completed!")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    # ✅ For Render deployment (bind to port 0.0.0.0)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
