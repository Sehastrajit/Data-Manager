import threading
import cv2
import streamlit as st
from matplotlib import pyplot as plt
from streamlit_webrtc import webrtc_streamer
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

# Video frame callback function
lock = threading.Lock()
img_container = {"img": None}

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    with lock:
        img_container["img"] = img
    return frame

ctx = webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

# Plotting histogram of video frames
fig_place = st.empty()
fig, ax = plt.subplots(1, 1)

while ctx.state.playing:
    with lock:
        img = img_container["img"]
    if img is None:
        continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ax.cla()
    ax.hist(gray.ravel(), 256, [0, 256])
    fig_place.pyplot(fig)
