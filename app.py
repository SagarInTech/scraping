from flask import Flask, render_template, request, send_from_directory, url_for
import os
import pandas as pd
from scraper import scrape_hotels  # Make sure this is your scraping logic

app = Flask(__name__)

# Ensure a directory exists to save the file
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    city_name = request.form['city_name']
    checkin_date = request.form['checkin_date']
    checkout_date = request.form['checkout_date']
    adults = request.form['adults']
    children = request.form['children']
    rooms = request.form['rooms']

    # Call your scraping function
    hotel_data = scrape_hotels(
        city=city_name,
        checkin=checkin_date,
        checkout=checkout_date,
        adults=adults,
        children=children,
        rooms=rooms
    )

    # Save to CSV
    filename = f"{city_name.replace(' ', '_')}_hotels.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    hotel_data.to_csv(filepath, index=False)

    # Show the form again with message and download link
    return render_template('index.html', filename=filename, message="✅ Scraping completed!")

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
