// State management
const state = {
    videoId: null,
    videoTitle: null,
    transcript: null,
    summary: null,
    chunks: null,
    vectorizer: null,
    matrix: null
};

// API base URL - adjust if needed
const API_BASE_URL = 'http://localhost:5000/api';

// DOM elements
const elements = {
    youtubeUrl: document.getElementById('youtube-url'),
    generateBtn: document.getElementById('generate-btn'),
    summaryInstructions: document.getElementById('summary-instructions'),
    audioFallback: document.getElementById('audio-fallback'),
    errorMessage: document.getElementById('error-message'),
    successMessage: document.getElementById('success-message'),
    warningMessage: document.getElementById('warning-message'),
    loadingSpinner: document.getElementById('loading-spinner'),
    loadingText: document.getElementById('loading-text'),
    videoInfo: document.getElementById('video-info'),
    videoThumbnail: document.getElementById('video-thumbnail'),
    summarySection: document.getElementById('summary-section'),
    summaryContent: document.getElementById('summary-content'),
    downloadSummaryBtn: document.getElementById('download-summary-btn'),
    copySummaryBtn: document.getElementById('copy-summary-btn'),
    downloadTranscriptBtn: document.getElementById('download-transcript-btn'),
    copyTranscriptBtn: document.getElementById('copy-transcript-btn'),
    qaSection: document.getElementById('qa-section'),
    questionInput: document.getElementById('question-input'),
    askBtn: document.getElementById('ask-btn'),
    answerContainer: document.getElementById('answer-container'),
    chunksExpander: document.getElementById('chunks-expander'),
    toggleChunksBtn: document.getElementById('toggle-chunks-btn'),
    chunksContent: document.getElementById('chunks-content'),
    transcriptSection: document.getElementById('transcript-section'),
    toggleTranscriptBtn: document.getElementById('toggle-transcript-btn'),
    transcriptContent: document.getElementById('transcript-content'),
    transcriptTextarea: document.getElementById('transcript-textarea')
};

// Utility functions
function showMessage(element, message, type = 'error') {
    element.textContent = message;
    element.style.display = 'block';
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

function showLoading(text) {
    elements.loadingText.textContent = text;
    elements.loadingSpinner.style.display = 'flex';
}

function hideLoading() {
    elements.loadingSpinner.style.display = 'none';
}

function hideAllMessages() {
    elements.errorMessage.style.display = 'none';
    elements.successMessage.style.display = 'none';
    elements.warningMessage.style.display = 'none';
}

// API calls
async function processVideo() {
    const url = elements.youtubeUrl.value.trim();
    if (!url) {
        showMessage(elements.errorMessage, 'Please enter a YouTube URL.');
        return;
    }

    hideAllMessages();
    showLoading('📜 Fetching transcript/captions...');
    elements.generateBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                youtube_url: url,
                summary_instructions: elements.summaryInstructions.value,
                enable_audio_fallback: elements.audioFallback.checked
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to process video');
        }

        // Update state
        state.videoId = data.video_id;
        state.videoTitle = data.video_title;
        state.transcript = data.transcript;
        state.summary = data.summary;
        state.chunks = data.chunks;
        state.vectorizer = data.vectorizer;
        state.matrix = data.matrix;

        // Update UI
        updateVideoInfo();
        updateSummarySection();
        updateQASection();
        updateTranscriptSection();

        // Smooth scroll to summary
        setTimeout(() => {
            elements.summarySection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);

        showMessage(elements.successMessage, '✓ Video processed successfully!', 'success');

    } catch (error) {
        console.error('Error processing video:', error);
        showMessage(elements.errorMessage, error.message || 'Failed to process video. Please try again.');
    } finally {
        hideLoading();
        elements.generateBtn.disabled = false;
    }
}

async function askQuestion() {
    const question = elements.questionInput.value.trim();
    if (!question) {
        showMessage(elements.errorMessage, 'Please enter a question.');
        return;
    }

    if (!state.chunks || !state.vectorizer || !state.matrix) {
        showMessage(elements.errorMessage, 'Please process a video first.');
        return;
    }

    hideAllMessages();
    showLoading('🔎 Retrieving relevant parts of transcript...');
    elements.askBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                video_id: state.videoId,
                chunks: state.chunks,
                vectorizer: state.vectorizer,
                matrix: state.matrix
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to get answer');
        }

        // Display answer
        elements.answerContainer.innerHTML = formatMarkdown(data.answer);
        elements.answerContainer.style.display = 'block';
        
        // Smooth scroll to answer
        elements.answerContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Display chunks if available
        if (data.chunks && data.chunks.length > 0) {
            displayChunks(data.chunks);
            elements.chunksExpander.style.display = 'block';
        } else {
            showMessage(elements.warningMessage, 'I couldn\'t find relevant transcript evidence for that question.');
        }

    } catch (error) {
        console.error('Error asking question:', error);
        showMessage(elements.errorMessage, error.message || 'Failed to get answer. Please try again.');
    } finally {
        hideLoading();
        elements.askBtn.disabled = false;
    }
}

// UI update functions
function updateVideoInfo() {
    if (!state.videoId) return;

    elements.videoThumbnail.src = `https://img.youtube.com/vi/${state.videoId}/maxresdefault.jpg`;
    elements.videoThumbnail.onerror = function() {
        this.src = `https://img.youtube.com/vi/${state.videoId}/hqdefault.jpg`;
    };
    elements.videoInfo.style.display = 'block';
}

function updateSummarySection() {
    if (!state.summary) return;

    elements.summaryContent.innerHTML = formatMarkdown(state.summary);
    elements.summarySection.style.display = 'block';
    elements.summarySection.style.opacity = '1';
    elements.summarySection.style.transform = 'translateY(0)';
}

function updateQASection() {
    if (!state.transcript) return;

    elements.qaSection.style.display = 'block';
    elements.qaSection.style.opacity = '1';
    elements.qaSection.style.transform = 'translateY(0)';
}

function updateTranscriptSection() {
    if (!state.transcript) return;

    elements.transcriptTextarea.value = state.transcript;
    elements.transcriptSection.style.display = 'block';
    elements.transcriptSection.style.opacity = '1';
    elements.transcriptSection.style.transform = 'translateY(0)';
}

function displayChunks(chunks) {
    elements.chunksContent.innerHTML = '';
    chunks.forEach(chunk => {
        const chunkDiv = document.createElement('div');
        chunkDiv.className = 'chunk-item';
        chunkDiv.innerHTML = `
            <h3>Chunk ${chunk.idx}</h3>
            <p>${escapeHtml(chunk.text)}</p>
        `;
        elements.chunksContent.appendChild(chunkDiv);
    });
}

// Download functions
function downloadSummary() {
    if (!state.summary) return;

    const blob = new Blob([state.summary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${state.videoId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function downloadTranscript() {
    if (!state.transcript) return;

    const blob = new Blob([state.transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${state.videoId}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function copyToClipboard(text, successMessage) {
    navigator.clipboard.writeText(text).then(() => {
        showMessage(elements.successMessage, successMessage, 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showMessage(elements.errorMessage, 'Failed to copy to clipboard');
    });
}

function copySummary() {
    if (!state.summary) return;
    copyToClipboard(state.summary, '✓ Summary copied to clipboard!');
}

function copyTranscript() {
    if (!state.transcript) return;
    copyToClipboard(state.transcript, '✓ Transcript copied to clipboard!');
}

// Utility: Simple markdown to HTML converter
function formatMarkdown(text) {
    if (!text) return '';
    
    // Convert markdown-style formatting to HTML
    let html = escapeHtml(text);
    
    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Line breaks
    html = html.replace(/\n/g, '<br>');
    
    // Wrap in paragraphs
    const paragraphs = html.split('<br><br>');
    html = paragraphs.map(p => p.trim() ? `<p>${p}</p>` : '').join('');
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle functions
function toggleChunks() {
    const isVisible = elements.chunksContent.style.display !== 'none';
    elements.chunksContent.style.display = isVisible ? 'none' : 'block';
    elements.toggleChunksBtn.textContent = isVisible 
        ? 'Show retrieved transcript chunks' 
        : 'Hide retrieved transcript chunks';
}

function toggleTranscript() {
    const isVisible = elements.transcriptContent.style.display !== 'none';
    elements.transcriptContent.style.display = isVisible ? 'none' : 'block';
    elements.toggleTranscriptBtn.textContent = isVisible 
        ? '📜 View full transcript' 
        : '📜 Hide full transcript';
}

// Event listeners
elements.generateBtn.addEventListener('click', processVideo);
elements.youtubeUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        processVideo();
    }
});

elements.askBtn.addEventListener('click', askQuestion);
elements.questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        askQuestion();
    }
});

elements.downloadSummaryBtn.addEventListener('click', downloadSummary);
elements.copySummaryBtn.addEventListener('click', copySummary);
elements.downloadTranscriptBtn.addEventListener('click', downloadTranscript);
elements.copyTranscriptBtn.addEventListener('click', copyTranscript);
elements.toggleChunksBtn.addEventListener('click', toggleChunks);
elements.toggleTranscriptBtn.addEventListener('click', toggleTranscript);

// Add smooth transitions when sections appear
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe sections for animation
document.addEventListener('DOMContentLoaded', () => {
    const sections = document.querySelectorAll('.summary-section, .qa-section, .transcript-section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        observer.observe(section);
    });
});
