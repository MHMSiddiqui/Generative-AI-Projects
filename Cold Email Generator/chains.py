"""
chains.py
LLM chains for job extraction and email generation
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Chain:
    def __init__(self):
        """Initialize the LLM chain with Groq API"""
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found! "
                "Please set it in your .env file or environment variables."
            )
        
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=api_key, 
            model_name="openai/gpt-oss-120b"
        )

    def extract_jobs(self, cleaned_text):
        """
        Extract job postings from scraped website text
        
        Args:
            cleaned_text (str): Cleaned text from career page
            
        Returns:
            list: List of job dictionaries with role, experience, skills, description
        """
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        """
        Generate a cold email based on job description and portfolio links
        
        Args:
            job (dict): Job information dictionary
            links (list): List of relevant portfolio links
            
        Returns:
            str: Generated cold email content
        """
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:

            {job_description}

            ROLE & CONTEXT:

            You are a business development representative at XYZ Company, an AI & Software Consulting firm.

            XYZ Company specializes in automating and integrating business processes through custom-built digital solutions. The company has experience delivering tailored solutions that enable:

            Scalability and growth

            Process optimization

            Cost reduction

            Improved operational efficiency

            TASK:

            Write a professional cold email to a prospective client regarding the job description provided above.

            The email should clearly explain how XYZ Company’s capabilities, technical expertise, and consulting experience align with and address the client’s specific needs outlined in the job description.

            Select and include the most relevant portfolio examples from the following links to demonstrate XYZ Company’s previous work and credibility:
            {link_list}

            REQUIREMENTS:

            Write in the first person plural voice (e.g., “we”, “our team at XYZ Company”)

            Maintain a professional, concise, and value-focused tone

            Highlight solutions and outcomes relevant to the client’s requirements

            Do not include any preamble, explanation, or meta commentary
            ### EMAIL (NO PREAMBLE):

            """
        )
        
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        
        return res.content


if __name__ == "__main__":
    # Test the Chain class
    print("Testing Chain class...")
    
    try:
        chain = Chain()
        print("✓ Chain initialized successfully")
        print(f"✓ Using model: llama-3.1-70b-versatile")
        
        # Test with sample data
        sample_text = """
        Senior Python Developer
        Experience: 5+ years
        Skills: Python, Django, PostgreSQL, AWS
        We are looking for an experienced Python developer to join our team.
        """
        
        print("\nTesting job extraction...")
        jobs = chain.extract_jobs(sample_text)
        print(f"✓ Extracted {len(jobs)} job(s)")
        print(f"Jobs: {jobs}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nTo fix this:")
        print("1. Create a .env file in your project directory")
        print("2. Add: GROQ_API_KEY=your_api_key_here")
        print("3. Get your API key from https://console.groq.com/")