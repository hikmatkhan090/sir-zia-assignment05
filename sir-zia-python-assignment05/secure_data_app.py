import streamlit as st
import json
import os
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet

# Constants
USER_DATA_FILE = "user_data.json"
SALT = b"this_is_a_secret_salt"

# Utility Functions
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def generate_key(passkey):
    derived_key = pbkdf2_hmac("sha256", passkey.encode(), SALT, 100000, dklen=32)
    return urlsafe_b64encode(derived_key)

def encrypt_data(text, passkey):
    key = generate_key(passkey)
    cipher = Fernet(key)
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text, passkey):
    try:
        key = generate_key(passkey)
        cipher = Fernet(key)
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return None

# Streamlit App Configuration
st.set_page_config(page_title="Secure Data App", page_icon="🔒", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
.vibrant-header {
    background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.header-title {
    color: #FFFF00 !important; /* Bright yellow */
    font-size: 2.2rem;
    margin: 0;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
}
.purple-footer {
    text-align: center;
    margin-top: 20px;
    padding: 10px 0;
    line-height: 1.3;
    background-color: #800080;
    border-radius: 5px;
}
.footer-quote {
    font-style: italic;
    font-size: 13px;
    color: white;
    margin-bottom: 3px;
}
.footer-author {
    font-size: 12px;
    color: #E6E6FA;
}
</style>
""", unsafe_allow_html=True)

# Vibrant Main Header with Purple Gradient and Yellow Text
st.markdown("""
<div class="vibrant-header">
    <h1 class="header-title">🔒 Secure Data Management App</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigate")
menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Store Data", "Retrieve Data"])

# Load user data
user_data = load_user_data()

# Initialize session state
if "username" not in st.session_state:
    st.session_state.username = None

# Register Page
if menu == "Register":
    st.subheader("Create a New Account 📝")
    new_username = st.text_input("Enter a Username")
    new_password = st.text_input("Enter a Password", type="password")

    if st.button("Register"):
        if new_username in user_data:
            st.error("Username already exists. Try another one!")
        else:
            user_data[new_username] = {
                "password": encrypt_data(new_password, new_username),
                "data": ""
            }
            save_user_data(user_data)
            st.success("Account created successfully! 🎉")

# Login Page
elif menu == "Login":
    st.subheader("Login to Your Account 🔑")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in user_data:
            decrypted_password = decrypt_data(user_data[username]["password"], username)
            if decrypted_password == password:
                st.session_state.username = username
                st.success(f"Welcome {username}! 🎯")
            else:
                st.error("Incorrect password.")
        else:
            st.error("Username not found.")

# Store Data Page
elif menu == "Store Data":
    if st.session_state.username:
        st.subheader(f"Store Secret Data 🗂️ (User: {st.session_state.username})")
        data = st.text_area("Enter the data to encrypt and store:")

        if st.button("Encrypt & Store"):
            encrypted = encrypt_data(data, st.session_state.username)
            user_data[st.session_state.username]["data"] = encrypted
            save_user_data(user_data)
            st.success("Data encrypted and stored successfully! 🔒")
    else:
        st.warning("Please login first!")

# Retrieve Data Page
elif menu == "Retrieve Data":
    if st.session_state.username:
        st.subheader(f"Retrieve Your Secret Data 🕵️ (User: {st.session_state.username})")

        if st.button("Decrypt & Show Data"):
            encrypted = user_data[st.session_state.username].get("data", "")
            if encrypted:
                decrypted = decrypt_data(encrypted, st.session_state.username)
                if decrypted:
                    st.success("Here is your decrypted data:")
                    st.code(decrypted)
                else:
                    st.error("Failed to decrypt data. It may be corrupted or wrong key.")
            else:
                st.info("No data found. Please store some first.")
    else:
        st.warning("Please login first!")

# Footer
st.markdown("""
<div class="purple-footer">
    <p class="footer-quote">"Security is not a product, but a process."</p>
    <p class="footer-author">Designed by HIKMAT KHAN</p>
</div>
""", unsafe_allow_html=True)
