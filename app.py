import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Gemini AI Chat", page_icon="🤖")

# Check for API key
api_key = os.getenv("gemini_api")

if not api_key:
    st.error("Failed to retrieve the gemini_api environment variable. Make sure it's set in your Streamlit Cloud settings.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize session state for conversation
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Display conversation history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Conditional heading
if not st.session_state.conversation:
    st.title("Welcome to Gemini AI Chat!")
    st.write("Enter a prompt below to start chatting with Gemini.")

# User input
user_input = st.chat_input("Enter your message here")

if user_input:
    # Add user message to conversation
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate and display Gemini's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in model.generate_content(user_input, stream=True):
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add Gemini's response to conversation
    st.session_state.conversation.append({"role": "assistant", "content": full_response})
    
    # Force a rerun to update the UI
    st.experimental_rerun()