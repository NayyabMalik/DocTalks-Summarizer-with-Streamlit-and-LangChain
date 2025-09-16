# DocTalks-Summarizer (PDF / YouTube / Audio/Video)

A Streamlit-based web application that extracts text from PDFs, transcribes audio from YouTube videos or uploaded audio/video files, and generates concise summaries using a HuggingFace language model.

## Features
- **YouTube Audio Transcription**: Download audio from a YouTube video, transcribe it using Google Speech Recognition, and summarize the content.
- **Audio/Video Upload**: Upload audio or video files (e.g., MP3, WAV, MP4, M4A) for transcription and summarization.
- **PDF Text Extraction**: Extract text from uploaded PDF files and generate summaries.
- **Summarization**: Uses a HuggingFace language model (MistralAI Mixtral-8x7B) to generate clear and concise summaries of extracted or transcribed text.

## Installation

### Prerequisites
- Python 3.12
- FFmpeg installed and added to system PATH (required for audio processing)
- A HuggingFace API token for accessing the language model


## Usage
1. Open the application in your browser (typically at `http://localhost:8501`).
2. Choose an input type:
   - **YouTube Link**: Enter a YouTube URL to download, transcribe, and summarize the audio.
   - **Upload Video/Audio**: Upload an audio or video file (MP3, WAV, MP4, M4A) for transcription and summarization.
   - **Upload PDF**: Upload a PDF file to extract text and generate a summary.
3. Click the appropriate "Process" button to extract or transcribe text.
4. View the extracted/transcribed text and click "Generate Summary" to produce a concise summary.

## Project Structure
```
NayyabMalik/Summarizer-PDF-YouTube-Audio
├── summarizer.py       # Main Streamlit application script
├── downloads/          # Temporary directory for downloaded YouTube audio (auto-created)
├── README.md           # This file
└── requirements.txt    # List of Python dependencies
```

## Dependencies
- `streamlit`: For the web interface
- `pytube`: For YouTube video handling (optional, used in earlier versions)
- `PyMuPDF`: For PDF text extraction
- `speechrecognition`: For audio transcription using Google Speech Recognition
- `langchain-huggingface`: For integrating HuggingFace language models
- `yt-dlp`: For downloading YouTube audio
- `pydub`: For audio file processing
- `ffmpeg`: For audio conversion (required by `pydub` and `yt-dlp`)

## Notes
- **File Name Handling**: The application sanitizes file names to ensure compatibility with Windows by replacing invalid characters (e.g., `|`, `:`) with underscores.
- **Temporary Files**: Downloaded audio files and temporary WAV files are automatically deleted after processing.
- **Error Handling**: The app includes error handling for failed downloads, transcriptions, or summarizations, with user-friendly error messages displayed in the UI.
- **Performance**: Processing large YouTube videos or audio files may take time due to downloading and transcription. Ensure a stable internet connection for YouTube downloads.

## Troubleshooting
- **FileNotFoundError**: If you encounter errors related to file paths, ensure the `downloads` directory is writable and check for special characters in YouTube video titles.
- **FFmpeg Errors**: Ensure FFmpeg is installed and accessible in your system PATH.
- **HuggingFace API Issues**: Verify your API token is correctly set and that you have an active internet connection.
- **Transcription Errors**: Google Speech Recognition may fail for unclear audio or require an internet connection.

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for the web interface.
- Powered by [HuggingFace](https://huggingface.co/) for language model integration.
- Uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube audio downloading.
- Audio processing with [pydub](https://github.com/jiaaro/pydub) and [FFmpeg](https://ffmpeg.org/).
