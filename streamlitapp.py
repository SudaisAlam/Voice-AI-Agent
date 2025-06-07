import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import os
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Voice AI Assistant",
    page_icon="🎤",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
    }
    .header {
        color: #1f77b4;
        text-align: center;
    }
    .response-box {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .highlight {
        background-color: #e6f7ff;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    .search-true {
        background-color: #4CAF50;
    }
    .search-false {
        background-color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

# Backend URL configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# App header
st.markdown("<h1 class='header'>🎤 Voice AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("Record your voice command and get AI-powered responses")

# Initialize session state with safe defaults
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'response' not in st.session_state:
    st.session_state.response = None

# Audio recording section
st.subheader("Record Your Voice")
st.info("Click the microphone to start recording. Speak clearly into your microphone.")

# Record audio
audio_bytes = audio_recorder(
    pause_threshold=3.0, 
    text="",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_size="2x",
)

# Function to send audio to backend
def process_audio(audio_data, filename="recording.wav"):
    try:
        files = {"file": (filename, BytesIO(audio_data), "audio/wav")}
        response = requests.post(f"{BACKEND_URL}/chat/voice", files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Connection failed. Please check if the backend server is running.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Process audio when recorded
if audio_bytes and not st.session_state.get('processing', False):
    st.session_state.processing = True
    st.session_state.response = None
    
    # Display audio player
    st.audio(audio_bytes, format="audio/wav")
    
    with st.spinner("Processing your voice command..."):
        # Send to backend
        response = process_audio(audio_bytes)
        st.session_state.response = response
        st.session_state.processing = False

# Display results if response exists
if st.session_state.get('response'):
    data = st.session_state.response
    
    st.markdown("---")
    st.subheader("AI Response")
    
    with st.container():
        st.markdown("<div class='response-box'>", unsafe_allow_html=True)
        
        # Transcript
        st.markdown("**Your Command:**")
        st.markdown(f"<div class='highlight'>{data['transcript']}</div>", unsafe_allow_html=True)
        
        # AI Response
        st.markdown("**AI Response:**")
        st.markdown(f"<div class='highlight'>{data['response']}</div>", unsafe_allow_html=True)
        
        # Search indicator
        search_status = "search-true" if data["search_triggered"] else "search-false"
        search_text = "Used web search" if data["search_triggered"] else "No web search needed"
        st.markdown(f"**Search Status:** <span class='status-indicator {search_status}'></span>{search_text}", 
                    unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Reset button
if st.session_state.get('processing') or st.session_state.get('response'):
    if st.button("Start New Recording"):
        st.session_state.processing = False
        st.session_state.response = None
        st.experimental_rerun()

# Sidebar information
st.sidebar.title("Configuration")
st.sidebar.markdown(f"**Backend URL:**\n{BACKEND_URL}")
st.sidebar.markdown("""
### How to Use:
1. Click the microphone icon
2. Speak your command clearly
3. Wait for processing
4. View your results
""")
