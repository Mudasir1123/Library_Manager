import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import pytesseract

# File to store library data
LIBRARY_FILE = "library.json"

# Ensure the 'covers' directory exists
covers_dir = "covers"
os.makedirs(covers_dir, exist_ok=True)

# Set Tesseract OCR path (update this based on your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Streamlit page configuration with custom theme
st.set_page_config(
    page_title="📚 Personal Library Manager",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
st.markdown("""
    <style>
        body {
            background-color: #f4f4f4;
        }
        .stApp {
            background-color: #f7f7f7;
        }
        .css-1d391kg {
            background-color: #ffffff;
        }
        .stButton button {
            background-color: #2a9d8f !important;
            color: white !important;
            font-size: 16px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton button:hover {
            background-color: #1e7a6d !important;
            transform: scale(1.05);
        }
        .stTextInput, .stNumberInput, .stTextArea {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Load or create library data
def load_library():
    try:
        with open(LIBRARY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_library(library):
    with open(LIBRARY_FILE, "w") as file:
        json.dump(library, file, indent=4)

# Add a book function
def add_book(library, title, author, year, genre, read, rating=0, notes=""):
    book = {
        "title": title,
        "author": author,
        "year": int(year),
        "genre": genre,
        "read": read,
        "rating": rating,
        "notes": notes,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    library.append(book)
    save_library(library)
    st.success(f"✅ **'{title}'** added successfully!")

# Remove a book function
def remove_book(library, title):
    for book in library:
        if book["title"].lower() == title.lower():
            library.remove(book)
            save_library(library)
            st.success(f"🗑 **'{title}'** removed successfully!")
            st.rerun()
            return
    st.error("⚠️ Book not found!")

# Upload and Extract Text
st.sidebar.header("📂 Upload Book Cover")
cover_image = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if cover_image:
    img = Image.open(cover_image)
    st.sidebar.image(img, caption="📸 Uploaded Cover", use_container_width=True)
    
    # Save image
    image_path = os.path.join(covers_dir, cover_image.name)
    img.save(image_path)

    # Extract text using OCR
    extracted_text = pytesseract.image_to_string(img)
    st.sidebar.subheader("📝 Extracted Text")
    st.sidebar.text_area("OCR Output", extracted_text, height=150)

# Load library data
library = load_library()

# Sidebar navigation with icons
st.sidebar.header("📚 Library Menu")
menu = st.sidebar.radio("📌 Select an option", ["➕ Add Book", "🔍 Search Books", "📜 View All Books", "📊 Library Stats", "🗑 Remove a Book"])

# Add Book Section
if menu == "➕ Add Book":
    st.subheader("📖 Add a New Book")
    
    with st.form("add_book_form"):
        title = st.text_input("📕 Book Title")
        author = st.text_input("✍️ Author")
        year = st.number_input("📅 Publication Year", min_value=0, max_value=datetime.now().year, value=datetime.now().year, format="%d")
        genre = st.text_input("🎭 Genre")
        read = st.checkbox("📖 Have you read this book?")
        rating = st.slider("⭐ Rating (if read)", 0, 5, 0)
        notes = st.text_area("📝 Notes (optional)")
        submitted = st.form_submit_button("➕ Add Book")
        
        if submitted:
            if title and author and genre:
                add_book(library, title, author, year, genre, read, rating, notes)
            else:
                st.error("⚠️ Please fill in all required fields before submitting.")

# Search Books Section
elif menu == "🔍 Search Books":
    st.subheader("🔎 Search for a Book")

    if library:
        search_query = st.selectbox("📖 Select a book", [""] + [f"{book['title']} - {book['author']}" for book in library])

        if search_query:
            selected_title = search_query.split(" - ")[0]  
            results = [book for book in library if book["title"] == selected_title]

            if results:
                for book in results:
                    with st.expander(f"📖 {book['title']} by {book['author']} ({book['year']})", expanded=True):
                        st.markdown(f"**Genre:** {book['genre']}")
                        st.markdown(f"**Read:** {'✅ Yes' if book['read'] else '❌ No'}")
                        st.markdown(f"**Rating:** {'⭐' * book['rating']}")
                        if book['notes']:
                            st.markdown(f"**Notes:** {book['notes']}")

# View All Books Section
elif menu == "📜 View All Books":
    st.subheader("📚 All Books in Your Library")
    if not library:
        st.info("📚 Your library is empty.")
    else:
        for book in library:
            st.markdown(f"📖 **{book['title']}** by *{book['author']}* ({book['year']})")

# Remove a Book Section
elif menu == "🗑 Remove a Book":
    st.subheader("🗑 Remove a Book")
    book_titles = [book["title"] for book in library]
    
    if book_titles:
        title = st.selectbox("❌ Select a book to remove", [""] + book_titles)
        if title and title != "":
            if st.button("🗑 Remove Book"):
                remove_book(library, title)
    else:
        st.info("📚 No books to remove.")

# Library Statistics Section
elif menu == "📊 Library Stats":
    st.subheader("📊 Library Statistics")
    
    total_books = len(library)
    read_books = sum(1 for book in library if book["read"])
    unread_books = total_books - read_books
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📚 Total Books", total_books)
    col2.metric("✅ Books Read", read_books)
    col3.metric("📖 Books Unread", unread_books)

    st.progress(int(percentage_read))

    genres = {book["genre"]: 0 for book in library}
    for book in library:
        genres[book["genre"]] += 1
    
    st.subheader("📌 Popular Genres")
    for genre, count in genres.items():
        st.markdown(f"- **{genre}**: {count} books")
