"""
API routes for resume analysis.
"""
import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import app
from tasks import analyze_resume_task
from celery.result import AsyncResult


@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'service': 'Resume Gap Finder API',
        'version': '1.0.0',
        'endpoints': {
            'analyze': '/analyze (POST) - Submit analysis task',
            'status': '/task/<task_id> (GET) - Get task status',
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
    Submit resume analysis task.

    Form data:
        - resume: PDF file
        - job_description: Text OR
        - job_url: URL

    Returns:
        202: task_id and status_url
        400: error message
        500: error message
    """
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400

        resume_file = request.files['resume']
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not resume_file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files allowed'}), 400

        job_url = request.form.get('job_url')
        job_description = request.form.get('job_description')

        if not job_url and not job_description:
            return jsonify({'error': 'Provide either job_url or job_description'}), 400

        filename = secure_filename(resume_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume_file.save(filepath)
        app.logger.info(f'Saved resume: {filename}')

        task = analyze_resume_task.delay(
            filepath,
            job_description,
            job_url,
            app.config['GEMINI_API_KEY']
        )

        app.logger.info(f'Task queued: {task.id}')
        return jsonify({
            'task_id': task.id,
            'status_url': f'/task/{task.id}'
        }), 202

    except Exception as e:
        app.logger.error(f'Error submitting task: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/task/<task_id>')
def get_task_status(task_id):
    """
    Get task status (for polling).

    Returns:
        200: Task state, status message, and result
        500: error message
    """
    try:
        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': 'Task is waiting in queue...'
            }
        elif task.state == 'PROCESSING':
            response = {
                'state': task.state,
                'status': task.info.get('status', 'Processing...')
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'state': task.state,
                'error': str(task.info)
            }
        else:
            response = {
                'state': task.state,
                'status': str(task.info)
            }

        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f'Error checking task status: {str(e)}')
        return jsonify({'error': str(e)}), 500
