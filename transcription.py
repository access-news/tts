from openai import OpenAI, OpenAIError
from dotenv import load_dotenv # Required for loading your OpenAI_API_KEY in .env
import base64
from pdf2image import convert_from_path
from io import BytesIO
from PIL import Image
import os

load_dotenv()
client = OpenAI() # instantiate OpenAI client, API key will be found in .env file

INPUT_FOLDER_NAME = "input"

system_message = {
    "role": "system",
    "content": (
        """You are an expert transcriptionist, specializing in transcribing unstructured data into easily readable, structured text. 
        This text will be read directly by a text-to-speech model.
        Ensure that your transcribed text maintains the structure of the data but is suitable for a TTS model."""
    )
}

def pdf_to_base64_images(pdf_path):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Store base64 encoded images in a list
    base64_images = []
    
    for image in images:
        # Save the image in memory as a BytesIO object
        buffered = BytesIO()
        image.save(buffered, format="PNG")  # Save image as PNG format
        
        # Convert the image to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Append the base64 string of the image to the list
        base64_images.append(img_base64)
    
    return base64_images

def image_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Convert the image to a byte array in PNG format
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        # Encode the byte array to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return img_base64

def transcribe():
    transcriptions = []  # Array to hold all transcription results
    base64_urls = []

    # Traverse through each file in the input folder
    for filename in os.listdir(INPUT_FOLDER_NAME):
        file_path = os.path.join(INPUT_FOLDER_NAME, filename)

        if filename.endswith(".pdf"):
            # Convert PDF to base64 images
            base64_images = pdf_to_base64_images(file_path)
            base64_urls.append(base64_images)  # Add as a list of images
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Convert image to base64
            base64_image = image_to_base64(file_path)
            base64_urls.append([base64_image])  # Add as a list with one image

    # Initialize the system message for each request
    for base64_image_list in base64_urls:
        messages = [system_message]  # Start with system message

        # Construct user message with all images in a single PDF or standalone image
        user_messages = [
            {"role": "user", "content": [
                {"type": "text", "text": "Transcribe the image/s into TTS-readable text. Ensure structure and meaning is conveyed."}
            ]}
        ]

        for image_base64 in base64_image_list:
            user_messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}",
                }
            })

        # Add the user messages to the conversation
        messages.extend(user_messages)

        try:
            # Send the message to the GPT model
            completion = client.chat.completions.create(
                model="gpt-4o",
                temperature=0,
                messages=messages,
            )
            # Get the transcription result
            transcription_result = completion.choices[0].message.content
            # Add the result to the transcriptions array
            transcriptions.append(transcription_result)

        except OpenAIError as e:
            print(f"Error in transcription: {e}")
            transcriptions.append(f"Error in transcription")

    return transcriptions