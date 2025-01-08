import os
import streamlit as st
from dotenv import load_dotenv
from services import ContentRepurposer
import pyperclip
from pathlib import Path

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(page_title="Content Repurposer", page_icon="🐦", layout="wide")

# Custom CSS
st.markdown(
    """
<style>
    .tweet-box {
        background-color: #181211;
        border: 1px solid #e1e8ed;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .copy-button {
        background-color: #1DA1F2;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
    }
    .main-header {
        color: #1DA1F2;
        text-align: center;
    }
    .hashtag {
        color: #1DA1F2;
        background-color: #E8F5FE;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        display: inline-block;
    }
</style>
""",
    unsafe_allow_html=True,
)


def create_temp_pdf(uploaded_file):
    """Create a temporary PDF file from uploaded content"""
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    temp_path = temp_dir / "uploaded_pdf.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    return str(temp_path)


def initialize_session_state():
    """Initialize session state variables"""
    if "tweets" not in st.session_state:
        st.session_state.tweets = None
    if "hashtags" not in st.session_state:
        st.session_state.hashtags = None


def copy_text_and_show_success(text, success_key):
    """Copy text to clipboard and show success message"""
    try:
        pyperclip.copy(text)
        st.success("Copied to clipboard!", icon="✅")
    except Exception as e:
        st.error(f"Failed to copy: {str(e)}")


def main():
    initialize_session_state()

    # Header
    st.markdown(
        "<h1 class='main-header'>📄 Content to Twitter Thread 🐦</h1>",
        unsafe_allow_html=True,
    )

    # Create two columns for layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Upload PDF")
        uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"])

        if uploaded_file:
            st.success("PDF uploaded successfully!")

            if st.button("Generate Twitter Thread", key="generate"):
                with st.spinner("Generating Twitter thread..."):
                    try:
                        # Get Google API key
                        google_api_key = os.getenv("GOOGLE_API_KEY")
                        if not google_api_key:
                            st.error(
                                "Google API key not found. Please check your .env file."
                            )
                            return

                        # Save uploaded file
                        pdf_path = create_temp_pdf(uploaded_file)

                        # Process PDF and generate thread
                        repurposer = ContentRepurposer()
                        thread = repurposer.process_article(pdf_path)

                        # Store results in session state
                        st.session_state.tweets = thread.tweets
                        st.session_state.hashtags = thread.hashtags

                        # Clean up temporary file
                        os.remove(pdf_path)

                    except Exception as e:
                        st.error(f"Error generating thread: {str(e)}")

    with col2:
        if st.session_state.tweets:
            st.markdown("### Generated Twitter Thread")

            # Copy entire thread section
            st.markdown("#### Copy Complete Thread")
            all_tweets = "\n\n".join(st.session_state.tweets)
            if st.button("📋 Copy Entire Thread"):
                copy_text_and_show_success(all_tweets, "thread")

            # Display individual tweets
            st.markdown("#### Individual Tweets")
            for i, tweet in enumerate(st.session_state.tweets, 1):
                tweet_col1, tweet_col2 = st.columns([4, 1])

                with tweet_col1:
                    st.markdown(
                        f"""
                    <div class='tweet-box'>
                        <p>{tweet}</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with tweet_col2:
                    if st.button("📋", key=f"tweet_{i}"):
                        copy_text_and_show_success(tweet, f"tweet_{i}")

            # Display hashtags
            if st.session_state.hashtags:
                st.markdown("### Suggested Hashtags")

                # Display hashtags with copy button
                hashtags_text = " ".join(st.session_state.hashtags)
                hashtags_col1, hashtags_col2 = st.columns([4, 1])

                with hashtags_col1:
                    hashtags_html = " ".join(
                        [
                            f"<span class='hashtag'>{hashtag}</span>"
                            for hashtag in st.session_state.hashtags
                        ]
                    )
                    st.markdown(hashtags_html, unsafe_allow_html=True)

                with hashtags_col2:
                    if st.button("📋 Copy Tags"):
                        copy_text_and_show_success(hashtags_text, "hashtags")


if __name__ == "__main__":
    main()
