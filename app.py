import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
# Fetch API key from environment variable
api_key = st.secrets["gemini_api"]
if not api_key:
    raise ValueError("No API key found. Please set the gemini_api environment variable.")

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Input prompt from the user
prompt = st.chat_input("Say something")
if prompt:
    answer = model.generate_content(prompt)
    st.write(f"Gemini says: {answer.text}")