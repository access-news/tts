from transcription import transcribe
from openai import OpenAI
from pathlib import Path
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI()

# Define folder names
INPUT_FOLDER_NAME = "input"
OUTPUT_FOLDER_NAME = "output"
FLYERS_FOLDER_NAME = "flyers"

def list_flyer_directories():
    """List all available flyer directories"""
    logger.info("Scanning for flyer directories")
    if not os.path.exists(FLYERS_FOLDER_NAME):
        logger.warning(f"Flyers folder '{FLYERS_FOLDER_NAME}' does not exist")
        return []
    
    flyer_dirs = [d for d in os.listdir(FLYERS_FOLDER_NAME) 
                 if os.path.isdir(os.path.join(FLYERS_FOLDER_NAME, d))]
    logger.info(f"Found {len(flyer_dirs)} flyer directories: {flyer_dirs}")
    return flyer_dirs

def list_date_directories(flyer_type):
    """List all date directories for a specific flyer type"""
    logger.info(f"Scanning for date directories in {flyer_type}")
    flyer_path = os.path.join(FLYERS_FOLDER_NAME, flyer_type)
    if not os.path.exists(flyer_path):
        logger.warning(f"Flyer path '{flyer_path}' does not exist")
        return []
    
    date_dirs = [d for d in os.listdir(flyer_path) 
                if os.path.isdir(os.path.join(flyer_path, d))]
    logger.info(f"Found {len(date_dirs)} date directories: {date_dirs}")
    return sorted(date_dirs, reverse=True)

def get_images_from_folder(folder_path):
    """Get all image files from a folder"""
    logger.info(f"Scanning for images in {folder_path}")
    image_extensions = ('.png', '.jpg', '.jpeg')
    images = [f for f in os.listdir(folder_path) 
             if f.lower().endswith(image_extensions)]
    logger.info(f"Found {len(images)} images: {images}")
    return images

def process_files(input_path, is_flyer=False):
    """Process files from the specified input path"""
    logger.info(f"Processing files from {input_path}")
    start_time = time.time()
    
    # Ensure the output folder exists
    os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)
    
    # Get input files
    if is_flyer:
        input_files = get_images_from_folder(input_path)
    else:
        input_files = [f for f in os.listdir(input_path) 
                      if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))]
    
    if not input_files:
        logger.warning("No valid input files found!")
        return
    
    logger.info(f"Starting transcription for {len(input_files)} files")
    try:
        transcriptions = transcribe(input_path)
        logger.info(f"Received {len(transcriptions)} transcriptions")
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}", exc_info=True)
        return
    
    # Process each transcription
    for idx, (transcription, input_file) in enumerate(zip(transcriptions, input_files), 1):
        logger.info(f"Processing file {idx}/{len(input_files)}: {input_file}")
        output_filename = os.path.splitext(input_file)[0] + ".mp3"
        output_path = Path(OUTPUT_FOLDER_NAME) / output_filename
        
        try:
            logger.info(f"Generating speech for {input_file}")
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=transcription
            )
            
            logger.info(f"Saving audio to {output_path}")
            response.stream_to_file(output_path)
            logger.info(f"Successfully generated audio file: {output_path}")
        except Exception as e:
            logger.error(f"Error generating audio for {input_file}: {str(e)}", exc_info=True)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Processing completed in {elapsed_time:.2f} seconds")

def main():
    logger.info("Starting application")
    
    choice = select_input_source()
    
    if choice == '1':
        logger.info("Processing from regular input folder")
        process_files(INPUT_FOLDER_NAME)
    else:
        logger.info("Processing from flyers directory")
        flyer_type = select_flyer_directory()
        if not flyer_type:
            logger.error("No flyer type selected")
            return
        
        date_dir = select_date_directory(flyer_type)
        if not date_dir:
            logger.error("No date directory selected")
            return
        
        flyer_path = os.path.join(FLYERS_FOLDER_NAME, flyer_type, date_dir)
        logger.info(f"Processing flyer path: {flyer_path}")
        process_files(flyer_path, is_flyer=True)

if __name__ == "__main__":
    main()