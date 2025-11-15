"""
API routes for resume analysis.
"""
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
import resume_service


@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'Resume Gap Finder API',
        'version': '1.0.0',
        'endpoints': {
            'analyze': '/analyze (POST)',
            'health': '/health (GET)'
        }
    })


@app.route('/health')
def health():
    """Health check."""
    return jsonify({'status': 'healthy'})


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze resume against job description.

    Form data:
        - resume: PDF file
        - job_description: Text OR
        - job_url: URL
    """
    try:
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No resume file provided'}), 400

        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not resume_file.filename.endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400

        job_url = request.form.get('job_url')
        job_description = request.form.get('job_description')

        if not job_url and not job_description:
            return jsonify({
                'success': False,
                'error': 'Provide either job_url or job_description'
            }), 400

        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)
        app.logger.info(f'Saved resume: {filename}')

        resume_text = resume_service.extract_text_from_pdf(filepath)

        if job_url:
            app.logger.info(f'Fetching job from URL: {job_url}')
            job_description = resume_service.extract_text_from_url(job_url)

        app.logger.info('Starting analysis...')
        result = resume_service.analyze_resume(
            app.config['GEMINI_API_KEY'],
            resume_text,
            job_description
        )
        os.remove(filepath)

        app.logger.info('Analysis complete')
        return jsonify(result)

    except Exception as e:
        app.logger.error(f'Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500
