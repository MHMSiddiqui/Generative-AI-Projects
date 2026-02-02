
# 📧 Cold Email Generator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Jupyter Notebook](https://img.shields.io/badge/Tools-Jupyter%20Notebook-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Complete-success)


A professional AI-powered tool designed for service-based companies to automate their outreach. This application scrapes job postings from company career pages, extracts technical requirements, matches them with your existing portfolio, and generates highly personalized cold emails using **Llama 3.1** and **ChromaDB**.

## ✨ Key Features

* **Automated Web Scraping**: Extracts job details directly from career page URLs using `WebBaseLoader`.
* **Intelligent Job Extraction**: Uses LLMs to parse unstructured website text into structured JSON data (Role, Experience, Skills, and Description).
* **Vector-Based Portfolio Matching**: Utilizes **ChromaDB** to find the most relevant projects from your portfolio based on the required tech stack.
* **Tailored Email Generation**: Crafts professional, value-driven emails that link specific portfolio evidence to the client's needs.
* **Modern Dashboard**: A clean, responsive UI built with Tailwind CSS.

## 🛠️ Tech Stack

* **LLM Framework**: LangChain
* **AI Model**: Groq (Llama 3.1 70B)
* **Vector Database**: ChromaDB
* **Backend**: Flask (Python)
* **Frontend**: HTML5, Tailwind CSS, JavaScript
* **Data Handling**: Pandas

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* A **Groq API Key** (Obtain one at [console.groq.com](https://console.groq.com))

### Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/cold-email-generator.git](https://github.com/yourusername/cold-email-generator.git)
    cd cold-email-generator
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Initialize Portfolio Data**
    Run the data creation script to generate the sample portfolio CSV:
    ```bash
    python portfolio_data.py
    ```

5.  **Run the Application**
    ```bash
    python app.py
    ```
    The application will be available at `http://localhost:5000`.

---

## 📖 Usage Guide

1.  **Enter URL**: Paste the link to a company's career page (e.g., `https://careers.nike.com/jobs`).
2.  **Submit**: Click "Generate Emails".
3.  **Process**: The system will:
    * Scrape the website content.
    * Identify individual job openings.
    * Match your tech stack (from `my_portfolio.csv`) to the job requirements.
    * Generate a custom email for every job found.
4.  **Download**: Copy or download the generated emails to use in your outreach.

## 📂 Project Structure

```text
.
├── app.py              # Flask server and API endpoints
├── chains.py           # LangChain logic for extraction and generation
├── portfolio.py        # ChromaDB logic for vector search & project matching
├── portfolio_data.py   # Script to initialize the portfolio CSV
├── utils.py            # Text cleaning and preprocessing utilities
├── requirements.txt    # Python dependencies
├── index.html          # Tailwind-based frontend
└── app/resource/       # Storage for portfolio CSV

```

## ⚙️ Configuration Details

| Variable | Description |
| --- | --- |
| `GROQ_API_KEY` | **Required.** Your API key for Groq Cloud. |
| `MAX_AUDIO_SIZE_MB` | (In app.py) Limit for audio file size sent to Whisper (Default: 25MB). |
| `WHISPER_MODEL` | (In app.py) Default: whisper-large-v3. |
| `SUMMARY_MODEL` | (In app.py) Default: llama-3.3-70b-versatile. |

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
