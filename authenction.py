import pymongo
import streamlit as st
from argon2 import PasswordHasher
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# MongoDB connection
uri = os.getenv('MONGO_URI')
uri2 = st.secrets["MONGO"]["MONGO_URI"]
client = pymongo.MongoClient(uri2)
db = client['LMS']
collection = db['users']

ph = PasswordHasher(time_cost=3, memory_cost=64*1024, parallelism=2)

st.title("Library Management System")

# --- LOGIN FORM ---
st.subheader("Login")
user_name = st.text_input("Username", key="login_user")
password = st.text_input("Password", type="password", key="login_pass")

login_button = st.button("Login")

if login_button:
    user = collection.find_one({"username": user_name})
    if user:
        try:
            if ph.verify(user['password'], password):
                st.success("Login successful")
            else:
                st.error("Incorrect password")
        except:
            st.error("Invalid password hash!")
    else:
        st.warning("User not found. You can register below.")

# --- REGISTRATION FORM ---
st.subheader("Register")
new_user = st.text_input("New Username", key="reg_user")
new_pass = st.text_input("New Password", type="password", key="reg_pass")
register_button = st.button("Register")




if register_button:
    if new_user == "":
        st.warning("Please enter a username.")
    if new_pass == "":
            st.warning("Please enter a password.")
    else:

        if collection.find_one({"username": new_user}):
            st.error("Username already exists!")
        else:
            hashed_pass = ph.hash(new_pass)
            collection.insert_one({"username": new_user, "password": hashed_pass})
            st.success("Registration successful")
