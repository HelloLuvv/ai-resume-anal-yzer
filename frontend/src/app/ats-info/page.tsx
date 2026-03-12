'use client'

export default function ATSInfo() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-x-hidden p-8">
      <main className="w-full max-w-3xl mx-auto text-white">
        <h1 className="text-4xl font-bold mb-4">How the ATS Score Works</h1>
        <p className="mb-4">
          Our scoring system is not tied to any single commercial Applicant Tracking System (ATS).
          Instead, we calculate a score based on common screening principles used by modern
          recruiting software such as Keyword Matching, Section Structure, Skills Relevance, and
          Formatting Compatibility. These factors are derived from research and best practices
          published by organizations like the Society for Human Resource Management, LinkedIn, and
          Indeed.
        </p>
        <h2 className="text-2xl font-semibold mt-6 mb-2">Score Components</h2>
        <ul className="list-disc list-inside space-y-2 text-slate-300">
          <li><strong>Keyword Match</strong> – how many job-related terms appear in your resume.</li>
          <li><strong>Skills Match</strong> – presence of technical or role-specific skills.</li>
          <li><strong>Formatting</strong> – checks for tables, images, or multi‑column layouts that many
              systems struggle with.</li>
          <li><strong>Experience</strong> – whether your work history is detectable by entity
              extraction.</li>
          <li><strong>Section Structure</strong> – presence of standard headings like "Education",
              "Experience", and "Skills".</li>
          <li><strong>Education</strong> – simple detection of degree information.</li>
        </ul>
        <p className="mt-4">
          We also offer an "ATS Simulator" mode that slightly adjusts the weighting to mimic
          popular platforms like Workday, Greenhouse, or Lever. This gives you a feel for how your
          resume might perform across different systems but is still just an estimate.
        </p>
        <p className="mt-6 text-sm text-slate-400">
          <em>Disclaimer:</em> there is no global ATS standard; scores are estimates intended to
          reflect common practices. Always tailor your resume to the job posting and follow
          platform-specific instructions when submitting.
        </p>
        <div className="mt-8">
          <a href="/" className="text-blue-400 underline hover:text-blue-200">Back to home</a>
        </div>
      </main>
    </div>
  )
}