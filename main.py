import streamlit as st
import langchain_helper as lch
import textwrap
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI API key from the .env file (if available)
openai_api_key_from_env = os.getenv("OPENAI_API_KEY")

st.title("YouTube Assistant")

with st.sidebar:
    with st.form(key='my_form'):
        youtube_url = st.sidebar.text_area(
            label="What is the YouTube video URL?",
            max_chars=50
        )
        query = st.sidebar.text_area(
            label="Ask me about the video?",
            max_chars=50,
            key="query"
        )

        # Populate the OpenAI API key field if it's found in the .env file
        openai_api_key = st.sidebar.text_input(
            label="OpenAI API Key",
            key="langchain_search_api_key_openai",
            max_chars=50,
            type="password",
            value=openai_api_key_from_env if openai_api_key_from_env else ""  # Pre-fill with the env key if available
        )
        
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        submit_button = st.form_submit_button(label='Submit')

if query and youtube_url:
    if not openai_api_key and not openai_api_key_from_env:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        # Pass the OpenAI API key to the helper function
        db = lch.create_db_from_youtube_video_url(youtube_url, openai_api_key or openai_api_key_from_env)
        response, docs = lch.get_response_from_query(db, query)
        st.subheader("Answer:")
        st.text(textwrap.fill(response, width=85))
