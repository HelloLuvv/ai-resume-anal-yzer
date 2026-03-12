from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

try:
    supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
    print("Supabase client created successfully")
except Exception as e:
    print(f"Error: {e}")

# simple local function tests
if __name__ == '__main__':
    from app import extract_contact_info, check_formatting, extract_job_keywords, calculate_ats_breakdown
    sample = "John Doe\nEmail: john@example.com\nPhone: +1 555-1234\nSkills: Python, SQL"
    print('contact', extract_contact_info(sample))
    print('formatting issues', check_formatting(sample))
    print('job keywords', extract_job_keywords('Looking for a Python engineer with Docker'))
    print('breakdown', calculate_ats_breakdown(['python'], ['b.sc'], {'roles':['engineer']}, sample))
