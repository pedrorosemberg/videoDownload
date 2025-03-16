import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from utils.downloader import download_video, validate_url
import tempfile
import shutil
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# Create a persistent temporary directory
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'youtube_downloads')
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        url = request.form.get('url')
        format_type = request.form.get('format')

        if not url:
            return jsonify({'error': 'URL não fornecida'}), 400

        if not validate_url(url):
            return jsonify({'error': 'URL inválida'}), 400

        if format_type not in ['mp3', 'mp4']:
            return jsonify({'error': 'Formato inválido'}), 400

        # Start download process
        file_path = download_video(url, format_type, TEMP_DIR)

        # Verify if file exists
        full_path = os.path.join(TEMP_DIR, file_path)
        if not os.path.exists(full_path):
            logger.error(f"File not found after download: {full_path}")
            return jsonify({'error': 'Arquivo não encontrado após download'}), 500

        logger.info(f"Download completed successfully. File path: {file_path}")
        return jsonify({
            'status': 'success',
            'message': 'Download concluído',
            'file_path': file_path
        })

    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        return jsonify({
            'error': f'Erro ao fazer download: {str(e)}'
        }), 500

@app.route('/get-file/<path:filename>')
def get_file(filename):
    try:
        file_path = os.path.join(TEMP_DIR, filename)
        logger.info(f"Attempting to send file: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'Arquivo não encontrado'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Error sending file: {str(e)}")
        return jsonify({
            'error': 'Erro ao enviar arquivo'
        }), 500

# Cleanup old files periodically (files older than 1 hour)
def cleanup_old_files():
    try:
        current_time = time.time()
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.getctime(file_path) < (current_time - 3600):
                os.remove(file_path)
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# Run cleanup every hour
@app.before_request
def before_request():
    if not hasattr(app, 'cleanup_last_run'):
        app.cleanup_last_run = 0

    current_time = time.time()
    if current_time - app.cleanup_last_run > 3600:  # 1 hour
        cleanup_old_files()
        app.cleanup_last_run = current_time