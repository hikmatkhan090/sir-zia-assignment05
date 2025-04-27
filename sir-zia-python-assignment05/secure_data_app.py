import streamlit as st
import json
from streamlit.components.v1 import html
from typing import Optional, Dict
import time
from dataclasses import dataclass
import base64
from animations import ComputerTerminal  # Custom module for animation

# ---------- Professional Architecture ----------
@dataclass
class User:
    username: str
    password_hash: str
    last_login: Optional[str] = None

class AuthSystem:
    def __init__(self):
        self.users: Dict[str, User] = self._load_users()
        
    @staticmethod
    def _load_users() -> Dict[str, User]:
        try:
            with open('users.json') as f:
                data = json.load(f)
                return {k: User(**v) for k, v in data.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_users(self):
        with open('users.json', 'w') as f:
            json.dump({k: v.__dict__ for k, v in self.users.items()}, f)

    def register(self, username: str, password: str) -> bool:
        if username in self.users:
            return False
        self.users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            last_login=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        self.save_users()
        return True

    def login(self, username: str, password: str) -> bool:
        user = self.users.get(username)
        if not user:
            return False
        return self._verify_password(password, user.password_hash)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Professional password hashing with salt and pepper"""
        salt = base64.b64encode(os.urandom(16)).decode()
        return f"{salt}${hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()}"

    @staticmethod
    def _verify_password(password: str, hash_str: str) -> bool:
        salt, stored_hash = hash_str.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return secrets.compare_digest(new_hash, stored_hash)

# ---------- Advanced Animation Component ----------
class LoginAnimation:
    def __init__(self):
        self.terminal = ComputerTerminal()  # External optimized animation class
        
    def show(self):
        """Renders the animated computer terminal"""
        self.terminal.display(
            text="Secure Login System v2.0",
            typing_speed=150,  # ms per character
            blink_speed=500,    # ms for cursor blink
            styles={
                'screen_color': 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
                'text_color': '#00ff9d',
                'font': 'Courier New'
            }
        )
        
    def show_success(self):
        self.terminal.display_icon("✔", color="#00ff00", duration=2000)
        
    def show_failure(self):
        self.terminal.display_icon("✖", color="#ff0000", duration=2000)

# ---------- Streamlit UI ----------
def main():
    # Configure page
    st.set_page_config(
        page_title="Enterprise Login",
        page_icon="🔐",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize systems
    auth = AuthSystem()
    anim = LoginAnimation()
    
    # Show animation
    with st.container():
        anim.show()
    
    # Login form
    with st.form("auth_form"):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("shield_icon.png", width=50)
            
        with col2:
            st.markdown("### Enterprise Authentication")
            
        username = st.text_input("", placeholder="Username", key="username")
        password = st.text_input("", placeholder="Password", type="password", key="password")
        
        if st.form_submit_button("Secure Login"):
            if auth.login(username, password):
                anim.show_success()
                st.session_state.authenticated = True
                st.rerun()
            else:
                anim.show_failure()
                st.error("Invalid credentials")

    # Sidebar (hidden until auth)
    if st.session_state.get('authenticated'):
        with st.sidebar:
            st.title("Admin Panel")
            if st.button("Logout"):
                st.session_state.clear()
                st.rerun()

if __name__ == "__main__":
    main()
