from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, ClientOptions
import os
from dotenv import load_dotenv
import spacy
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
import pdfplumber
from docx import Document
import tempfile
import jwt
import json
import base64

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_auth_supabase(token):
    return create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY'),
        options=ClientOptions(headers={'Authorization': f'Bearer {token}'})
    )

def get_user_id_from_token(token):
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get('sub')
    except:
        return None

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    import subprocess
    import sys
    subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Predefined skills and degrees
SKILLS = ['python', 'javascript', 'java', 'c++', 'machine learning', 'data analysis', 'web development', 'sql', 'react', 'node.js', 'flask', 'django', 'tensorflow', 'pytorch', 'nlp', 'computer vision', 'aws', 'docker', 'git', 'agile', 'scrum', 'html', 'css', 'linux', 'kubernetes']
DEGREES = ['bachelor', 'master', 'phd', 'bsc', 'msc', 'ba', 'ma', 'bachelor of science', 'master of science']

# Job roles with skills
JOBS = {
    'data scientist': ['python', 'machine learning', 'data analysis', 'sql', 'tensorflow', 'pytorch'],
    'web developer': ['javascript', 'react', 'node.js', 'html', 'css', 'web development'],
    'software engineer': ['python', 'java', 'c++', 'git', 'agile', 'scrum'],
    'ml engineer': ['python', 'tensorflow', 'pytorch', 'machine learning', 'nlp', 'computer vision'],
    'devops engineer': ['docker', 'aws', 'git', 'linux', 'kubernetes']
}

def extract_text(file_path):
    if file_path.lower().endswith('.pdf'):
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += (page.extract_text() or '') + '\n'
        return text
    elif file_path.lower().endswith('.docx'):
        doc = Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    return ''

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

def extract_skills(text, skills_list):
    doc = nlp(text)
    extracted = []
    for token in doc:
        if token.lemma_.lower() in skills_list:
            extracted.append(token.lemma_.lower())
    return list(set(extracted))

def extract_education(text):
    doc = nlp(text)
    education = []
    for ent in doc.ents:
        if ent.label_ in ['ORG', 'GPE'] and any(deg in ent.text.lower() for deg in DEGREES):
            education.append(ent.text)
    # Also check for degree mentions
    for deg in DEGREES:
        if deg in text:
            education.append(deg)
    return list(set(education))

def extract_experience(text):
    dates = re.findall(r'\b(19|20)\d{2}\b', text)
    doc = nlp(text)
    roles = []
    for ent in doc.ents:
        if ent.label_ == 'PERSON' or 'engineer' in ent.text.lower() or 'developer' in ent.text.lower() or 'analyst' in ent.text.lower():
            roles.append(ent.text)
    return {'dates': list(set(dates)), 'roles': list(set(roles))}

def calculate_ats_score(skills, education, experience, text):
    score = 0
    # Skills presence
    score += min(len(skills) * 5, 40)
    # Education
    if education:
        score += 20
    # Experience
    if experience['roles']:
        score += 20
    # Length
    word_count = len(text.split())
    if word_count > 200:
        score += 10
    # Formatting (assume good)
    score += 10
    return min(score, 100)

def generate_suggestions(skills, education, experience):
    suggestions = []
    if len(skills) < 3:
        suggestions.append("Add more technical skills relevant to your field")
    if not education:
        suggestions.append("Include your education background")
    if not experience['roles']:
        suggestions.append("Add detailed work experience")
    if len(experience['dates']) < 2:
        suggestions.append("Include dates for your experiences")
    return suggestions

def recommend_jobs(skills):
    if not skills:
        return []
    user_skills = ' '.join(skills)
    job_skills = [' '.join(JOBS[job]) for job in JOBS]
    all_texts = [user_skills] + job_skills
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(all_texts)
    similarities = cosine_similarity(vectors[0:1], vectors[1:])[0]
    top_indices = similarities.argsort()[-3:][::-1]
    recommendations = [list(JOBS.keys())[i] for i in top_indices]
    return recommendations

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    try:
        file = request.files.get('resume')
        if not file:
            return jsonify({'error': 'Missing file'}), 400
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
        token = auth_header.replace('Bearer ', '')
        
        # Get user ID from token
        user_id = get_user_id_from_token(token)
        if not user_id:
            return jsonify({'error': 'Invalid authentication token'}), 401
        
        # Create authenticated Supabase client with user's token for RLS
        auth_supabase = get_auth_supabase(token)
        
        # Save to temp - Use a safer approach for Windows
        suffix = os.path.splitext(file.filename)[1]
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        file.save(temp_path)
        
        # Extract text
        text = extract_text(temp_path)
        cleaned_text = clean_text(text)
        
        # Upload to Supabase Storage with authenticated client
        try:
            bucket = auth_supabase.storage.from_('resumes')
            file_name = f"{user_id}_{file.filename}"
            with open(temp_path, 'rb') as f:
                upload_res = bucket.upload(file_name, f, {"upsert": "true"})
            
            # Check if upload was successful (different versions of supabase-py return different things)
            # In latest it might raise an exception or return an object with error
        except Exception as storage_err:
            print(f'Storage error: {str(storage_err)}')
            return jsonify({'error': f'Failed to upload to storage: {str(storage_err)}. Ensure "resumes" bucket exists.'}), 500

        url = bucket.get_public_url(file_name)
        
        # Store in DB using authenticated client (for RLS) - user_id will be enforced by RLS
        try:
            auth_supabase.table('resumes').upsert({
                'user_id': user_id,
                'file_name': file_name,
                'url': url,
                'text': cleaned_text
            }, on_conflict='file_name').execute()
        except Exception as db_err:
            print(f'Database error: {str(db_err)}')
            return jsonify({'error': f'Failed to save resume metadata: {str(db_err)}'}), 500
        
        os.remove(temp_path)
        return jsonify({'resume_id': file_name, 'url': url})
    except Exception as e:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        print(f'Error in upload_resume: {str(e)}')
        return jsonify({'error': f'Failed to upload resume: {str(e)}'}), 500

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
        token = auth_header.replace('Bearer ', '')
        
        auth_supabase = get_auth_supabase(token)
        
        resume_id = request.json.get('resume_id')
        if not resume_id:
            return jsonify({'error': 'Missing resume_id'}), 400
        
        # Get text from DB using authenticated client (for RLS)
        res = auth_supabase.table('resumes').select('text').eq('file_name', resume_id).execute()
        if not res.data:
            return jsonify({'error': 'Resume not found'}), 404
        text = res.data[0]['text']
        
        skills = extract_skills(text, SKILLS)
        education = extract_education(text)
        experience = extract_experience(text)
        suggestions = generate_suggestions(skills, education, experience)
        
        # Store analysis using authenticated client
        auth_supabase.table('analyses').upsert({
            'resume_id': resume_id,
            'skills': skills,
            'education': education,
            'experience': experience,
            'suggestions': suggestions
        }, on_conflict='resume_id').execute()
        
        return jsonify({
            'skills': skills,
            'education': education,
            'experience': experience,
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({'error': f'Failed to analyze resume: {str(e)}'}), 500

@app.route('/api/ats-score', methods=['POST'])
def ats_score():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
        token = auth_header.replace('Bearer ', '')
        
        auth_supabase = get_auth_supabase(token)
        
        resume_id = request.json.get('resume_id')
        if not resume_id:
            return jsonify({'error': 'Missing resume_id'}), 400
        
        # Get analysis using authenticated client
        res = auth_supabase.table('analyses').select('*').eq('resume_id', resume_id).execute()
        if not res.data:
            return jsonify({'error': 'Analysis not found'}), 404
        data = res.data[0]
        
        # Get text using authenticated client
        text_res = auth_supabase.table('resumes').select('text').eq('file_name', resume_id).execute()
        text = text_res.data[0]['text']
        
        score = calculate_ats_score(data['skills'], data['education'], data['experience'], text)
        
        # Update using authenticated client
        auth_supabase.table('analyses').update({'ats_score': score}).eq('resume_id', resume_id).execute()
        
        return jsonify({'score': score})
    except Exception as e:
        return jsonify({'error': f'Failed to calculate ATS score: {str(e)}'}), 500

@app.route('/api/job-recommendations', methods=['POST'])
def job_recommendations():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
        token = auth_header.replace('Bearer ', '')
        
        auth_supabase = get_auth_supabase(token)
        
        resume_id = request.json.get('resume_id')
        if not resume_id:
            return jsonify({'error': 'Missing resume_id'}), 400
        
        res = auth_supabase.table('analyses').select('skills').eq('resume_id', resume_id).execute()
        if not res.data:
            return jsonify({'error': 'Analysis not found'}), 404
        skills = res.data[0]['skills']
        
        jobs = recommend_jobs(skills)
        return jsonify({'jobs': jobs})
    except Exception as e:
        return jsonify({'error': f'Failed to get job recommendations: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)