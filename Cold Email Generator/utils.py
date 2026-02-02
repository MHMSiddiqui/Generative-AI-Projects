"""
utils.py
Text cleaning and preprocessing utilities
"""

import re

def clean_text(text):
    """
    Clean and normalize text by removing HTML, URLs, and special characters
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned and normalized text
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    
    # Remove URLs
    text = re.sub(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
        '', 
        text
    )
    
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Trim leading and trailing whitespace
    text = text.strip()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


if __name__ == "__main__":
    # Test the function
    sample_text = """
    <html><body>
    <h1>Sample Job Posting</h1>
    <p>We are looking for a Python developer with 3+ years of experience.</p>
    <a href="https://example.com/apply">Apply Now</a>
    </body></html>
    """
    
    cleaned = clean_text(sample_text)
    print("Original text:")
    print(sample_text)
    print("\nCleaned text:")
    print(cleaned)