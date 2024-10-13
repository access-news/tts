from transcription import transcribe
from openai import OpenAI
from pathlib import Path
import os

# Initialize the OpenAI client
client = OpenAI()

# Define input and output folder names
INPUT_FOLDER_NAME = "input"
OUTPUT_FOLDER_NAME = "output"

def main():
    # Ensure the output folder exists
    os.makedirs(OUTPUT_FOLDER_NAME, exist_ok=True)

    # Get transcriptions
    transcriptions = transcribe()

    # Get the list of input filenames
    input_files = [f for f in os.listdir(INPUT_FOLDER_NAME) if f.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))]

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

if __name__ == "__main__":
    main()