import streamlit as st
import streamlit.components.v1 as components

def book_card(title, author, year, cover_url):
    components.html(
        f"""
        <html>
        <head>
            <style>
                .card {{
                    width: 260px;
                    background: #1e1e2f;
                    color: white;
                    border-radius: 15px;
                    overflow: hidden;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    font-family: Arial, sans-serif;
                    transition: transform 0.2s;
                }}
                .card:hover {{
                    transform: scale(1.05);
                }}
                .card img {{
                    width: 100%;
                    height: 180px;
                    object-fit: cover;
                }}
                .card-content {{
                    padding: 15px;
                }}
                .card-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
                .card-author {{
                    font-size: 14px;
                    color: #bbb;
                    margin-bottom: 12px;
                }}
                .card-year {{
                    font-size: 13px;
                    color: #999;
                    margin-bottom: 12px;
                }}
                .card button {{
                    background: #ff6b6b;
                    color: white;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background 0.3s;
                }}
                .card button:hover {{
                    background: #ff4b4b;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <img src="{cover_url}" alt="Book Cover">
                <div class="card-content">
                    <div class="card-title">{title}</div>
                    <div class="card-author">by {author}</div>
                    <div class="card-year">Published: {year}</div>
                    <button>Borrow</button>
                </div>
            </div>
        </body>
        </html>
        """,
        height=400,
        width=280
    )

# Example usage
st.title("My Books")
book_card(
    "Atomic Habits",
    "James Clear",
    2018,
    "https://m.media-amazon.com/images/I/91bYsX41DVL.jpg"
)

