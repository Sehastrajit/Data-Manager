import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import io
import json

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

# Function to get DataFrame info
def get_dataframe_info(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    return buffer.getvalue()

# Function to generate CSV context
def generate_csv_context(df):
    info = get_dataframe_info(df)
    describe = df.describe().to_string()
    sample = df.head().to_string()
    
    context = f"""
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
    return context

# Sidebar for CSV upload and LinkedIn badge instructions
with st.sidebar:
    st.header("Upload CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        st.session_state.csv_data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")
        st.write("CSV Preview:")
        st.write(st.session_state.csv_data.head())
    
    # Add LinkedIn badge instructions
    st.markdown("---")
    st.subheader("LinkedIn Public Profile Badge Builder")
    st.markdown("""
    Promote your profile by adding a badge to your blog, online resume, or website.
    
    **Step 1:** Copy and paste the following script anywhere in your page (you only need to do this once)
    ```html
    <script src="https://platform.linkedin.com/badges/js/profile.js" async defer type="text/javascript"></script>
    ```
    
    **Step 2:** Choose a badge size and copy the corresponding code:
    
    - **Small**
    - **Medium**
    - **Large**
    - **Extra-large**
    
    (Replace with actual badge code for each size)
    
    By using these scripts, you agree to the LinkedIn Plugin Terms of Use.
    """)
    
    st.markdown("---")
    st.markdown("Created by [Sehastrajit S](https://www.linkedin.com/in/sehastrajit-s-0a84b8203/)")
    st.markdown("Member of the Young Generation Coding Club @ VIT | certified GCCP, and Azure | Aspiring for MS in CS in the USA, Fall '25.")

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
    if st.session_state.csv_data is not None:
        context = generate_csv_context(st.session_state.csv_data)
        prompt = f"{context}\n\nUser Query: {user_input}\n\nPlease provide a detailed answer, and if any data analysis is needed, include the exact Python code to perform the analysis."
    else:
        prompt = user_input
    
    # Generate and display Gemini's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in model.generate_content(prompt, stream=True):
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
        # Check if there's Python code in the response
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
    
    # Add Gemini's response to conversation
    st.session_state.conversation.append({"role": "assistant", "content": full_response})
    
    # Force a rerun to update the UI
    st.experimental_rerun()

# Display CSV data if available
if st.session_state.csv_data is not None:
    st.header("Uploaded CSV Data")
    st.write(st.session_state.csv_data)