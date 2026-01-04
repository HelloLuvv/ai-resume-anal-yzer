-- Setup script for AI Resume Analyzer
-- Go to: https://app.supabase.com/project/[your-project]/sql/new

-- 1. Create tables if they don't exist
CREATE TABLE IF NOT EXISTS public.resumes (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  file_name TEXT UNIQUE,
  url TEXT,
  text TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.analyses (
  id SERIAL PRIMARY KEY,
  resume_id TEXT UNIQUE REFERENCES public.resumes(file_name),
  skills TEXT[],
  education TEXT[],
  experience JSONB,
  suggestions TEXT[],
  ats_score INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ensure unique constraints exist (in case tables were created without them)
DO $$ 
BEGIN 
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'resumes_file_name_key') THEN
    ALTER TABLE public.resumes ADD CONSTRAINT resumes_file_name_key UNIQUE (file_name);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'analyses_resume_id_key') THEN
    ALTER TABLE public.analyses ADD CONSTRAINT analyses_resume_id_key UNIQUE (resume_id);
  END IF;
END $$;

-- 2. Enable RLS on tables
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- 3. Drop existing policies to start fresh
DROP POLICY IF EXISTS "Users can insert their own resumes" ON public.resumes;
DROP POLICY IF EXISTS "Users can read their own resumes" ON public.resumes;
DROP POLICY IF EXISTS "Users can update their own resumes" ON public.resumes;
DROP POLICY IF EXISTS "Users can delete their own resumes" ON public.resumes;

DROP POLICY IF EXISTS "Users can insert their own analyses" ON public.analyses;
DROP POLICY IF EXISTS "Users can read their own analyses" ON public.analyses;
DROP POLICY IF EXISTS "Users can update their own analyses" ON public.analyses;
DROP POLICY IF EXISTS "Users can delete their own analyses" ON public.analyses;

-- Drop storage policies if they exist
DROP POLICY IF EXISTS "Give users access to their own resumes 1j04616_0" ON storage.objects;
DROP POLICY IF EXISTS "Give users access to their own resumes 1j04616_1" ON storage.objects;
DROP POLICY IF EXISTS "Give users access to their own resumes 1j04616_2" ON storage.objects;
DROP POLICY IF EXISTS "Give users access to their own resumes 1j04616_3" ON storage.objects;

-- 4. Create policies for resumes table
CREATE POLICY "Users can insert their own resumes" ON public.resumes
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can read their own resumes" ON public.resumes
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own resumes" ON public.resumes
  FOR UPDATE USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own resumes" ON public.resumes
  FOR DELETE USING (auth.uid() = user_id);

-- 5. Create policies for analyses table
-- These policies use a subquery to check if the user owns the corresponding resume
CREATE POLICY "Users can insert their own analyses" ON public.analyses
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.resumes
      WHERE public.resumes.file_name = analyses.resume_id
      AND public.resumes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can read their own analyses" ON public.analyses
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.resumes
      WHERE public.resumes.file_name = analyses.resume_id
      AND public.resumes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update their own analyses" ON public.analyses
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM public.resumes
      WHERE public.resumes.file_name = analyses.resume_id
      AND public.resumes.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.resumes
      WHERE public.resumes.file_name = analyses.resume_id
      AND public.resumes.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete their own analyses" ON public.analyses
  FOR DELETE USING (
    EXISTS (
      SELECT 1 FROM public.resumes
      WHERE public.resumes.file_name = analyses.resume_id
      AND public.resumes.user_id = auth.uid()
    )
  );

-- 6. Storage Policies (Run these if you haven't set up storage bucket policies)
-- Allow users to upload their own resumes (files starting with their user_id)
-- Note: This assumes you have a bucket named 'resumes'
CREATE POLICY "Give users access to their own resumes 1j04616_0" ON storage.objects
FOR SELECT TO authenticated
USING (bucket_id = 'resumes' AND name LIKE auth.uid()::text || '_%');

CREATE POLICY "Give users access to their own resumes 1j04616_1" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'resumes' AND name LIKE auth.uid()::text || '_%');

CREATE POLICY "Give users access to their own resumes 1j04616_2" ON storage.objects
FOR UPDATE TO authenticated
USING (bucket_id = 'resumes' AND name LIKE auth.uid()::text || '_%')
WITH CHECK (bucket_id = 'resumes' AND name LIKE auth.uid()::text || '_%');

CREATE POLICY "Give users access to their own resumes 1j04616_3" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'resumes' AND name LIKE auth.uid()::text || '_%');
