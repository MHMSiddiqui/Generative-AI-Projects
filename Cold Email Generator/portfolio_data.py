"""
create_portfolio.py
Script to create the portfolio CSV file
Run this before using portfolio.py
"""

import pandas as pd
import os

def create_portfolio_csv():
    """Create portfolio CSV file with sample data"""
    
    # Create the portfolio data
    portfolio_data = {
        'Techstack': [
            'React, Node.js, MongoDB',
            'Python, Machine Learning, TensorFlow',
            'Java, Spring Boot, MySQL',
            'Angular, TypeScript, PostgreSQL',
            'Vue.js, Express.js, Redis',
            'Django, Python, PostgreSQL',
            'React Native, Firebase, GraphQL',
            'Flutter, Dart, SQLite',
            'PHP, Laravel, MySQL',
            'Ruby on Rails, PostgreSQL',
            'ASP.NET Core, C#, SQL Server',
            'Go, Microservices, Docker',
            'Kotlin, Android, Room',
            'Swift, iOS, CoreData',
            'JavaScript, AWS Lambda, DynamoDB',
            'Python, FastAPI, MongoDB',
            'Scala, Apache Spark, Hadoop',
            'Rust, WebAssembly, PostgreSQL',
            'Elixir, Phoenix, PostgreSQL',
            'C++, Qt, SQLite'
        ],
        'Links': [
            'https://example.com/react-portfolio',
            'https://example.com/ml-portfolio',
            'https://example.com/java-portfolio',
            'https://example.com/angular-portfolio',
            'https://example.com/vue-portfolio',
            'https://example.com/django-portfolio',
            'https://example.com/react-native-portfolio',
            'https://example.com/flutter-portfolio',
            'https://example.com/php-portfolio',
            'https://example.com/rails-portfolio',
            'https://example.com/dotnet-portfolio',
            'https://example.com/go-portfolio',
            'https://example.com/kotlin-portfolio',
            'https://example.com/swift-portfolio',
            'https://example.com/serverless-portfolio',
            'https://example.com/fastapi-portfolio',
            'https://example.com/spark-portfolio',
            'https://example.com/rust-portfolio',
            'https://example.com/elixir-portfolio',
            'https://example.com/cpp-portfolio'
        ]
    }
    
    # Create DataFrame
    portfolio_df = pd.DataFrame(portfolio_data)
    
    # Create directory if it doesn't exist
    os.makedirs('app/resource', exist_ok=True)
    
    # Save to CSV
    csv_path = 'app/resource/my_portfolio.csv'
    portfolio_df.to_csv(csv_path, index=False)
    
    print("✓ Portfolio CSV created successfully!")
    print(f"✓ Location: {csv_path}")
    print(f"✓ Total entries: {len(portfolio_df)}")
    print("\nFirst few entries:")
    print(portfolio_df.head())
    
    return csv_path


if __name__ == "__main__":
    create_portfolio_csv()