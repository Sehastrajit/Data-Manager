import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import io
import base64

st.set_page_config(page_title="Data Manager", layout="wide", page_icon="assets/data_master.png")

# Function to encode image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get base64 encoded images
user_image = get_image_base64("assets/User.png")
ai_image = get_image_base64("assets/Ai.png")

# Custom CSS to use the images
st.markdown(f"""
<style>
    .stChatMessage [data-testid="StChatMessageContent"] {{
        background-image: none;
        padding-left: 0;
    }}
    .stChatMessage [data-testid="StChatMessageContent"] .stChatIconContent {{
        display: none;
    }}
    .stChatMessage [data-testid="StChatMessageContent"]::before {{
        content: "";
        display: inline-block;
        width: 40px;
        height: 40px;
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        margin-right: 10px;
    }}
    .stChatMessage.user [data-testid="StChatMessageContent"]::before {{
        background-image: url("data:image/png;base64,{user_image}");
    }}
    .stChatMessage.assistant [data-testid="StChatMessageContent"]::before {{
        background-image: url("data:image/png;base64,{ai_image}");
    }}
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("gemini_api")
if not api_key:
    st.error("Failed to retrieve the gemini_api environment variable. Make sure it's set in your Streamlit Cloud settings.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None

def get_dataframe_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()

def generate_csv_context(df):
    info = get_dataframe_info(df)
    describe = df.describe().to_string()
    sample = df.head().to_string()
    return f"""
    CSV Data Information:
    {info}
    Statistical Summary:
    {describe}
    Sample Data (first 5 rows):
    {sample}
    To analyze this data, you can use the following functions:
    1. df.column_name - to access a specific column
    2. df['column_name'] - alternative way to access a specific column
    3. df.groupby('column_name').agg(...) - for grouping and aggregation
    4. df.sort_values('column_name') - for sorting
    5. df[df['column_name'] condition] - for filtering
    When you need to perform calculations or analysis, provide the exact Python code, and I'll execute it and give you the results.
    """

with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
        st.write("CSV Preview:")
        st.write(st.session_state.csv_data.head())
    
    st.markdown("---")
    st.subheader("Developer")
    st.components.v1.html("""
    <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
    <div id="badge-wrapper">
        <div class="badge-base LI-profile-badge" data-locale="en_US" data-size="medium" data-theme="dark" data-type="VERTICAL" data-vanity="sehastrajit-s-0a84b8203" data-version="v1">
        </div>
    </div>
    <style>
        #badge-wrapper * {
            background-color: transparent !important;
            background: none !important;
            box-shadow: none !important;
        }
        .badge-base {
            min-height: 350px;
            position: relative;
        }
        .bdiframe {
            background-color: transparent !important;
        }
        #badge-wrapper::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(38,39,48,255) !important;
            z-index: -1;
        }
    </style>
    """, height=400)

st.title("Data Manager")

for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask about your data or enter a prompt")

if user_input:
    st.session_state.conversation.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    
    if st.session_state.csv_data is not None:
        context = generate_csv_context(st.session_state.csv_data)
        prompt = f"{context}\n\nUser Query: {user_input}\n\nPlease provide a detailed answer, and if any data analysis is needed, include the exact Python code to perform the analysis."
    else:
        prompt = user_input
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in model.generate_content(prompt, stream=True):
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
        if "```python" in full_response:
            code_blocks = full_response.split("```python")
            for block in code_blocks[1:]:
                code = block.split("```")[0].strip()
                try:
                    result = eval(code)
                    st.write("Analysis Result:")
                    st.write(result)
                except Exception as e:
                    st.error(f"Error executing code: {str(e)}")
    
    st.session_state.conversation.append({"role": "assistant", "content": full_response})

if st.session_state.csv_data is not None:
    st.header("Uploaded CSV Data")
    st.write(st.session_state.csv_data)