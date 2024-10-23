from transcription import transcribe
from openai import OpenAI
from pathlib import Path
import os

# Initialize the OpenAI client
client = OpenAI()

# Define folder names
INPUT_FOLDER_NAME = "input"
OUTPUT_FOLDER_NAME = "output"
FLYERS_FOLDER_NAME = "flyers"

def list_flyer_directories():
    """List all available flyer directories"""
    if not os.path.exists(FLYERS_FOLDER_NAME):
        return []
    
    # Get all subdirectories in the flyers folder
    flyer_dirs = [d for d in os.listdir(FLYERS_FOLDER_NAME) 
                 if os.path.isdir(os.path.join(FLYERS_FOLDER_NAME, d))]
    return flyer_dirs

def list_date_directories(flyer_type):
    """List all date directories for a specific flyer type"""
    flyer_path = os.path.join(FLYERS_FOLDER_NAME, flyer_type)
    if not os.path.exists(flyer_path):
        return []
    
    # Get all date subdirectories
    date_dirs = [d for d in os.listdir(flyer_path) 
                if os.path.isdir(os.path.join(flyer_path, d))]
    return sorted(date_dirs, reverse=True)  # Most recent first

def get_images_from_folder(folder_path):
    """Get all image files from a folder"""
    image_extensions = ('.png', '.jpg', '.jpeg')
    return [f for f in os.listdir(folder_path) 
            if f.lower().endswith(image_extensions)]

def select_input_source():
    """Interactive function to select input source"""
    print("\nSelect input source:")
    print("1. Regular input folder")
    print("2. Flyers")
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice in ['1', '2']:
            return choice
        print("Invalid choice. Please enter 1 or 2.")

def select_flyer_directory():
    """Interactive function to select flyer directory"""
    flyer_dirs = list_flyer_directories()
    
    if not flyer_dirs:
        print("No flyer directories found!")
        return None
    
    print("\nAvailable flyer types:")
    for i, d in enumerate(flyer_dirs, 1):
        print(f"{i}. {d}")
    
    while True:
        try:
            choice = int(input(f"Select flyer type (1-{len(flyer_dirs)}): "))
            if 1 <= choice <= len(flyer_dirs):
                return flyer_dirs[choice - 1]
            print(f"Please enter a number between 1 and {len(flyer_dirs)}")
        except ValueError:
            print("Please enter a valid number")

def select_date_directory(flyer_type):
    """Interactive function to select date directory"""
    date_dirs = list_date_directories(flyer_type)
    
    if not date_dirs:
        print("No date directories found!")
        return None
    
    print("\nAvailable dates:")
    for i, d in enumerate(date_dirs, 1):
        print(f"{i}. {d}")
    
    while True:
        try:
            choice = int(input(f"Select date (1-{len(date_dirs)}): "))
            if 1 <= choice <= len(date_dirs):
                return date_dirs[choice - 1]
            print(f"Please enter a number between 1 and {len(date_dirs)}")
        except ValueError:
            print("Please enter a valid number")

def process_files(input_path, is_flyer=False):
    """Process files from the specified input path"""
    # Ensure the output folder exists
    os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)
    
    # Get input files
    if is_flyer:
        input_files = get_images_from_folder(input_path)
    else:
        input_files = [f for f in os.listdir(input_path) 
                      if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))]
    
    if not input_files:
        print("No valid input files found!")
        return
    
    # Get transcriptions - pass the input_path to transcribe
    transcriptions = transcribe(input_path)
    
    # Process each transcription
    for transcription, input_file in zip(transcriptions, input_files):
        # Create the output filename
        output_filename = os.path.splitext(input_file)[0] + ".mp3"
        output_path = Path(OUTPUT_FOLDER_NAME) / output_filename
        
        try:
            # Generate speech from the transcription
            response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=transcription
            )
            
            # Save the audio to a file
            response.stream_to_file(output_path)
            print(f"Generated audio file: {output_path}")
        except Exception as e:
            print(f"Error generating audio for {input_file}: {e}")

def main():
    # Get input source choice
    choice = select_input_source()
    
    if choice == '1':
        # Process files from regular input folder
        process_files(INPUT_FOLDER_NAME)
    else:
        # Process files from flyers directory
        flyer_type = select_flyer_directory()
        if not flyer_type:
            return
        
        date_dir = select_date_directory(flyer_type)
        if not date_dir:
            return
        
        # Construct the full path to the selected flyer directory
        flyer_path = os.path.join(FLYERS_FOLDER_NAME, flyer_type, date_dir)
        process_files(flyer_path, is_flyer=True)

if __name__ == "__main__":
    main()