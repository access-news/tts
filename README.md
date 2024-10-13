# Image and PDF to Speech Converter

This project converts images and PDF files into speech using OpenAI's GPT-4o for transcription and TTS-1 for text-to-speech conversion. It's designed to take unstructured visual data and turn it into easily understandable audio content.

## Features

- Supports both image (.png, .jpg, .jpeg) and PDF input files
- Uses GPT-4o to transcribe and describe the content of images and PDFs
- Converts transcriptions to speech using OpenAI's TTS-1 model
- Outputs MP3 audio files

## Prerequisites

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/access-news/tts.git
   cd tts
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Place your input files (images or PDFs) in the `input` folder.

2. Run the main script:
   ```
   python main.py
   ```

3. The script will process each file in the `input` folder and generate corresponding MP3 files in the `output` folder.

## Project Structure

- `main.py`: The main script that orchestrates the conversion process.
- `transcription.py`: Contains functions for transcribing images and PDFs using GPT-4 Vision.
- `input/`: Folder for input files (images and PDFs).
- `output/`: Folder where generated MP3 files are saved.
- `requirements.txt`: List of Python dependencies.

## How It Works

1. The script reads files from the `input` folder.
2. For each file:
   - If it's a PDF, it's converted to images.
   - The image(s) are encoded to base64.
   - GPT-4o is used to transcribe and describe the content.
   - The transcription is converted to speech using OpenAI's TTS-1 model.
   - The resulting audio is saved as an MP3 file in the `output` folder.

## Notes

- The system is designed to add context and description to the transcriptions, making them more suitable for audio consumption.
- The TTS model uses the "nova" voice, but this can be changed in the `main.py` file.

## Limitations

- Large PDF files may take longer to process due to the conversion to images.
- The quality of transcription and description depends on the clarity and complexity of the input images.