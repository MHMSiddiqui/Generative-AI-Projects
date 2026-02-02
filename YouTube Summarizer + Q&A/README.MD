
# 🎬 YouTube Summarizer & RAG Q&A

A powerful, lightweight web application that generates detailed summaries of YouTube videos and allows users to ask questions about the video content. Powered by **Groq** (Llama 3.3 & Whisper), **Flask**, and **Scikit-Learn** for local Retrieval-Augmented Generation (RAG).

## ✨ Key Features

* **Smart Summarization**: Generates concise, structured summaries using Llama 3.3 (via Groq).
* **Interactive Q&A**: Chat with the video! Ask specific questions and get answers based strictly on the transcript context.
* **Dual Transcript Strategy**:
    1.  **API Fetch**: Fast retrieval of existing captions/transcripts.
    2.  **Audio Fallback**: Downloads audio and transcribes it using **Whisper Large V3** if no captions exist.
* **Lightweight RAG**: Uses TF-IDF vectorization and Cosine Similarity for fast, local context retrieval without heavy vector databases.
* **Modern UI**: Responsive Dark Mode interface built with vanilla HTML/JS/CSS.
* **Export Options**: Download raw transcripts or generated summaries as text files.

## 🛠️ Tech Stack

* **Backend**: Flask, yt-dlp, YouTube Transcript API.
* **AI/Inference**: Groq API (Llama-3.3-70b-versatile, Whisper-large-v3).
* **Vector Search**: Scikit-Learn (TF-IDF, Cosine Similarity).
* **Frontend**: Vanilla JavaScript, HTML5, CSS3.
* **Containerization**: Docker.

---

## 🚀 Getting Started

### Prerequisites

* **Python 3.11+**
* **FFmpeg** (Required for audio processing/transcription fallback)
* **Groq API Key** (Get one at [console.groq.com](https://console.groq.com))

### Option A: Local Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/youtube-summarizer.git](https://github.com/yourusername/youtube-summarizer.git)
    cd youtube-summarizer
    ```

2.  **Set up a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg**
    * **Ubuntu/Debian**: `sudo apt install ffmpeg`
    * **macOS**: `brew install ffmpeg`
    * **Windows**: Download binaries and add to PATH.

5.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

6.  **Run the Application**
    ```bash
    python app.py
    ```
    Access the app at `http://localhost:5000`.

### Option B: Docker Deployment

1.  **Build the Image**
    ```bash
    docker build -t youtube-summarizer .
    ```

2.  **Run the Container**
    ```bash
    docker run -p 5000:5000 -e GROQ_API_KEY=your_api_key_here youtube-summarizer
    ```

---

## 📖 Usage Guide

1.  **Input URL**: Paste a standard YouTube link (e.g., `https://www.youtube.com/watch?v=...`).
2.  **Configuration**:
    * Add optional custom instructions (e.g., "Focus on technical details").
    * Check "Enable audio transcription fallback" if the video has no captions.
3.  **Generate**: Click the **🚀 Generate** button.
4.  **Review**: Read the generated summary.
5.  **Ask**: Scroll down to the Q&A section to ask specific questions.
6.  **Inspect**: Toggle "View source chunks" to see which parts of the transcript were used for the answer.

## 📂 Project Structure

```text
.
├── app.py                # Main Flask application & RAG logic
├── Dockerfile            # Docker configuration
├── requirements.txt      # Python dependencies
├── index.html            # Frontend structure
├── script.js             # Frontend logic & API calls
└── styles.css            # Dark mode styling

```

## ⚙️ Configuration Details

| Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | **Required.** Your API key for Groq Cloud. |
| `MAX_AUDIO_SIZE_MB` | (In `app.py`) Limit for audio file size sent to Whisper (Default: 25MB). |
| `WHISPER_MODEL` | (In `app.py`) Default: `whisper-large-v3`. |
| `SUMMARY_MODEL` | (In `app.py`) Default: `llama-3.3-70b-versatile`. |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

```

```
