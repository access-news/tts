from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import base64
import io
import os
from pathlib import Path
import requests
from target_weekly_ad import main as fetch_target_ads
from transcription import transcribe
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
client = OpenAI()

# Configure upload folder
UPLOAD_FOLDER = 'input'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_single_file(file_path):
    """Process a single file and return the audio data"""
    try:
        # Get transcription
        transcriptions = transcribe(str(Path(file_path).parent))
        if not transcriptions:
            return None, "No transcription generated"

        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=transcriptions[0]
        )
        
        # Get the audio data
        audio_data = io.BytesIO()
        for chunk in response.iter_bytes():
            audio_data.write(chunk)
        audio_data.seek(0)
        
        return base64.b64encode(audio_data.read()).decode(), None
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        return None, str(e)

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files and 'base64' not in request.json and 'url' not in request.json:
        return jsonify({'error': 'No file or base64 data or URL provided'}), 400

    try:
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

        # Handle base64 data
        elif 'base64' in request.json:
            try:
                file_data = base64.b64decode(request.json['base64'])
                filename = 'input_file.png'  # Default to PNG
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400

        # Handle URL
        elif 'url' in request.json:
            try:
                response = requests.get(request.json['url'])
                response.raise_for_status()
                filename = 'downloaded_file.png'  # Default to PNG
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
            except Exception as e:
                return jsonify({'error': f'Error downloading file: {str(e)}'}), 400

        # Process the file
        audio_base64, error = process_single_file(filepath)
        
        # Clean up
        os.remove(filepath)
        
        if error:
            return jsonify({'error': error}), 500
            
        return jsonify({
            'audio': audio_base64,
            'message': 'Conversion successful'
        })

    except Exception as e:
        logger.error(f"Error in convert endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/fetch-target-ads', methods=['GET'])
def fetch_ads():
    try:
        # Create a temporary directory for processing
        temp_dir = os.path.join(UPLOAD_FOLDER, 'temp_target_ads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Fetch the ads
        fetch_target_ads()
        
        # Get the latest ads directory
        target_dir = os.path.join('flyers', 'target_weekly_ad')
        dates = sorted([d for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))], reverse=True)
        if not dates:
            return jsonify({'error': 'No target ads found'}), 404
            
        latest_date = dates[0]
        latest_dir = os.path.join(target_dir, latest_date)
        
        # Process the files and get audio data
        audio_results = []
        for file in os.listdir(latest_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(latest_dir, file)
                audio_base64, error = process_single_file(file_path)
                if error:
                    logger.error(f"Error processing {file}: {error}")
                    continue
                audio_results.append({
                    'filename': file,
                    'audio': audio_base64
                })
        
        return jsonify({
            'message': 'Target ads fetched and processed successfully',
            'date': latest_date,
            'audio_files': audio_results
        })
        
    except Exception as e:
        logger.error(f"Error fetching Target ads: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 