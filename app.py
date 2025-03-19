from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

# --- News API Configuration ---
API_KEY = "f37fdd1cfb0c461877e66a006a6d717f"  # Replace with a real API key
NEWS_URL = f"https://gnews.io/api/v4/top-headlines?token={API_KEY}&lang=en"

# --- Database Setup ---
def create_connection():
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row  # Enables column access by name
    return conn

def init_db():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Read Saved News ---
@app.route("/")
def index():
    conn = create_connection()
    news_articles = conn.execute("SELECT * FROM news").fetchall()
    conn.close()
    return render_template("index.html", news_articles=news_articles)

# --- Fetch Live News from API ---
@app.route("/fetch-news")
def fetch_news():
    response = requests.get(NEWS_URL)
    if response.status_code == 200:
        news_data = response.json().get("articles", [])
    else:
        news_data = []
    
    return render_template("fetch_news.html", news_data=news_data)

# --- Add Selected News to Database ---
@app.route("/save-news", methods=["POST"])
def save_news():
    selected_news = request.form.getlist("selected_news")

    conn = create_connection()
    cursor = conn.cursor()

    for news in selected_news:
        title, content, source = news.split("|||")  # Splitting the combined data
        cursor.execute("INSERT INTO news (title, content, source) VALUES (?, ?, ?)", (title, content, source))

    conn.commit()
    conn.close()
    
    return redirect(url_for("index"))

# --- Delete News Article ---
@app.route("/delete/<int:id>")
def delete_news(id):
    conn = create_connection()
    conn.execute("DELETE FROM news WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
