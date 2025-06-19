#!/usr/bin/env python
import sys
import warnings
import os
from dotenv import load_dotenv

from datetime import datetime

from email_scan.crew import EmailScan

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    # Prompt the user for the date to scan emails
    scan_date = input("Enter the date to scan emails (YYYY-MM-DD) or press Enter for today's date: ")
    
    # If no date is provided, use today's date
    if not scan_date:
        scan_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"Scanning emails for date: {scan_date}")
    
       
    # Define the inputs for the crew
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year),
        'scan_date': scan_date,
        'email_content': """
        Subject: Project Update and Action Items
        
        Hi Team,
        
        I wanted to provide a quick update on our AI project and outline some action items:
        
        1. Please review the latest documentation by next Monday.
        2. John, could you send me the budget report by end of this week?
        3. We need to schedule a meeting with the client - I'm thinking sometime next week.
        4. I'll prepare the presentation slides for our next meeting.
        
        Let me know if you have any questions!
        
        Best regards,
        Alex
        """
    }
    
    try:
        EmailScan().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
