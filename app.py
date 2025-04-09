from flask import Flask, render_template, request, send_from_directory
from scraping import scrape_hotels
import os

app = Flask(__name__)

# Folder where CSV files are saved
DOWNLOAD_FOLDER = 'files'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Retrieve form data from the HTML form
    city_name = request.form['city_name']
    checkin_date = request.form['checkin_date']
    checkout_date = request.form['checkout_date']
    adults = request.form['adults']
    children = request.form['children']
    rooms = request.form['rooms']
    
    # Ensure the 'files/' directory exists
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    # Create the filename and full path for saving the CSV
    filename = f"{city_name}_{checkin_date}_data.csv"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    # Perform hotel scraping and save data
    scrape_hotels(city_name, checkin_date, checkout_date, adults, children, rooms, filepath)

    # Return the page with download link
    return render_template('index.html', message="Data scraping completed!", filename=filename)

@app.route('/download/<filename>')
def download_file(filename):
    # Allow downloading the file from 'files/' directory
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
