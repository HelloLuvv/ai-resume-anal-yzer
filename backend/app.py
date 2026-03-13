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


def extract_contact_info(text):
    """Pull out name, email, phone number from resume text."""
    name = None
    email = None
    phone = None

    # simple regex for email and phone
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        email = email_match.group(0)
    phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,}\d)', text)
    if phone_match:
        phone = phone_match.group(0)

    # spaCy NER for person name
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            name = ent.text
            break

    return {'name': name, 'email': email, 'phone': phone}


def check_formatting(text):
    """Look for formatting patterns that ATS generally disfavor."""
    issues = []
    # tables or vertical bars
    if re.search(r'\|', text) or re.search(r'\t', text):
        issues.append('Tables or tabular formatting detected')
    # image references (often extracted as [Figure], etc.)
    if re.search(r'\[Figure', text, re.I) or re.search(r'Figure \d', text):
        issues.append('Image references detected')
    # two-column heuristic (very rough): many short lines alternating
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) > 20:
        short = sum(1 for l in lines if len(l.split()) < 3)
        if short / len(lines) > 0.3:
            issues.append('Possible multi-column layout detected')
    return issues


def check_section_structure(text):
    """Score presence of common resume sections and return missing ones."""
    sections = ['education', 'experience', 'skills', 'projects', 'certifications', 'summary', 'objective']
    found = []
    for sec in sections:
        if re.search(r'\b' + re.escape(sec) + r'\b', text, re.I):
            found.append(sec)
    score = min(10, len(found) * 2)  # 2 points per section up to 10
    missing = [sec for sec in sections if sec not in found]
    return score, missing


def calculate_ats_breakdown(skills, education, experience, text, formatting_issues=None, section_structure_score=None, job_keywords=None, simulator='generic'):
    breakdown = {}
    # weighting differs slightly by simulator
    weights = {
        'keyword': 35,
        'skills': 20,
        'format': 15,
        'experience': 10,
        'sections': 10,
        'education': 10
    }
    if simulator == 'workday':
        weights['keyword'] = 30
        weights['skills'] = 25
    elif simulator == 'greenhouse':
        weights['format'] = 20
        weights['sections'] = 5
    elif simulator == 'lever':
        weights['experience'] = 15
        weights['education'] = 5
    # keyword match
    keyword_score = 0
    if job_keywords:
        # compute ratio of job_keywords found in text
        found = sum(1 for kw in job_keywords if kw.lower() in text.lower())
        keyword_score = (found / max(len(job_keywords), 1)) * weights['keyword']
    else:
        # fallback: use skills count as proxy
        keyword_score = min(len(skills) * 5, weights['keyword'])
    breakdown['keyword_match'] = round(keyword_score, 1)

    # skills match
    skills_score = min(len(skills) * 5, weights['skills'])
    breakdown['skills'] = round(skills_score, 1)

    # formatting
    if formatting_issues is None:
        formatting_issues = check_formatting(text)
    format_score = max(weights['format'] - len(formatting_issues) * 5, 0)
    breakdown['formatting'] = round(format_score, 1)
    breakdown['formatting_issues'] = formatting_issues

    # experience
    exp_score = weights['experience'] if experience.get('roles') else 0
    breakdown['experience'] = round(exp_score, 1)

    # sections
    if section_structure_score is None:
        section_structure_score, missing = check_section_structure(text)
    breakdown['sections'] = round(section_structure_score, 1)
    breakdown['missing_sections'] = missing

    # education
    edu_score = weights['education'] if education else 0
    breakdown['education'] = round(edu_score, 1)

    # total
    breakdown['total'] = round(sum(breakdown[k] for k in ['keyword_match','skills','formatting','experience','sections','education']), 1)
    return breakdown


def extract_job_keywords(text):
    """Return set of known skills (from SKILLS list) found in the job description."""
    found = []
    lower = text.lower()
    for skill in SKILLS:
        if skill.lower() in lower:
            found.append(skill)
    # include other words using basic tokenization (could be enhanced later)
    return list(set(found))


def skills_from_text(text):
    """Small helper that uses the same extractor as resume analysis."""
    return extract_skills(text, SKILLS)

def calculate_ats_score(skills, education, experience, text, formatting_issues=None, section_structure_score=None, job_keywords=None, simulator='generic'):
    """Return a simple overall ATS score (0-100) using the provided breakdown pieces.
    This wrapper will call :pyfunc:`calculate_ats_breakdown` and sum the components.
    ``simulator`` can be one of ``generic``/``workday``/``greenhouse``/``lever``
    to slightly tweak weights and mimic different vendor behaviours.
    """
    breakdown = calculate_ats_breakdown(skills, education, experience, text,
                                        formatting_issues=formatting_issues,
                                        section_structure_score=section_structure_score,
                                        job_keywords=job_keywords,
                                        simulator=simulator)
    return min(breakdown.get('total', 0), 100)

def generate_suggestions(skills, education, experience, formatting_issues=None, section_structure_missing=None):
    suggestions = []
    if len(skills) < 3:
        suggestions.append("Add more technical skills relevant to your field")
    if not education:
        suggestions.append("Include your education background")
    if not experience['roles']:
        suggestions.append("Add detailed work experience")
    if len(experience['dates']) < 2:
        suggestions.append("Include dates for your experiences")
    if formatting_issues:
        for issue in formatting_issues:
            suggestions.append(f"Fix formatting issue: {issue}")
    if section_structure_missing:
        suggestions.append("Consider adding or renaming sections: " + ", ".join(section_structure_missing))
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
        
        contacts = extract_contact_info(text)
        skills = extract_skills(text, SKILLS)
        education = extract_education(text)
        experience = extract_experience(text)
        formatting_issues = check_formatting(text)
        section_score, missing_sections = check_section_structure(text)
        suggestions = generate_suggestions(skills, education, experience,
                                           formatting_issues=formatting_issues,
                                           section_structure_missing=missing_sections)
        

        
        return jsonify({
            'contacts': contacts,
            'skills': skills,
            'education': education,
            'experience': experience,
            'formatting_issues': formatting_issues,
            'sections_missing': missing_sections,
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
        simulator = request.json.get('simulator', 'generic')
        job_desc = request.json.get('job_description')

        if not resume_id:
            return jsonify({'error': 'Missing resume_id'}), 400
        
        # Get text from resume
        text_res = auth_supabase.table('resumes').select('text').eq('file_name', resume_id).execute()
        if not text_res.data:
            return jsonify({'error': 'Resume not found'}), 404
        text = text_res.data[0]['text']

        # Compute analysis fresh from text (avoid database schema issues)
        skills = extract_skills(text, SKILLS)
        education = extract_education(text)
        experience = extract_experience(text)
        formatting_issues = check_formatting(text)
        _, missing_sections = check_section_structure(text)

        # Prepare job keywords if provided
        job_keywords = None
        if job_desc:
            job_keywords = extract_job_keywords(job_desc)

        breakdown = calculate_ats_breakdown(skills, education, experience, text,
                                           formatting_issues=formatting_issues,
                                           job_keywords=job_keywords,
                                           simulator=simulator)
        score = breakdown['total']
        
        return jsonify({'score': score, 'breakdown': breakdown})
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
        
        # Get resume text and compute skills
        res = auth_supabase.table('resumes').select('text').eq('file_name', resume_id).execute()
        if not res.data:
            return jsonify({'error': 'Resume not found'}), 404
        text = res.data[0]['text']
        skills = extract_skills(text, SKILLS)
        
        jobs = recommend_jobs(skills)
        return jsonify({'jobs': jobs})
    except Exception as e:
        return jsonify({'error': f'Failed to get job recommendations: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


@app.route('/api/job-match', methods=['POST'])
def job_match():
    """Compare resume against a provided job description."""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing authorization token'}), 401
        token = auth_header.replace('Bearer ', '')
        auth_supabase = get_auth_supabase(token)

        resume_id = request.json.get('resume_id')
        job_desc = request.json.get('job_description', '')
        if not resume_id or not job_desc:
            return jsonify({'error': 'Missing resume_id or job_description'}), 400

        # fetch resume text
        res = auth_supabase.table('resumes').select('text').eq('file_name', resume_id).execute()
        if not res.data:
            return jsonify({'error': 'Resume not found'}), 404
        text = res.data[0]['text']

        # compute simple cosine similarity on bag-of-words
        vec = CountVectorizer().fit_transform([text, job_desc])
        score = float(cosine_similarity(vec[0:1], vec[1:])[0][0])
        match_percent = round(score * 100, 1)

        job_keywords = extract_job_keywords(job_desc)
        found_keywords = [kw for kw in job_keywords if kw.lower() in text.lower()]
        missing_keywords = [kw for kw in job_keywords if kw not in found_keywords]

        skill_gap = [kw for kw in job_keywords if kw not in skills_from_text(text)]

        return jsonify({
            'match_score': match_percent,
            'required_keywords': job_keywords,
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'skill_gap': skill_gap
        })
    except Exception as e:
        return jsonify({'error': f'Failed to perform job match: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)