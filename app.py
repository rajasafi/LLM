
import streamlit as st
from dotenv import load_dotenv
from html import escape
load_dotenv()
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Custom CSS styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .stTextInput input {
            border-radius: 20px;
            padding: 10px 15px;
        }
        .stButton button {
            width: 100%;
            border-radius: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #45a049;
            transform: scale(1.05);
        }
        .summary-box {
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: black;
            margin-top: 20px;
        }
        .thumbnail {
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

prompt = """You are YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1].split("&")[0]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# App Layout
st.header("🎥 YouTube Video to Smart Notes Converter", divider="rainbow")
st.markdown("""
    Transform YouTube videos into concise, organized notes with AI-powered summarization. 
    Simply paste any YouTube video link below and get instant structured notes!
""")

with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        youtube_link = st.text_input(" ", placeholder="Paste YouTube URL here...")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        process_clicked = st.button("✨ Generate Smart Notes")

if youtube_link:
    try:
        video_id = youtube_link.split("v=")[1].split("&")[0]
        print(video_id)
        with st.container():
            st.markdown("### Video Preview")
            col1, col2, col3 = st.columns([1, 6, 1])
            with col2:
                st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", 
                        use_container_width=True, 
                        caption="Video Thumbnail",
                        output_format="JPEG",
                        clamp=True,
                        channels="RGB")
    except:
        st.error("⚠️ Please enter a valid YouTube URL")

if process_clicked and youtube_link:
    with st.spinner("🔍 Analyzing video content..."):
        try:
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                with st.spinner("📝 Generating smart notes..."):
                    summary = generate_gemini_content(transcript_text, prompt)
                
                st.success("✅ Notes generated successfully!")
                with st.container():
                    st.markdown("### 📋 Structured Notes")
                    with st.expander("View Detailed Notes", expanded=True):
                        st.markdown(f"""
                            <div class="summary-box">
                                {escape(summary.replace("•", "•"))}
                            </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error processing video: {str(e)}")
