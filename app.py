from flask import Flask, render_template, request
from scraper import run_scraper
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    query = request.form.get("query")
    if query:
        data = run_scraper(query)
        return render_template("result.html", data=data, query=query)
    return render_template("index.html", error="Please enter a search query.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use dynamic port from Render
    app.run(host="0.0.0.0", port=port, debug=True)  # Bind to 0.0.0.0
