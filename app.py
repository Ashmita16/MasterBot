import streamlit as st
import os
import asyncio
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from pypdf import PdfReader

def configure_genai():
    """Configure the Google AI API."""
    api_key = os.getenv("GOOGLE_API_KEY_NEW")  # Set API key in environment
    if not api_key:
        st.error("Google API key is missing. Set the 'GOOGLE_API_KEY_NEW' environment variable.")
        return None

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-pro")

text_model = configure_genai()

def extract_pdf_text(uploaded_file):
    """Extracts text from a PDF file."""
    reader = PdfReader(uploaded_file)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen for audio input and recognize speech."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙️ Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand."
        except sr.RequestError:
            return "Speech recognition service unavailable."

async def run_listen():
    """Async wrapper for listen function."""
    return await asyncio.to_thread(listen)

st.set_page_config(page_title="MasterBot 👑", layout="wide")

if st.sidebar.button("🔄 Start New Session"):
    st.session_state.clear()  
    st.rerun()  

st.sidebar.markdown("<h2 style='text-align: center;'>MasterBot Features 👑</h2>", unsafe_allow_html=True)
choice = st.sidebar.radio("Choose:", ["💬 Chat with MasterBot", "📄 Upload a PDF", "🎤 Voice Assistant"])

output_mode = st.sidebar.selectbox("Select Output Mode:", ["Text Only", "Voice Only", "Both"], index=2)

if choice == "💬 Chat with MasterBot":
    st.markdown("<h1 style='text-align: center;'>💬 MasterBot Chat</h1>", unsafe_allow_html=True)
    st.write("---")


    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input("Type your query here...")

    with col2:
        send_button = st.button("📨 Send")

    if send_button and user_input:
        response = text_model.generate_content(user_input).text
        st.session_state.chat_history.append(("🧑‍💻 You", user_input))
        st.session_state.chat_history.append(("MasterBot 👑", response))

        if output_mode in ["Voice Only", "Both"]:
            speak(response)
        if output_mode in ["Text Only", "Both"]:
            st.markdown(f"<div style='background-color:#d1e7fd; padding:10px; border-radius:10px;'><b>MasterBot:</b> {response}</div>", unsafe_allow_html=True)
          
elif choice == "📄 Upload a PDF":
    st.markdown("<h1 style='text-align: center;'>📄 Upload a PDF Document</h1>", unsafe_allow_html=True)
    st.write("---")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        full_text = extract_pdf_text(uploaded_file)
        st.markdown(f"<div style='background-color:#f8f9fa; padding:15px; border-radius:10px;'><b>Extracted Text from PDF:</b><p style='white-space: pre-wrap;'>{full_text}</p></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input("Ask a question based on the PDF:")

        with col2:
            query_button = st.button("📨 Ask")

        if query_button and full_text:
            context = f"Context: {full_text}\n\nQuestion: {query}"
            response = asyncio.run(asyncio.to_thread(text_model.generate_content, context)).text

            if output_mode in ["Voice Only", "Both"]:
                speak(response)
            if output_mode in ["Text Only", "Both"]:
                st.markdown(f"<div style='background-color:#d1e7fd; padding:15px; border-radius:10px;'><b>MasterBot's Response:</b><p>{response}</p></div>", unsafe_allow_html=True)

elif choice == "🎤 Voice Assistant":
    st.markdown("<h1 style='text-align: center;'>🎤 MasterBot Voice Assistant</h1>", unsafe_allow_html=True)
    st.write("---")

    if st.button("🎤 Start Listening"):
        text = asyncio.run(run_listen())  # ✅ FIXED: Uses asyncio.run() safely
        st.write("🗣️ **You said:**", text)

        if text.lower() != "sorry, i couldn't understand.":
            response = text_model.generate_content(text).text
            if output_mode in ["Voice Only", "Both"]:
                speak(response)
            if output_mode in ["Text Only", "Both"]:
                st.write("👑 **MasterBot:**", response)
