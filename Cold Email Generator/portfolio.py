"""
portfolio.py
Portfolio management system using ChromaDB for vector search
"""

import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        """
        Initialize Portfolio with CSV file path and ChromaDB client
        
        Args:
            file_path (str): Path to portfolio CSV file
        """
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        """Load portfolio data into ChromaDB vector store"""
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )
            print(f"✓ Loaded {len(self.data)} portfolio items into vector store")
        else:
            print(f"✓ Portfolio already loaded ({self.collection.count()} items)")

    def query_links(self, skills):
        """
        Query relevant portfolio links based on skills
        
        Args:
            skills (list): List of skills to match
            
        Returns:
            list: List of metadata dictionaries containing matching links
        """
        return self.collection.query(query_texts=skills, n_results=2).get('metadatas', [])


if __name__ == "__main__":
    # Test the Portfolio class
    print("Testing Portfolio class...")
    
    try:
        portfolio = Portfolio()
        portfolio.load_portfolio()
        
        # Test query
        test_skills = ["Python", "Machine Learning", "React"]
        results = portfolio.query_links(test_skills)
        
        print("\nTest Query Results:")
        print(f"Skills: {test_skills}")
        print(f"Matching portfolios: {results}")
        
    except FileNotFoundError:
        print("❌ Error: Portfolio CSV file not found!")
        print("Please run 'create_portfolio.py' first to create the portfolio file.")