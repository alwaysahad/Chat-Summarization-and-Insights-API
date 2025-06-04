import streamlit as st
import requests
from datetime import datetime
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
LOGIN_URL = f"{API_URL}/users/auth/login"
REGISTER_URL = f"{API_URL}/users/auth/register"

# Page configuration
st.set_page_config(
    page_title="Chat Summarization",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
    }
    .chat-message.assistant {
        background-color: #475063;
    }
    .chat-message .content {
        display: flex;
        flex-direction: column;
    }
    .chat-message .timestamp {
        font-size: 0.8rem;
        color: #a0a0a0;
        margin-top: 0.5rem;
    }
    .stButton > button {
        width: 100%;
        margin-top: 1rem;
    }
    .summary-box, .sentiment-box {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "sentiment" not in st.session_state:
        st.session_state.sentiment = None

def login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            LOGIN_URL,
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        st.session_state.jwt_token = data["access_token"]
        st.session_state.username = username
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

def register(username: str, password: str) -> bool:
    try:
        response = requests.post(
            REGISTER_URL,
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        st.success("Registration successful! Please log in.")
        return True
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code == 400:
            st.error("Username already registered.")
        else:
            st.error(f"Registration failed: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return False

def send_message(message: str) -> Dict:
    """Send a message to the API."""
    if not st.session_state.conversation_id:
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    payload = {
        "conversation_id": st.session_state.conversation_id,
        "user_id": st.session_state.username,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    
    try:
        response = requests.post(f"{API_URL}/chats", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def get_conversation_history() -> List[Dict]:
    """Retrieve conversation history from the API."""
    if not st.session_state.conversation_id:
        return []
    
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    try:
        response = requests.get(f"{API_URL}/chats/{st.session_state.conversation_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error retrieving conversation: {str(e)}")
        return []

def get_summary() -> str:
    """Get conversation summary from the API."""
    if not st.session_state.conversation_id:
        return "No conversation to summarize"
    
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    try:
        response = requests.post(
            f"{API_URL}/chats/summarize",
            json={"conversation_id": st.session_state.conversation_id},
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("summary", "No summary available")
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting summary: {str(e)}")
        return "Error retrieving summary"

def get_sentiment() -> str:
    if not st.session_state.conversation_id:
        return "No conversation to analyze"
    headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
    try:
        response = requests.post(
            f"{API_URL}/chats/insights",
            json={"conversation_id": st.session_state.conversation_id, "insight_type": "sentiment"},
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("insight", "No sentiment available")
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting sentiment: {str(e)}")
        return "Error retrieving sentiment"

def display_chat_message(message: Dict, is_user: bool):
    if is_user:
        role_label = "User"
    else:
        role_label = "✔✔"  # Double tick for assistant
    timestamp = datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat()))
    st.markdown(f"""
        <div class="chat-message {'user' if is_user else 'assistant'}">
            <div class="content">
                <strong>{role_label}</strong>
                <p>{message.get('message', '')}</p>
                <span class="timestamp">{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    # Title and description
    st.title("💬 Chat Summarization Interface")
    st.markdown("""
        Welcome to the Chat Summarization Interface! This tool allows you to:
        - Send and receive messages in real-time
        - View your conversation history
        - Generate AI-powered summaries and sentiment analysis of your conversations
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Login/Sign Up forms if not authenticated
    if not st.session_state.jwt_token:
        st.sidebar.header("🔐 Login or Sign Up")
        tabs = st.sidebar.tabs(["Login", "Sign Up"])
        with tabs[0]:
            with st.form("login_form"):
                username = st.text_input("Username", value="", key="login_username")
                password = st.text_input("Password", type="password", value="", key="login_password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    if login(username, password):
                        st.success("Login successful!")
                        st.rerun()
        with tabs[1]:
            with st.form("signup_form"):
                new_username = st.text_input("Username", value="", key="signup_username")
                new_password = st.text_input("Password", type="password", value="", key="signup_password")
                submitted = st.form_submit_button("Sign Up")
                if submitted:
                    register(new_username, new_password)
        st.stop()
    
    # Sidebar for user configuration
    with st.sidebar:
        st.header("👤 User Settings")
        st.markdown(f"**Logged in as:** `{st.session_state.username}`")
        st.markdown("---")
        
        # Conversation controls
        st.subheader("Conversation Controls")
        if st.button("🆕 New Conversation", use_container_width=True):
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.session_state.summary = None
            st.session_state.sentiment = None
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.jwt_token = None
            st.session_state.username = ""
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.session_state.summary = None
            st.session_state.sentiment = None
            st.success("Logged out successfully.")
            st.rerun()
    
    # Main chat interface
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for message in st.session_state.messages:
            display_chat_message(message, message["role"] == "user")
    
    # Chat input
    with st.container():
        st.markdown("---")
        prompt = st.chat_input("Type your message here...", key="chat_input")
        
        if prompt:
            # Add user message to chat
            st.session_state.messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            })
            display_chat_message({"message": prompt, "timestamp": datetime.now().isoformat()}, True)
            
            # Send message to API
            response = send_message(prompt)
            if response:
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Message sent successfully!",
                    "timestamp": datetime.now().isoformat()
                })
                display_chat_message({
                    "message": "Message sent successfully!",
                    "timestamp": datetime.now().isoformat()
                }, False)
    
    # Summary and Sentiment Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Summarize Conversation", use_container_width=True):
            st.session_state.summary = get_summary()
    with col2:
        if st.button("😊 Analyze Sentiment", use_container_width=True):
            st.session_state.sentiment = get_sentiment()
    
    # Display Results
    if st.session_state.summary:
        st.markdown(f"""
            <div class="summary-box">
                <b>Summary:</b><br>{st.session_state.summary}
            </div>
        """, unsafe_allow_html=True)
    if st.session_state.sentiment:
        st.markdown(f"""
            <div class="sentiment-box">
                <b>Sentiment:</b><br>{st.session_state.sentiment}
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 