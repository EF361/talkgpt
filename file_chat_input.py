# file_chat_input.py
import streamlit as st

def file_chat_input(placeholder: str = "Type a message..."):
    uploaded_files = st.file_uploader(
        "Attach files (pdf, jpg, png, docx)", 
        type=["pdf", "jpg", "jpeg", "png", "docx"],
        accept_multiple_files=True
    )
    user_input = st.text_input(placeholder, key="chat_input")
    if st.button("Send", key="send_button") and (user_input or uploaded_files):
        return {
            "text": user_input,
            "files": uploaded_files
        }
    return None
