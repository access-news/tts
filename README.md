# Image and PDF to Speech Converter

This project converts images and PDF files into speech using OpenAI's GPT-4o for transcription and TTS-1 for text-to-speech conversion. It's designed to take unstructured visual data and turn it into easily understandable audio content, with special support for automated flyer processing.

## Features

- Supports both image (.png, .jpg, .jpeg) and PDF input files
- Uses GPT-4o to transcribe and describe the content of images and PDFs
- Converts transcriptions to speech using OpenAI's TTS-1 model
- Outputs MP3 audio files
- Automated flyer processing with date-based organization
- Support for multiple flyer sources (e.g., Target Weekly Ad)

## Prerequisites

- Python 3.7+
- OpenAI API key
- Chrome or Firefox browser (for Selenium)
- ChromeDriver or GeckoDriver (for Selenium)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/access-news/tts.git
cd tts
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Install Selenium and WebDriver dependencies:

For Chrome:
```bash
# Install Chrome WebDriver
pip install webdriver-manager
```

For Firefox:
```bash
# Install Firefox GeckoDriver
# On Ubuntu/Debian:
sudo apt-get install firefox-geckodriver
# On macOS with Homebrew:
brew install geckodriver
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

```
project/
├── main.py              # Main script for processing files
├── transcription.py     # Handles image/PDF transcription
├── input/              # Regular input folder for files
├── output/             # Output folder for MP3 files
├── flyers/             # Root folder for flyer processing
│   └── target_weekly_ad/  # Example flyer source
│       └── YYYYMMDD/      # Date-based folders
└── requirements.txt    # Python dependencies
```

## Usage

### Regular File Processing

1. Place your input files (images or PDFs) in the `input` folder.
2. Run the main script:
```bash
python main.py
```
3. Select option 1 when prompted for input source.
4. The script will process each file and generate corresponding MP3 files in the `output` folder.

### Flyer Processing

1. Ensure the proper folder structure exists under `flyers/`:
```
flyers/
└── target_weekly_ad/
    └── YYYYMMDD/
        └── [image files]
```
2. Run the main script:
```bash
python main.py
```
3. Select option 2 when prompted for input source.
4. Choose the flyer type (e.g., target_weekly_ad).
5. Select the date folder to process.

## How It Works

### Regular Processing

1. The script reads files from the `input` folder.
2. For each file:
   - If it's a PDF, it's converted to images.
   - The image(s) are encoded to base64.
   - GPT-4o is used to transcribe and describe the content.
   - The transcription is converted to speech using OpenAI's TTS-1 model.
   - The resulting audio is saved as an MP3 file in the `output` folder.

### Flyer Processing

1. Flyers are organized by source and date in the `flyers` directory.
2. Each flyer source (e.g., target_weekly_ad) has its own directory.
3. Within each source directory, flyers are organized by date (YYYYMMDD format).
4. The script processes all images in the selected date folder.
5. Generated audio files are saved in the `output` folder.

### Automated Flyer Download

The project includes support for automated flyer downloading using Selenium:
1. Selenium automates the browser to navigate to flyer websites
2. Downloads are organized by date in the appropriate flyer source folder

## Notes

- The system is designed to add context and description to the transcriptions, making them more suitable for audio consumption.
- The TTS model uses the "nova" voice, but this can be changed in the `main.py` file.
- Flyer processing is organized by date to maintain historical records.
- Selenium automation helps maintain up-to-date flyer content.

## Limitations

- Large PDF files may take longer to process due to the conversion to images.
- The quality of transcription and description depends on the clarity and complexity of the input images.
- Automated flyer downloads may break if websites change their structure.
- Selenium requires proper WebDriver setup and maintenance.

## Troubleshooting

### Selenium Issues

If you encounter issues with Selenium:

1. Check WebDriver compatibility:
```bash
# For Chrome, check versions
google-chrome --version
chromedriver --version

# For Firefox, check versions
firefox --version
geckodriver --version
```

2. Update WebDriver if needed:
```bash
# For Chrome
webdriver-manager update

# For Firefox
# Update through your package manager
```

3. Common Selenium errors:
- "WebDriver not found": Ensure the correct WebDriver is installed and in your PATH
- "Version mismatch": Update WebDriver to match your browser version
- "Browser not found": Verify browser installation and PATH settings

### Processing Issues

- For memory issues with large files, try processing fewer files at once

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## API Documentation

### Endpoints

#### Convert Files to Speech
`POST /convert`

Converts images or PDFs to speech audio. Accepts file uploads, base64-encoded data, or URLs.

**Request Body:**
- Multipart form data with file upload:
  ```
  file: [binary file data]
  ```
- OR JSON with base64 data:
  ```
  {
    "base64": "base64_encoded_string"
  }
  ```
- OR JSON with URL:
  ```
  {
    "url": "https://example.com/image.jpg"
  }
  ```

**Supported File Types:**
- Images: .png, .jpg, .jpeg
- Documents: .pdf

**Response:**
```
{
    "audio": "base64_encoded_audio",
    "message": "Conversion successful"
}
```

**Error Response:**
```
{
    "error": "Error message description"
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (invalid file type, missing file)
- 500: Server error

#### Fetch Target Weekly Ads
`GET /fetch-target-ads`

Fetches the latest Target weekly advertisements, processes them, and returns base64-encoded audio for each ad.

**Response:**
```
{
    "message": "Target ads fetched and processed successfully",
    "date": "20240320",
    "audio_files": [
        {
            "filename": "target_ad_1.jpg",
            "audio": "base64_encoded_audio_string"
        },
        {
            "filename": "target_ad_2.jpg",
            "audio": "base64_encoded_audio_string"
        }
        // ... more files
    ]
}
```

**Error Response:**
```
{
    "error": "Error message description"
}
```

**Status Codes:**
- 200: Success
- 404: No ads found
- 500: Server error

### Example Usage

**Converting a File:**
```bash
curl -X POST -F "file=@image.png" http://127.0.0.1:5000/convert
```

**Converting from URL:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"url":"https://example.com/image.jpg"}' \
     http://127.0.0.1:5000/convert
```

**Converting Base64 Data:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"base64":"base64_encoded_string"}' \
     http://127.0.0.1:5000/convert
```

**Fetching Target Ads:**
```bash
curl http://127.0.0.1:5000/fetch-target-ads
```
