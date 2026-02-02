import os
import re
import tempfile
import json
import pickle
import base64
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from dotenv import load_dotenv
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Missing GROQ_API_KEY. Create a .env file with GROQ_API_KEY=...")

client = Groq(api_key=GROQ_API_KEY)

# Models / limits
WHISPER_MODEL = "whisper-large-v3"
SUMMARY_MODEL = "llama-3.3-70b-versatile"
QA_MODEL = "llama-3.3-70b-versatile"
MAX_AUDIO_SIZE_MB = 25  # Groq Whisper API limit


@dataclass
class TranscriptChunk:
    idx: int
    text: str


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from common YouTube URL forms."""
    if not url:
        return None
    url = url.strip()
    patterns = [
        r"(?:youtube\.com\/watch\?v=)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com\/shorts\/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com\/embed\/)([0-9A-Za-z_-]{11})",
        r"(?:youtube\.com\/live\/)([0-9A-Za-z_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    # fallback: first 11-char candidate after v= or /
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\b|&|\?)", url)
    return m.group(1) if m else None


def fetch_transcript_from_youtube(video_id: str) -> str:
    """Fetch transcript/captions via YouTubeTranscriptApi if available."""
    # Try old API first (if available)
    if hasattr(YouTubeTranscriptApi, "get_transcript"):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return TextFormatter().format_transcript(transcript)
        except Exception:
            pass  # Fall through to new API

    api = YouTubeTranscriptApi()
    
    # Try list_transcripts approach (most reliable for v1.x)
    if hasattr(api, "list_transcripts"):
        try:
            transcripts = api.list_transcripts(video_id)
            try:
                t = transcripts.find_transcript(["en"])
            except Exception:
                # fall back to generated transcript
                t = transcripts.find_generated_transcript(["en"])
            fetched = t.fetch()
            
            # Check if fetched has .text property (direct access)
            if hasattr(fetched, "text") and isinstance(fetched.text, str):
                return fetched.text
            
            # Otherwise try to_raw_data()
            if hasattr(fetched, "to_raw_data"):
                raw = fetched.to_raw_data()
                if isinstance(raw, list) and len(raw) > 0:
                    if isinstance(raw[0], dict):
                        text_parts = [item.get("text", "") if isinstance(item, dict) else str(item) for item in raw]
                        return " ".join(text_parts)
                    elif hasattr(raw[0], "text"):
                        text_parts = [getattr(item, "text", "") for item in raw]
                        return " ".join(text_parts)
            
            # Last resort: try to format as transcript list
            if hasattr(fetched, "to_dict"):
                transcript_list = fetched.to_dict()
                if isinstance(transcript_list, list):
                    return TextFormatter().format_transcript(transcript_list)
        except Exception as e:
            pass  # Fall through to direct fetch
    
    # Try direct fetch() method
    if hasattr(api, "fetch"):
        try:
            fetched = api.fetch(video_id)
            
            if hasattr(fetched, "text") and isinstance(fetched.text, str):
                return fetched.text
            
            if hasattr(fetched, "to_raw_data"):
                raw = fetched.to_raw_data()
                if isinstance(raw, list) and len(raw) > 0:
                    if isinstance(raw[0], dict):
                        text_parts = [item.get("text", "") if isinstance(item, dict) else str(item) for item in raw]
                        return " ".join(text_parts)
                    elif hasattr(raw[0], "text"):
                        text_parts = [getattr(item, "text", "") for item in raw]
                        return " ".join(text_parts)
        except Exception:
            pass

    raise Exception("Unsupported youtube-transcript-api version: could not fetch transcript.")


def download_audio(video_url: str, output_path_no_ext: str) -> Tuple[str, str]:
    """Download audio from YouTube video to mp3. Requires ffmpeg installed on the machine."""
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": output_path_no_ext,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        audio_file = output_path_no_ext + ".mp3"
        return audio_file, info.get("title", "Unknown")


def transcribe_audio(audio_file: str) -> str:
    """Transcribe audio using Groq Whisper API."""
    file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
    if file_size_mb > MAX_AUDIO_SIZE_MB:
        raise Exception(
            f"Audio file too large ({file_size_mb:.1f}MB). Maximum is {MAX_AUDIO_SIZE_MB}MB. "
            "Try a shorter video or use a video with captions."
        )
    with open(audio_file, "rb") as f:
        return client.audio.transcriptions.create(
            file=(os.path.basename(audio_file), f.read()),
            model=WHISPER_MODEL,
            response_format="text",
        )


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[TranscriptChunk]:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return []
    chunks: List[TranscriptChunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(TranscriptChunk(idx=idx, text=chunk))
            idx += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def build_retriever(chunks: List[TranscriptChunk]) -> Tuple[TfidfVectorizer, object]:
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=60000)
    matrix = vectorizer.fit_transform([c.text for c in chunks])
    return vectorizer, matrix


def retrieve_top_chunks(
    query: str, chunks: List[TranscriptChunk], vectorizer: TfidfVectorizer, matrix, top_k: int = 5
) -> List[TranscriptChunk]:
    if not query.strip() or not chunks:
        return []
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, matrix)[0]
    top_idx = sims.argsort()[::-1][:top_k]
    return [chunks[i] for i in top_idx]


def generate_summary(transcript: str, user_instruction: str) -> str:
    prompt = f"""You are an expert content summarizer.

Your task:
- Read the YouTube video transcript below
- Give it a Title
- Generate a concise, well-structured summary
- Highlight key ideas and important points
- Do NOT add information not present in the transcript

Additional instruction from user:
{user_instruction}

Transcript:
{transcript}
"""
    response = client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[
            {"role": "system", "content": "You create clear, concise, accurate summaries grounded in the provided transcript."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1500,
    )
    return response.choices[0].message.content


def answer_question(question: str, context_chunks: List[TranscriptChunk]) -> str:
    context = "\n\n".join([f"[Chunk {c.idx}] {c.text}" for c in context_chunks])[:12000]
    prompt = f"""Answer the question using ONLY the transcript context.
If the answer is not in the context, say you don't know based on the transcript.
Output ONLY the answer (no preamble). If you cite, do it inline at the end like: (chunks: 2, 5).

Question:
{question}

Transcript context:
{context}
"""
    response = client.chat.completions.create(
        model=QA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer strictly from the provided context. Return ONLY the answer text with no preamble.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=900,
    )
    return response.choices[0].message.content


def serialize_vectorizer(vectorizer):
    """Serialize TfidfVectorizer to base64 string."""
    pickled = pickle.dumps(vectorizer)
    return base64.b64encode(pickled).decode('utf-8')


def deserialize_vectorizer(serialized):
    """Deserialize TfidfVectorizer from base64 string."""
    pickled = base64.b64decode(serialized.encode('utf-8'))
    return pickle.loads(pickled)


def serialize_matrix(matrix):
    """Serialize sparse matrix to base64 string."""
    pickled = pickle.dumps(matrix)
    return base64.b64encode(pickled).decode('utf-8')


def deserialize_matrix(serialized):
    """Deserialize sparse matrix from base64 string."""
    pickled = base64.b64decode(serialized.encode('utf-8'))
    return pickle.loads(pickled)


@app.route('/api/process', methods=['POST'])
def process_video():
    try:
        data = request.json
        youtube_url = data.get('youtube_url')
        summary_instructions = data.get('summary_instructions', 'Create a detailed summary with key takeaways and main points.')
        enable_audio_fallback = data.get('enable_audio_fallback', False)

        if not youtube_url:
            return jsonify({'error': 'Please enter a YouTube URL.'}), 400

        video_id = extract_video_id(youtube_url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL (could not extract video id).'}), 400

        # Try transcript first
        transcript: Optional[str] = None
        try:
            transcript = fetch_transcript_from_youtube(video_id)
        except Exception as e:
            if not enable_audio_fallback:
                return jsonify({'error': f'Could not fetch captions transcript. ({str(e)})'}), 400

        video_title = "Unknown"
        temp_dir = None
        audio_file = None

        # Optional fallback: audio → whisper
        if (not transcript or not transcript.strip()) and enable_audio_fallback:
            temp_dir = tempfile.mkdtemp()
            audio_path_no_ext = os.path.join(temp_dir, f"audio_{video_id}")
            try:
                audio_file, video_title = download_audio(youtube_url, audio_path_no_ext)
                transcript = transcribe_audio(audio_file)
            except Exception as e:
                return jsonify({'error': f'Audio transcription failed: {str(e)}'}), 400
            finally:
                try:
                    if audio_file and os.path.exists(audio_file):
                        os.remove(audio_file)
                    if temp_dir and os.path.isdir(temp_dir):
                        os.rmdir(temp_dir)
                except Exception:
                    pass

        if not transcript or not transcript.strip():
            return jsonify({'error': 'No transcript available. Try enabling the audio transcription fallback or use a video with captions.'}), 400

        # Generate summary
        summary = generate_summary(transcript, summary_instructions)

        # Chunk and build retriever
        chunks = chunk_text(transcript)
        vectorizer, matrix = build_retriever(chunks)

        # Serialize for JSON response
        chunks_dict = [asdict(c) for c in chunks]
        vectorizer_serialized = serialize_vectorizer(vectorizer)
        matrix_serialized = serialize_matrix(matrix)

        return jsonify({
            'video_id': video_id,
            'video_title': video_title,
            'transcript': transcript,
            'summary': summary,
            'chunks': chunks_dict,
            'vectorizer': vectorizer_serialized,
            'matrix': matrix_serialized
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question')
        chunks_data = data.get('chunks')
        vectorizer_serialized = data.get('vectorizer')
        matrix_serialized = data.get('matrix')

        if not question or not question.strip():
            return jsonify({'error': 'Please enter a question.'}), 400

        if not chunks_data or not vectorizer_serialized or not matrix_serialized:
            return jsonify({'error': 'Missing required data. Please process a video first.'}), 400

        # Deserialize
        chunks = [TranscriptChunk(**c) for c in chunks_data]
        vectorizer = deserialize_vectorizer(vectorizer_serialized)
        matrix = deserialize_matrix(matrix_serialized)

        # Retrieve top chunks
        top_chunks = retrieve_top_chunks(question, chunks, vectorizer, matrix, top_k=5)

        if not top_chunks:
            return jsonify({'error': 'I couldn\'t find relevant transcript evidence for that question.'}), 400

        # Generate answer
        answer = answer_question(question, top_chunks)

        return jsonify({
            'answer': answer,
            'chunks': [asdict(c) for c in top_chunks]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
