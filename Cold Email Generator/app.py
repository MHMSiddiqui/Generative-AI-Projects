"""
app.py
Flask application for Cold Email Generator
Run with: python app.py
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize components
try:
    chain = Chain()
    portfolio = Portfolio()
    portfolio.load_portfolio()
    print("✓ Application initialized successfully")
except Exception as e:
    print(f"✗ Initialization Error: {e}")
    chain = None
    portfolio = None


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/api/generate-emails', methods=['POST'])
def generate_emails():
    """
    API endpoint to process URL and generate cold emails for job postings
    
    Expected JSON body:
        {
            "url": "https://example.com/careers"
        }
    
    Returns:
        JSON response with jobs and emails or error message
    """
    try:
        # Check if components are initialized
        if not chain or not portfolio:
            return jsonify({
                'error': 'Application not properly initialized. Check GROQ_API_KEY.'
            }), 500
        
        # Get URL from request
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Load the webpage
        print(f"Loading URL: {url}")
        loader = WebBaseLoader([url])
        page_content = loader.load().pop().page_content
        
        # Clean the text
        cleaned_data = clean_text(page_content)
        print(f"Cleaned data length: {len(cleaned_data)} characters")
        
        # Extract jobs
        print("Extracting jobs...")
        jobs = chain.extract_jobs(cleaned_data)
        
        if not jobs:
            return jsonify({
                'error': 'No job postings found on this page',
                'jobs': []
            }), 404
        
        print(f"Found {len(jobs)} job(s)")
        
        # Generate emails for each job
        results = []
        for idx, job in enumerate(jobs, 1):
            print(f"Generating email for job {idx}: {job.get('role', 'Unknown')}")
            
            # Get relevant portfolio links
            skills = job.get('skills', [])
            links = portfolio.query_links(skills)
            
            # Generate email
            email = chain.write_mail(job, links)
            
            # Add email to job data
            job['email'] = email
            results.append(job)
        
        print("✓ All emails generated successfully")
        
        return jsonify({
            'success': True,
            'jobs': results
        }), 200
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'chain_initialized': chain is not None,
        'portfolio_initialized': portfolio is not None
    }), 200


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Cold Email Generator - Flask Backend")
    print("="*50)
    print(f"✓ Server starting...")
    print(f"✓ Access the application at: http://localhost:5000")
    print(f"✓ API endpoint: http://localhost:5000/api/generate-emails")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)