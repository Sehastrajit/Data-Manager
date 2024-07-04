import os
import subprocess
import sys

# Function to install packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])

# Upgrade pip
try:
    install("pip")
except subprocess.CalledProcessError as e:
    print(f"Failed to upgrade pip: {e}")
    sys.exit(1)

# List of required packages
required_packages = [
    'streamlit',
    'google-generativeai',
    'python-dotenv'
]

# Install required packages
for package in required_packages:
    try:
        install(package)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        sys.exit(1)

# Import installed packages
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
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
    answer = model.generate_content(prompt)
    st.write(f"Gemini says: {answer.text}")