"""
Call Analyzer - File Upload and Analysis

This script allows users to upload either an audio file (.wav) or a transcript (.txt).  
    - If an audio file is uploaded, it is sent to a FastAPI backend for transcription.  
    - If a text file is uploaded, it is processed directly for analysis.  
    - The processed data is stored in `st.session_state` and the user is redirected to the analytics page. 
"""

import streamlit as st
import httpx
import os
import io
import time
import tomllib

def load_toml_config(file_path="config.toml"):
    with open(file_path, "rb") as file:
        return tomllib.load(file)

config = load_toml_config()

FASTAPI_UPLOAD_URL = config["fastapi"]["upload_url"]
FASTAPI_PROCESS_URL = config["fastapi"]["process_url"]

# Page config
st.set_page_config(page_title="Call Analyzer", layout="centered", initial_sidebar_state="collapsed")


st.title("📂 Upload Audio or Transcript Log")

# File uploader with both audio and text file support
ip_file = st.file_uploader("Upload your file (Audio: .wav | Text: .txt)", type=["wav", "txt"])

# Processing file given
if ip_file:
    file_name = ip_file.name
    file_extension = os.path.splitext(file_name)[1].lower()

    st.success(f"✅ {file_name} uploaded successfully!")

    # For audio files
    if file_extension == ".wav":
        st.info("🎵 Detected **Audio File**. Proceeding to transcription...")

        files = {"file": (file_name, ip_file, "audio/wav")}
        
        try:
            with httpx.Client(timeout=1000.0) as client: 
                response = client.post(FASTAPI_UPLOAD_URL, files=files)

            if response.status_code == 200:
                file_path = response.json()["path"]
                st.success(f"✅ File saved at: {file_path}")

                with st.spinner("Processing audio..."):
                    with httpx.Client(timeout=1000.0) as client:
                        process_response = client.get(FASTAPI_PROCESS_URL, params={"file_path": file_path})

                if process_response.status_code == 200:
                    st.session_state["ip_file"] = io.StringIO(process_response.text)
                    st.session_state["file_type"] = 1
                    st.success("✅ Text file stored successfully in session_state!")
                else:
                    st.error("❌ Failed to process audio file.")
            else:
                st.error("❌ Upload failed.")
        
        except httpx.HTTPError as e:
            st.error(f"HTTP Error: {e}")

        st.switch_page("pages/analytics.py")

    # For transcripts
    elif file_extension == ".txt":
        st.info("📄 Detected **Text File**. Proceeding to analysis...")
        with st.spinner("Processing... Please wait."):
            time.sleep(2)
        st.session_state["ip_file"] = ip_file
        st.session_state["file_type"] = 0
        st.switch_page("pages/analytics.py")

    # Wrong file type
    else:
        st.error("❌ Unsupported file type. Please upload a valid audio (.wav) or text (.txt) file.")
        st.stop()