import os
from celery_config import celery_app
import resume_service


@celery_app.task(bind=True, name='tasks.analyze_resume')
def analyze_resume_task(self, resume_path, job_description, job_url, gemini_api_key):
    """
    Async task to analyze resume.

    Args:
        self: Celery task instance
        resume_path: Path to uploaded resume PDF
        job_description: Job description text (or None)
        job_url: Job description URL (or None)
        gemini_api_key: Gemini API key

    Returns:
        dict: Analysis results
    """
    try:
        self.update_state(state='PROCESSING', meta={'status': 'Extracting resume text...'})

        resume_text = resume_service.extract_text_from_pdf(resume_path)

        if job_url:
            self.update_state(state='PROCESSING', meta={'status': 'Fetching job description...'})
            job_description = resume_service.extract_text_from_url(job_url)

        self.update_state(state='PROCESSING', meta={'status': 'Analyzing with AI...'})
        result = resume_service.analyze_resume(
            gemini_api_key,
            resume_text,
            job_description
        )

        os.remove(resume_path)
        return result

    except Exception as e:
        os.remove(resume_path)
        return {
            'success': False,
            'error': str(e)
        }
