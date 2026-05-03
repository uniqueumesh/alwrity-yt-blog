import os
import time
import requests
import streamlit as st
import re
from pytubefix import YouTube

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats"""
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_match = re.match(youtube_regex, url)
    if youtube_match:
        return youtube_match.group(6)
    return None

def get_youtube_transcript(yt_url, assemblyai_api_key: str):
    """Extract transcript from YouTube video using AssemblyAI"""
    ASSEMBLYAI_API_KEY = assemblyai_api_key
    if not ASSEMBLYAI_API_KEY:
        st.error("AssemblyAI API key not set. Please set it in the API Keys section.")
        return None
        
    base_url = "https://api.assemblyai.com"
    headers = {"authorization": ASSEMBLYAI_API_KEY, "content-type": "application/json"}
    # Use absolute path for cloud reliability
    temp_audio = os.path.join(os.getcwd(), 'temp_audio.mp4')
    
    try:
        if not yt_url:
            st.error("Please enter a YouTube URL.")
            return None
            
        video_id = extract_video_id(yt_url)
        if not video_id:
            st.error("Invalid YouTube URL format. Please enter a valid YouTube URL.")
            return None
            
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
            
        with st.status("Processing YouTube video...") as status:
            status.update(label="Downloading audio from YouTube...")
            try:
                try:
                    yt = YouTube(clean_url, use_oauth=False, allow_oauth_cache=True)
                except Exception:
                    yt = YouTube(clean_url)
                
                try:
                    video_title = yt.title
                    video_length = yt.length
                except Exception as e:
                    st.warning(f"Could not get video metadata: {str(e)}. Continuing anyway...")
                    video_title = "Unknown Title"
                    video_length = 0
                
                if video_length > 1800:
                    st.warning(f"⚠️ Video is {video_length//60} minutes long. Processing may take a while.")
                
                if video_title != "Unknown Title":
                    st.info(f"📹 Video: {video_title} ({video_length//60}:{video_length%60:02d})")
                
                audio_stream = None
                stream_attempts = [
                    lambda: yt.streams.filter(only_audio=True, file_extension='mp4').first(),
                    lambda: yt.streams.filter(only_audio=True, file_extension='webm').first(),
                    lambda: yt.streams.filter(only_audio=True).first(),
                    lambda: yt.streams.filter(progressive=True).first(),
                    lambda: yt.streams.first()
                ]
                
                for attempt in stream_attempts:
                    try:
                        audio_stream = attempt()
                        if audio_stream:
                            if hasattr(audio_stream, 'subtype') and audio_stream.subtype:
                                temp_audio = f'temp_audio.{audio_stream.subtype}'
                            break
                    except Exception:
                        continue
                
                if not audio_stream:
                    st.error("YouTube blocked the download or no audio stream found. This is common on cloud hosting.")
                    return None
                    
                try:
                    audio_stream.download(filename=temp_audio, timeout=60)
                except Exception:
                    try:
                        audio_stream.download(output_path=".", filename=temp_audio)
                    except Exception as alt_error:
                        st.error(f"Download failed: {str(alt_error)}")
                        return None
                
                if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) < 1000:
                    st.error("Audio download failed or file is invalid.")
                    if os.path.exists(temp_audio): os.remove(temp_audio)
                    return None
                    
                status.update(label="Uploading to AssemblyAI...")
                with open(temp_audio, "rb") as f:
                    response = requests.post(f"{base_url}/v2/upload", headers={"authorization": ASSEMBLYAI_API_KEY}, data=f)
                
                if os.path.exists(temp_audio): os.remove(temp_audio)
                    
                if response.status_code != 200:
                    st.error(f"Upload error: {response.text}")
                    return None
                    
                upload_url = response.json().get("upload_url")
                
                status.update(label="Requesting transcription...")
                transcript_request = {"audio_url": upload_url, "language_detection": True, "speech_model": "universal"}
                transcript_response = requests.post(f"{base_url}/v2/transcript", json=transcript_request, headers=headers)
                
                transcript_id = transcript_response.json().get('id')
                polling_endpoint = f"{base_url}/v2/transcript/{transcript_id}"
                
                status.update(label="Transcribing audio...")
                progress_bar = st.progress(0)
                start_time = time.time()
                estimated_time = max(video_length * 0.5, 30)
                
                while True:
                    polling_response = requests.get(polling_endpoint, headers=headers)
                    transcription_result = polling_response.json()
                    status_value = transcription_result.get('status')
                    
                    elapsed = time.time() - start_time
                    progress_bar.progress(min(elapsed / estimated_time, 0.95))
                    
                    if status_value == 'completed':
                        progress_bar.progress(1.0)
                        status.update(label="Done!", state="complete")
                        return transcription_result.get('text')
                    elif status_value == 'error':
                        st.error(f"Transcription failed: {transcription_result.get('error')}")
                        return None
                    time.sleep(3)
                        
            except Exception as e:
                st.error(f"Processing error: {str(e)}")
                return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        if os.path.exists(temp_audio): os.remove(temp_audio)
        return None