import os
import time
import requests
import streamlit as st
import re
import yt_dlp
# Global variable to store ffmpeg path
FFMPEG_PATH = None

try:
    from static_ffmpeg import add_paths as ffmpeg_add_paths
    import static_ffmpeg.run as ffmpeg_run
    # This adds FFmpeg to the system path
    ffmpeg_add_paths()
    # Get the actual folder path where ffmpeg is located
    FFMPEG_PATH = os.path.dirname(ffmpeg_run.get_platform_executables_root())
except Exception:
    pass

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
    # Use absolute path for cloud reliability, yt-dlp will handle the extension
    temp_audio_base = os.path.join(os.getcwd(), 'temp_audio')
    temp_audio_mp3 = f"{temp_audio_base}.mp3"
    
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
            status.update(label="Downloading audio from YouTube using yt-dlp...")
            
            # yt-dlp options for high quality and bypassing bot detection
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': temp_audio_base + '.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
            
            # Explicitly tell yt-dlp where ffmpeg is located (Fix for Windows)
            if FFMPEG_PATH:
                ydl_opts['ffmpeg_location'] = FFMPEG_PATH

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(clean_url, download=True)
                    video_title = info.get('title', 'Unknown Title')
                    video_length = info.get('duration', 0)
                    
                    if video_title != "Unknown Title":
                        st.info(f"📹 Video: {video_title} ({video_length//60}:{video_length%60:02d})")
                
                # Verify the download
                if not os.path.exists(temp_audio_mp3):
                    st.error("Audio file was not downloaded correctly by yt-dlp.")
                    return None
                    
                if os.path.getsize(temp_audio_mp3) < 1000:  # Less than 1KB
                    st.error("Downloaded audio file is too small to be valid.")
                    if os.path.exists(temp_audio_mp3): os.remove(temp_audio_mp3)
                    return None
                    
                status.update(label="Uploading audio to transcription service...")
                # Upload audio file to AssemblyAI
                try:
                    with open(temp_audio_mp3, "rb") as f:
                        response = requests.post(
                            f"{base_url}/v2/upload",
                            headers={"authorization": ASSEMBLYAI_API_KEY},
                            data=f
                        )
                except Exception as upload_error:
                    st.error(f"Error uploading to AssemblyAI: {str(upload_error)}")
                    if os.path.exists(temp_audio_mp3): os.remove(temp_audio_mp3)
                    return None
                    
                # Clean up temp file immediately after upload
                if os.path.exists(temp_audio_mp3):
                    os.remove(temp_audio_mp3)
                    
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