import requests
from pydub import AudioSegment
import tempfile
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
load_dotenv()
# Configure Google API for audio summarization
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# List to store temporary file paths
temp_files = []

def summarize_audio(audio_file_path,description_file_path):
    """Understand the audio file, get the relevant piece of information from the audio, and present that information in a generalized statement format."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    
    with open(description_file_path, 'r') as file:
        description = file.read()
    response = model.generate_content(
        [
            description,
            audio_file
        ]
    )
    return response.text

def make_title(audio_file_path,description_file_path):
    """Generate a title for the audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    
    
    with open(description_file_path, 'r') as file:
        description = file.read()
    response = model.generate_content(
        [
            description,
            audio_file
        ]
    )
    return response.text

def download_and_convert_to_mp3(url):
    """Download the MP4 file from the given URL, convert it to MP3, and save it to a temporary file."""
    try:
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Save the downloaded MP4 to a temporary file
        temp_mp4_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        with open(temp_mp4_file.name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        temp_files.append(temp_mp4_file.name)  # Add to temp files list for cleanup
        
        # Convert MP4 to MP3
        temp_mp3_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        audio = AudioSegment.from_file(temp_mp4_file.name, format="mp4")
        audio.export(temp_mp3_file.name, format="mp3")
        temp_files.append(temp_mp3_file.name)  # Add to temp files list for cleanup

        return temp_mp3_file.name
    except Exception as e:
        print(f"Error downloading or converting file: {e}")
        return None

def cleanup_temp_files():
    """Delete all temporary files."""
    for file_path in temp_files :
        try:
            os.remove(file_path)
            print(f"Deleted temp file: {file_path}")
        except Exception as e:
            print(f"Error deleting temp file {file_path}: {e}")

def main():
    # URL of the video file
    
    file_url = input("enter the video url")
    
    # Download the file from the URL and convert it to MP3
    
    print('Downloading ...')
    downloading_time_start = time.time()
    audio_file_path = download_and_convert_to_mp3(file_url)
    if not audio_file_path:
        print("Failed to download and convert file. Exiting...")
        return
    downloading_time_end = time.time()
    downloading_time = downloading_time_end-downloading_time_start
    
    
    # Summarize audio
    print('Making description ...')
    summary_description = "summary_description.txt"
    title_description = "title_description.txt"
    
    summarizing_time_start = time.time()
    summary_text = summarize_audio(audio_file_path,summary_description)
    summarizing_time_end = time.time()
    summarizing_time = summarizing_time_end-summarizing_time_start
    
    print("Summary:")
    print(summary_text)

    # Make title
    print('Making title...')
    
    titleing_time_start = time.time()
    title = make_title(audio_file_path,title_description)
    titleing_time_end = time.time()
    titleing_time = titleing_time_end-titleing_time_start
    print("Title:")
    print(title)

    print("Download Time",downloading_time)
    print("Describing Time",summarizing_time)
    print("Title Creating Time ",titleing_time)
    
    total_time=downloading_time+summarizing_time+titleing_time
    
    print(total_time)
    # Clean up temporary files
    cleanup_temp_files()

if __name__ == "__main__":
    main()
