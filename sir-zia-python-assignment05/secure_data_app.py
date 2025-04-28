import streamlit as st
import json
import os
import time
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
from streamlit.components.v1 import html

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

# Animation Components
def loading_animation():
    with st.spinner("🔐 Securing your data..."):
        time.sleep(1.5)

def success_animation():
    html("""
    <div class="success-animation">
        <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/>
            <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
        </svg>
    </div>
    <style>
    .success-animation { margin: 0 auto; }
    .checkmark { width: 50px; height: 50px; display: block; margin: 0 auto; }
    .checkmark__circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 2; stroke-miterlimit: 10; 
        stroke: #4CAF50; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
    .checkmark__check { stroke-dasharray: 48; stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards; }
    @keyframes stroke { 100% { stroke-dashoffset: 0; } }
    </style>
    """)

def lock_animation():
    html("""
    <div class="lock-animation">
        <svg xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#6e48aa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
        </svg>
    </div>
    <style>
    .lock-animation { 
        animation: pulse 1.5s infinite;
        margin: 0 auto;
        text-align: center;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
    """)

# Streamlit App Configuration
st.set_page_config(page_title="Secure Data App", page_icon="🔒", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
/* Vibrant Header */
.vibrant-header {
    background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 25px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    animation: fadeIn 1s ease-in-out;
}
.header-title {
    color: #FFFF00 !important;
    font-size: 2.2rem;
    margin: 0;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
}

/* Footer */
.purple-footer {
    text-align: center;
    margin-top: 20px;
    padding: 10px 0;
    line-height: 1.3;
    background-color: #800080;
    border-radius: 5px;
    animation: slideUp 0.5s ease-out;
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

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Input Fields */
.stTextInput>div>div>input, .stTextArea>div>textarea {
    border-radius: 5px !important;
    border: 1px solid #6e48aa !important;
    transition: all 0.3s ease;
}
.stTextInput>div>div>input:focus, .stTextArea>div>textarea:focus {
    border-color: #9d50bb !important;
    box-shadow: 0 0 0 2px rgba(110,72,170,0.2) !important;
}

/* Buttons */
.stButton>button {
    border-radius: 5px;
    border: 1px solid #6e48aa;
    background-color: #6e48aa;
    color: white;
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #9d50bb;
    border-color: #9d50bb;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# Vibrant Header
st.markdown("""
<div class="vibrant-header">
    <h1 class="header-title">🛡️ Secure Vault Pro</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔐 Navigation")
menu = st.sidebar.selectbox("Menu", ["👤 Register", "🔑 Login", "💾 Store Data", "🔍 Retrieve Data"])

# Load data
user_data = load_user_data()

# Initialize session
if "username" not in st.session_state:
    st.session_state.username = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Welcome Page After Login/Register
def show_welcome_page():
    st.markdown(f"""
    <div style="text-align:center; margin-top: 50px; animation: fadeIn 2s;">
        <h1 style="font-size:3rem; color:#6e48aa;">🎉 Welcome, <span style="color:#9d50bb;">{st.session_state.username}</span>!</h1>
        <p style="font-size:1.2rem; color:gray;">We are excited to have you on board. Explore your secure vault! 🔒</p>
    </div>
    """, unsafe_allow_html=True)

# Main flow
if st.session_state.authenticated:
    show_welcome_page()
else:
    if menu == "👤 Register":
        st.subheader("📝 Create a New Account")
        new_username = st.text_input("🧑‍💻 Enter a Username")
        new_password = st.text_input("🔑 Enter a Password", type="password")

        if st.button("🚀 Register"):
            if new_username in user_data:
                st.error("❌ Username already exists. Try another one!")
            else:
                loading_animation()
                user_data[new_username] = {
                    "password": encrypt_data(new_password, new_username),
                    "data": ""
                }
                save_user_data(user_data)
                st.session_state.username = new_username
                st.session_state.authenticated = True
                success_animation()
                time.sleep(1.5)
                st.rerun()


    elif menu == "🔑 Login":
        st.subheader("🔐 Login to Your Account")
        username = st.text_input("🧑‍💻 Username")
        password = st.text_input("🔑 Password", type="password")

        if st.button("🔓 Login"):
            if username in user_data:
                loading_animation()
                decrypted_password = decrypt_data(user_data[username]["password"], username)
                if decrypted_password == password:
                    st.session_state.username = username
                    st.session_state.authenticated = True
                    success_animation()
                    time.sleep(1.5)
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect password.")
            else:
                st.error("❌ Username not found.")

    elif menu == "💾 Store Data":
        st.warning("⚠️ Please login first!")

    elif menu == "🔍 Retrieve Data":
        st.warning("⚠️ Please login first!")

# Footer
st.markdown("""
<div class="purple-footer">
    <p class="footer-quote">"Security is a process, not a product."</p>
    <p class="footer-author">🔒 Designed by HIKMAT KHAN</p>
</div>
""", unsafe_allow_html=True)
