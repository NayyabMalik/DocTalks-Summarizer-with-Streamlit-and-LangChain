import streamlit as st
import tempfile
import os
import pytube
import fitz  # PyMuPDF for PDF text extraction
import speech_recognition as sr
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import yt_dlp
from pydub import AudioSegment
import re
import unicodedata

# --------------------------
# SETUP MODEL
# --------------------------
try:
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    )
    chat_model = ChatHuggingFace(llm=llm)
except Exception as e:
    st.error(f"Error initializing model: {str(e)}")
    st.stop()

# --------------------------
# FUNCTIONS
# --------------------------
def sanitize_filename(filename):
    """Remove or replace invalid characters in file names for Windows compatibility."""
    # Normalize Unicode characters to their closest ASCII equivalents
    filename = unicodedata.normalize('NFKC', filename)
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'  # Extended to include control characters
    sanitized = re.sub(invalid_chars, '_', filename)
    # Replace additional problematic characters (e.g., full-width colon, vertical bar)
    sanitized = sanitized.replace('：', '_').replace('｜', '_')
    # Remove leading/trailing spaces and periods
    sanitized = sanitized.strip().strip('.')
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "default_filename"
    return sanitized

def extract_pdf_text(uploaded_pdf):
    text = ""
    with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def transcribe_with_google(file_path):
    recognizer = sr.Recognizer()

    # Convert everything to WAV using pydub
    wav_path = file_path + ".wav"
    sound = AudioSegment.from_file(file_path)
    sound.export(wav_path, format="wav")

    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = "Google Speech Recognition could not understand the audio."
        except sr.RequestError:
            text = "Could not request results from Google Speech Recognition service."
    # Clean up the WAV file
    if os.path.exists(wav_path):
        os.remove(wav_path)
    return text

def download_youtube_audio(youtube_url, output_path="downloads"):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Extract info first (without download) to get the title
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        original_title = info['title']
        sanitized_title = sanitize_filename(original_title)

    # Now use sanitized title directly in outtmpl
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_path, f"{sanitized_title}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    sanitized_file_path = os.path.join(output_path, f"{sanitized_title}.mp3")

    if not os.path.exists(sanitized_file_path):
        raise FileNotFoundError(f"Expected file not found: {sanitized_file_path}")

    return sanitized_file_path


# --------------------------
# STREAMLIT UI
# --------------------------
st.title("Summarizer (PDF / YouTube / Audio)")

input_type = st.radio(
    "Choose Input Type",
    ["YouTube Link", "Upload Video/Audio", "Upload PDF"]
)

raw_text = ""

if input_type == "YouTube Link":
    youtube_url = st.text_input("Enter YouTube URL")
    if youtube_url and st.button("Process YouTube"):
        with st.spinner("Downloading & transcribing YouTube audio..."):
            try:
                audio_file = download_youtube_audio(youtube_url)
                raw_text = transcribe_with_google(audio_file)
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except Exception as e:
                st.error(f"Error processing YouTube audio: {str(e)}")

elif input_type == "Upload Video/Audio":
    uploaded_file = st.file_uploader("Upload Video/Audio", type=["mp3", "wav", "mp4", "m4a"])
    if uploaded_file and st.button("Process Audio/Video"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        with st.spinner("Transcribing uploaded file..."):
            try:
                raw_text = transcribe_with_google(tmp_path)
            except Exception as e:
                st.error(f"Error transcribing file: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

elif input_type == "Upload PDF":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf and st.button("Process PDF"):
        with st.spinner("Extracting text from PDF..."):
            try:
                raw_text = extract_pdf_text(uploaded_pdf)
            except Exception as e:
                st.error(f"Error extracting PDF text: {str(e)}")

# --------------------------
# GENERATE SUMMARY
# --------------------------
if raw_text:
    st.subheader("Extracted Content")
    st.text_area("Preview", raw_text[:1500] + "..." if len(raw_text) > 1500 else raw_text, height=200)

    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            try:
                prompt = PromptTemplate.from_template(
                    "Summarize the following content in a clear, concise way:\n\n{content}\n\nSummary:"
                )
                chain = prompt | chat_model
                result = chain.invoke({"content": raw_text})
                st.subheader("Summary")
                st.write(result.content)
            except Exception as e:
                st.error(f"Error generating summary: {str(e)}")