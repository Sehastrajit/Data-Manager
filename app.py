import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
# Fetch API key from environment variable
api_key = os.getenv("gemini_api")
if not api_key:
    raise ValueError("No API key found. Please set the gemini_api environment variable.")

# Configure Google Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Input prompt from the user
prompt = st.chat_input("Say something")
if prompt:
    answer = response = model.generate_content(prompt)
    st.write(f"Gemini says: {answer.text}")
