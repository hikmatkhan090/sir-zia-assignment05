import streamlit as st
import hashlib
import json
import os
import time
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac
import re
import requests  # For Lottie Animation

# ====== Configuration ======
DATA_FILE = 'secure_data.json'
SALT = b"secure_salt_value"
LOCKOUT_DURATION = 60  # seconds

# ====== Utility Functions ======

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def generate_key(passkey):
    key = pbkdf2_hmac("sha256", passkey.encode(), SALT, 100000)
    return urlsafe_b64encode(key)

def hash_password(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), SALT, 100000).hex()

def encrypt_data(text, key):
    cipher = Fernet(key)
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted_text, key):
    try:
        cipher = Fernet(generate_key(key))
        return cipher.decrypt(encrypted_text.encode()).decode()
    except:
        return None

def check_password_strength(password):
    if len(password) < 6:
        return "Weak 🔴"
    elif re.search(r"[A-Z]", password) and re.search(r"[0-9]", password):
        return "Strong 🟢"
    else:
        return "Medium 🟡"

# ====== Session Initialization ======

if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "lockout_time" not in st.session_state:
    st.session_state.lockout_time = 0

if "registered_success" not in st.session_state:
    st.session_state.registered_success = False

# ====== App UI Design ======

st.set_page_config(page_title="SecureVault 🔐", page_icon="🔐", layout="centered")

st.markdown("""
    <style>
        .main {background: linear-gradient(to right, #ece9e6, #ffffff);}
        footer {visibility: hidden;}
        .stApp {margin-bottom: 50px;}
    </style>
""", unsafe_allow_html=True)

# ====== Lottie Animation URL for Logo ======
def show_lottie_animation(url):
    st.markdown(
        f'<lottie-player src="{url}"  background="transparent" speed="1" style="width: 150px; height: 150px;" loop autoplay></lottie-player>',
        unsafe_allow_html=True
    )

# ====== Main App ======

stored_data = load_data()

st.title("🔐 SecureVault - Your Private Digital Locker")

# Display Lottie Animation for Logo
show_lottie_animation("https://assets7.lottiefiles.com/packages/lf20_tlthojcp.json")  # Sample Lottie animation link

menu = ["🏠 Home", "🔑 Login", "📝 Register", "💾 Store Data", "📂 Retrieve Data"]
choice = st.sidebar.selectbox("Navigate", menu)

# ====== Home ======
if choice == "🏠 Home":
    st.header("Welcome to SecureVault! 🚀")
    st.write("""
    This app allows you to securely **store** and **retrieve** your data 🔐  
    All your information is encrypted and protected with your personal passkey 🛡️  
    """)
    st.success("Get started by registering or logging in from the sidebar ➡️")

# ====== Register ======
elif choice == "📝 Register":
    st.header("Create a New Account 🧑‍💻")

    with st.form("Register Form"):
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        password_strength = check_password_strength(password)
        st.caption(f"Password Strength: {password_strength}")

        submit = st.form_submit_button("Register 🚀")

    if submit:
        if not username or not password:
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match ❌")
        elif username in stored_data:
            st.error("Username already exists! Try another one.")
        else:
            stored_data[username] = {"password": hash_password(password), "data": []}
            save_data(stored_data)
            st.session_state.registered_success = True
            st.success("Account created successfully! 🎉 Redirecting to Login page...")
            time.sleep(2)
            st.rerun()

# ====== Login ======
elif choice == "🔑 Login":
    st.header("Login to Your Vault 🔓")

    if st.session_state.registered_success:
        st.success("Account created successfully! Now login 🔑")
        st.session_state.registered_success = False

    if time.time() < st.session_state.lockout_time:
        remaining_time = int(st.session_state.lockout_time - time.time())
        st.error(f"🚫 Too many failed attempts. Please wait {remaining_time} seconds.")
        st.stop()

    with st.form("Login Form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login 🔑")

    if submit:
        if username in stored_data and stored_data[username]["password"] == hash_password(password):
            st.session_state.authenticated_user = username
            st.session_state.failed_attempts = 0
            st.success(f"Welcome back, {username}! 🎉")
            st.balloons()
            time.sleep(1)
            st.rerun()

        else:
            st.session_state.failed_attempts += 1
            remaining_attempts = 3 - st.session_state.failed_attempts
            st.error(f"Invalid credentials! {remaining_attempts} attempts left.")

            if st.session_state.failed_attempts >= 3:
                st.session_state.lockout_time = time.time() + LOCKOUT_DURATION
                st.error("🚫 Too many failed attempts. You are locked out temporarily!")
                st.stop()

# ====== After Login – Store Data ======
elif choice == "💾 Store Data":
    if not st.session_state.authenticated_user:
        st.warning("⚠️ Please login first to store your data.")
    else:
        st.header("Store Your Secret Data 📂")
        with st.form("Store Form"):
            data = st.text_area("Enter the data you want to encrypt 🔒")
            passkey = st.text_input("Enter a secure passphrase", type="password")
            submit = st.form_submit_button("Encrypt & Store 💾")

        if submit:
            if data and passkey:
                encrypted = encrypt_data(data, passkey)
                stored_data[st.session_state.authenticated_user]["data"].append(encrypted)
                save_data(stored_data)
                st.success("Your data has been securely stored! 🛡️")
                st.balloons()
            else:
                st.error("Please provide both data and passkey.")

# ====== Footer ======

st.markdown("""
    <hr>
    <center>
    Made with ❤️ by <strong>HIKMAT KHAN</strong> <br>
    [LinkedIn](https://www.linkedin.com/in/hikmat-khan-652301256//) | [GitHub](https://github.com/hikmatkhan090/) | [Streamlit Profile](https://https://share.streamlit.io/)
    </center>
""", unsafe_allow_html=True)
