import os
import logging
from flask import Flask, render_template, request, jsonify, send_file
from utils.downloader import download_video, validate_url
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key")

# Temporary directory for downloads
TEMP_DIR = tempfile.mkdtemp()

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
        return send_file(
            os.path.join(TEMP_DIR, filename),
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error sending file: {str(e)}")
        return jsonify({
            'error': 'Erro ao enviar arquivo'
        }), 500

# Cleanup temp files when app exits
@app.teardown_appcontext
def cleanup(error):
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
