from PyPDF2 import PdfReader
import google.generativeai as genai
import os
from dotenv import load_dotenv
from newspaper import Article

resume_pdf = 'AbhinavOhri.pdf'

def extract_text_from_pdf(pdf_path):
    text= ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error: {e}")

    return text

def extract_text_from_url(url):
    text = ""
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
    except Exception as e:
        print(f"Error: Could not extract text from URL {url}. Error: {e}")
    
    return text

extracted_resume_text = extract_text_from_pdf(resume_pdf)

# job_desc_url = "https://ats.rippling.com/rippling/jobs/f6909f33-27f5-4e1d-bc58-791d9b9fbdad?referral_id=ba8a880f-1a35-401d-bad2-fcc354f90210"
job_desc_url = "https://www.linkedin.com/jobs/view/4309753456/?alternateChannel=search&eBP=BUDGET_EXHAUSTED_JOB&refId=lMlD66LtBLlV4rqwvLP8Ug%3D%3D&trackingId=PBpn%2Bc9aE%2BljT%2BU5k7gVoA%3D%3D%27"
extracted_job_desc_from_url = extract_text_from_url(job_desc_url)

job_desc = """About the role
At Rippling, Engineering is at the heart of our business and culture. We are looking for highly motivated upcoming or recent grads to join our software engineering teams. As a New Grad Engineer at Rippling, you will work on projects that impact the highest priorities of our technology and business, all while collaborating cross-functionally with multiple teams and stakeholders. You will build products and features that fulfill our mission; free smart people to work on hard problems!

You would be joining the Spend Management team which plays a pivotal role in redefining the future of corporate spending as we scale from millions to billions of dollars in transactions per month. The Reimbursement team is looking for a backend full-stack engineer who skews more backend to enable employees to get paid for a company expense that they paid themselves. The product requires integrating with payment products, approval frameworks, AI pipelines, payroll runs, and more. This team has a direct impact on Rippling's revenue and is bought as a standalone product for new customers. You will work closely with PMs and fellow engineering peers to own and deliver product experiences from start to finish!

What you will do
1+ years of overall experience with a Bachelors or Masters in Computer Science, or related fields
Knowledge of algorithms, data structures, and systems architecture
Familiarity with the following programming languages: Python, React, JavaScript, and HTML/CSS
You care about product ownership and solving problems for our customers
You’re passionate about being in a product focused environment where everyone cares deeply about customer impactWhat you will need
Describe the experience and attributes of the ideal candidate
Describe the experience and attributes of the ideal candidate
Additional Information
Rippling is an equal opportunity employer. We are committed to building a diverse and inclusive workforce and do not discriminate based on race, religion, color, national origin, ancestry, physical disability, mental disability, medical condition, genetic information, marital status, sex, gender, gender identity, gender expression, age, sexual orientation, veteran or military status, or any other legally protected characteristics, Rippling is committed to providing reasonable accommodations for candidates with disabilities who need assistance during the hiring process. To request a reasonable accommodation, please email accomodations@rippling.com



Rippling highly values having employees working in-office to foster a collaborative work environment and company culture.  For office-based employees (employees who live within a defined radius of a Rippling office), Rippling considers working in the office, at least three days a week under current policy, to be an essential function of the employee's role.



This role will receive a competitive salary + benefits + equity. The salary for US-based employees will be aligned with one of the ranges below based on location; see which tier applies to your location here.

A variety of factors are considered when determining someone’s compensation–including a candidate’s professional background, experience, and location. Final offer amounts may vary from the amounts listed below."""

task_desciption = """**TASK:**
You will perform a strict, technical comparison between the provided Job Description (JD) and the Resume. Your entire analysis must be based *only* on the text in these two documents.

**CRITICAL RULES:**
1.  **Infer Context:** The Job Description is your *only* source of truth. You must *infer* the ideal candidate profile, required technical skills, and domain (e.g., "FinTech," "Data Engineering," "Frontend") directly from it.
2.  **Ignore Fluff:** You must **ignore all generic soft skills** and corporate "fluff" (e.g., "hard-working," "team player," "passionate," "good communicator"). Your analysis must focus **exclusively on concrete, actionable, technical skills, keywords, and project-based experience.**
3.  **Distinguish Experience vs. Projects:** You *must* differentiate between "Professional Experience" (jobs, internships, formal roles) and "Personal Projects" (side projects) based on the resume's own headings. Analyze them in their separate, designated sections below."""

required_output = """
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

prompt = f"""
{task_desciption}

**[Input 1: Job Description]**

{extracted_job_desc_from_url}

**[Input 2: Resume]**

{extracted_resume_text}

{required_output}
"""

if __name__ == "__main__":
    load_dotenv()
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    except KeyError:
        print("Error: GEMINI_API_KEY environment variable not set.")
        exit()


    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        # Send the prompt and get the response
        response = model.generate_content(prompt)
        
        print("\n✅ Here is your resume analysis:\n")
        print(response.text)

    except Exception as e:
        print(f"\nAn error occurred: {e}")


