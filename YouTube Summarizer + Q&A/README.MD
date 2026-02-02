## YouTube Summarizer + Q&A (HTML/CSS/JS + Flask + Groq)

Paste a YouTube URL to get:
- **Transcript** (prefers YouTube captions when available)
- **AI summary**
- **Q&A** grounded in the transcript (retrieval + LLM answer)

This repo includes a modern **HTML/CSS/JavaScript** frontend and a **Flask** backend API that runs the Python logic.

### Features
- **Clean interactive UI** (copy/download, smooth transitions)
- **Transcript from captions** via `youtube-transcript-api`
- Optional **audio → Whisper** fallback (requires `ffmpeg`)
- **Local retrieval** (TF‑IDF) + Groq LLM for Q&A

### Project files
- `index.html` / `styles.css` / `script.js`: frontend
- `app.py`: Flask backend API
- `main.py`: original Streamlit version (kept for reference)

## Requirements
- **Python 3.9+** (recommended 3.10/3.11)
- A **Groq API key**

Optional:
- **ffmpeg** (only needed if you enable the audio transcription fallback)

## Quickstart (Windows PowerShell)

### 1) Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2) Set your API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_key_here
```

### 3) Run the backend

```powershell
python app.py
```

Backend will be available at `http://localhost:5000`.

### 4) Run the frontend

Open `index.html` using a simple local server (recommended):

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## API endpoints
- **POST** `/api/process`
  - Body:
    - `youtube_url` (string)
    - `summary_instructions` (string, optional)
    - `enable_audio_fallback` (boolean, optional)
- **POST** `/api/ask`
  - Body:
    - `question` (string)
    - `chunks`, `vectorizer`, `matrix` (returned from `/api/process`)
- **GET** `/api/health`

## Notes / Troubleshooting
- **No captions?** Turn on “audio transcription fallback” (requires **ffmpeg**).
- **Long videos** may fail audio fallback due to the Groq Whisper upload size limit.
- If the frontend can’t reach the API, confirm `app.py` is running on port **5000**.

## License
Add a license if you plan to publish this publicly.

