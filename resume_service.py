"""
Resume analysis service using Google Gemini AI.
"""
from PyPDF2 import PdfReader
import google.generativeai as genai
from newspaper import Article


TASK_DESCRIPTION = """**TASK:**
You will perform a strict, technical comparison between the provided Job Description (JD) and the Resume. Your entire analysis must be based *only* on the text in these two documents.

**CRITICAL RULES:**
1.  **Infer Context:** The Job Description is your *only* source of truth. You must *infer* the ideal candidate profile, required technical skills, and domain (e.g., "FinTech," "Data Engineering," "Frontend") directly from it.
2.  **Ignore Fluff:** You must **ignore all generic soft skills** and corporate "fluff" (e.g., "hard-working," "team player," "passionate," "good communicator"). Your analysis must focus **exclusively on concrete, actionable, technical skills, keywords, and project-based experience.**
3.  **Distinguish Experience vs. Projects:** You *must* differentiate between "Professional Experience" (jobs, internships, formal roles) and "Personal Projects" (side projects) based on the resume's own headings. Analyze them in their separate, designated sections below."""

REQUIRED_OUTPUT = """
**[Required Output: Actionable Analysis]**

**1. Skills Gap Analysis:**
* **Missing Must-Haves:** List the 3-5 most critical *technical skills* and *technologies* required by the JD that are completely missing from the resume.
* **Keywords to Add:** List 3-5 *specific technical or product keywords* from the JD (e.g., "AI pipelines," "payment products," "systems architecture") and suggest *exactly* which resume bullet point (from Experience or Projects) to integrate them into.
* **Skills to De-emphasize:** List any skills on the resume that are *not* relevant to this JD and are taking up valuable space.

**2. Experience Relevance Analysis (for Work History):**
* **Role-by-Role Rating:** For each *professional experience* or *work role* found in the resume, rate its relevance to the JD as **"High"**, **"Medium"**, or **"Low"**. Provide a 1-sentence technical reason.
* **Rewording Suggestions:** Pick the resume's *most relevant* professional experience and **rewrite 2-3 of its bullet points** to directly mirror the language and technical requirements found in the JD.

**3. Project Relevance Analysis (for Personal Projects):**
* **Project-by-Project Rating:** For each *personal project* found in the resume, rate its relevance to the JD as **"High"**, **"Medium"**, or **"Low"**. Provide a 1-sentence technical reason.
* **Positive Feedback:** If any projects are rated **"High"** and are already well-described, **explicitly state this** (e.g., "This project is highly relevant and well-explained. No changes needed.").
* **Rewording Suggestions:** If a project is relevant but poorly worded, rewrite 1-2 bullet points to improve its alignment with the JD.

**4. New Project Suggestions (to fill the gap):**
* **Actionable Ideas:** Based *only* on the "Missing Must-Haves" from section 1, suggest 1-2 *small* new projects the candidate could build.
* **Tech Stack:** For each project, specify the **exact tech stack** they should use, using *only* technologies mentioned in the JD.
* **Resume Bullet Point:** For each new project, write a single, powerful bullet point the candidate could add to their resume.
"""


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        raise Exception(f"Error extracting PDF: {str(e)}")


def extract_text_from_url(url):
    """Extract text from URL."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        raise Exception(f"Error extracting URL: {str(e)}")


def analyze_resume(gemini_api_key, resume_text, job_description):
    """Analyze resume against job description using Gemini AI."""
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
{TASK_DESCRIPTION}

**[Input 1: Job Description]**

{job_description}

**[Input 2: Resume]**

{resume_text}

{REQUIRED_OUTPUT}
"""

        response = model.generate_content(prompt)
        return {
            'success': True,
            'analysis': response.text
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
