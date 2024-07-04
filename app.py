import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import io

st.set_page_config(page_title="Data Manager", layout="wide")

# Check for API key
api_key = os.getenv("gemini_api")

if not api_key:
    st.error("Failed to retrieve the gemini_api environment variable. Make sure it's set in your Streamlit Cloud settings.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

# Sidebar for CSV upload
with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
        st.write("CSV Preview:")
        st.write(st.session_state.csv_data.head())

# Main content area
st.title("Data Manager")

# Display conversation history
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Ask about your data or enter a prompt")

if user_input:
    # Add user message to conversation
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Prepare context for Gemini
    context = user_input
    if st.session_state.csv_data is not None:
        csv_info = f"CSV Data Info:\n"
        csv_info += f"Columns: {', '.join(st.session_state.csv_data.columns)}\n"
        csv_info += f"Shape: {st.session_state.csv_data.shape}\n"
        csv_info += f"Sample data:\n{st.session_state.csv_data.head().to_string()}\n"
        context = f"{csv_info}\n\nUser Query: {user_input}"
    
    # Generate and display Gemini's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in model.generate_content(context, stream=True):
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add Gemini's response to conversation
    st.session_state.conversation.append({"role": "assistant", "content": full_response})
    
    # Force a rerun to update the UI
    st.experimental_rerun()

# Display CSV data if available
if st.session_state.csv_data is not None:
    st.header("Uploaded CSV Data")
    st.write(st.session_state.csv_data)