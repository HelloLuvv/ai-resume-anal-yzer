# AI Resume Analyzer

A production-ready AI-based resume analyzer web application.

## Features

- Upload PDF/DOCX resumes
- AI-powered skill extraction, education, and experience analysis
- ATS compatibility scoring
- Resume improvement suggestions
- Job role recommendations

## Tech Stack

- **Backend**: Python Flask, spaCy, NLTK, scikit-learn
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Database & Auth**: Supabase

## Setup

### Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account

### Backend Setup

1. Navigate to `backend` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Download spaCy model: `python -m spacy download en_core_web_sm`
4. Create `.env` file with Supabase credentials

### Frontend Setup

1. Navigate to `frontend` directory
2. Install dependencies: `npm install`
3. Create `.env.local` file with Supabase credentials

### Supabase Setup

1. Create a new Supabase project
2. Enable authentication
3. Create the following tables:

```sql
-- Users table (handled by Supabase Auth)

-- Resumes table
CREATE TABLE resumes (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  file_name TEXT,
  url TEXT,
  text TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Analyses table
CREATE TABLE analyses (
  id SERIAL PRIMARY KEY,
  resume_id TEXT REFERENCES resumes(file_name),
  skills TEXT[],
  education TEXT[],
  experience JSONB,
  suggestions TEXT[],
  ats_score INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Storage bucket
-- Create a bucket named 'resumes' with public access
```

4. Get your project URL and anon key from Supabase dashboard

### Environment Variables

#### Backend (.env)
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

#### Frontend (.env.local)
```
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Running the Application

1. Start the backend: `cd backend && python app.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000

## API Endpoints

- `POST /api/upload-resume`: Upload resume file
- `POST /api/analyze-resume`: Analyze resume content
- `POST /api/ats-score`: Calculate ATS score
- `POST /api/job-recommendations`: Get job recommendations

## Notes

- The AI uses predefined skill lists and NLP for extraction
- ATS scoring is based on keyword density, completeness, and formatting
- Job recommendations use cosine similarity on skill vectors