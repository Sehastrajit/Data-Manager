import streamlit as st
import google.generativeai as genai
import os

st.write("Checking for environment variables...")

# Try to get the API key from an environment variable
api_key = os.getenv("gemini_api")

if api_key:
    st.success("Successfully retrieved the GEMINI_API environment variable!")
else:
    st.error("Failed to retrieve the GEMINI_API environment variable. Make sure it's set in your Streamlit Cloud settings.")
    st.stop()

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Rest of your app code...
st.write("Gemini API configured successfully!")

# Simple input for testing
user_input = st.text_input("Enter a prompt for Gemini:")
if user_input:
    try:
        response = model.generate_content(user_input)
        st.write("Gemini's response:", response.text)
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")