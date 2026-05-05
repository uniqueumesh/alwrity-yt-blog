import time
from google import genai
from google.genai import types
import streamlit as st

def summarize_youtube_video(yt_transcript, gemini_api_key: str):
    """Use Gemini AI to transform transcript into a blog post"""
    # Truncate transcript if it's too long for the model
    max_transcript_length = 25000  # Characters
    if len(yt_transcript) > max_transcript_length:
        st.warning(f"⚠️ Transcript is very long ({len(yt_transcript)} characters). Truncating to {max_transcript_length} characters.")
        yt_transcript = yt_transcript[:max_transcript_length] + "..."
    
    prompt = f'''
    You are an expert content writer specializing in digital content writing. I will provide you with a transcript.
    Your task is to transform a given transcript into a well-formatted and informative blog article.

    Please follow the below guidelines:
    1. Master the Transcript: Understand main ideas, key points, and the core message.
    2. Sentence Structure: Rephrase while preserving logical flow and coherence. Don't quote anyone from video.
    3. Write Unique Content: Avoid direct copying; rewrite in your own words.
    4. REMEMBER to avoid direct quoting and maintain uniqueness.
    5. Proofread: Check for grammar, spelling, and punctuation errors.
    6. Use Creative and Human-like Style: Incorporate contractions, idioms, transitional phrases, interjections, and colloquialisms.
    7. Ensure Uniqueness: Guarantee the article is plagiarism-free.
    8. Punctuation: Use appropriate question marks at the end of questions.
    9. Pass AI Detection Tools: Create content that easily passes AI plagiarism detection tools.
    10. Rephrase words like 'video, youtube, channel' with 'article, blog' and such suitable words.

    Make sure that your response is well formatted, with headings, lists, bullet points etc. Respond in markdown style.
    Follow above guidelines to craft a blog content from the following transcript:

    Transcript: {yt_transcript}
    '''
    
    try:
        response = generate_text_with_exception_handling(prompt, gemini_api_key)
        return response
    except Exception as err:
        st.error(f"Failed to get response from LLM: {str(err)}")
        return None

def generate_text_with_exception_handling(prompt, gemini_api_key: str):
    """
    Generate text using Gemini 2.5 series AI with robust error handling, retries, and model fallback.
    
    Fallback Behavior:
    1. Primary: gemini-2.5-flash-lite
    2. Secondary: gemini-2.5-flash
    3. Tertiary: gemini-2.5-pro
    """
    api_key = gemini_api_key
    if not api_key:
        st.error("Gemini API key not set. Please set it in the API Keys section.")
        return None
        
    try:
        client = genai.Client(api_key=api_key)
        
        config = types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=4096,
            safety_settings=[
                types.SafetySetting(category='HARM_CATEGORY_HARASSMENT', threshold='BLOCK_MEDIUM_AND_ABOVE'),
                types.SafetySetting(category='HARM_CATEGORY_HATE_SPEECH', threshold='BLOCK_MEDIUM_AND_ABOVE'),
                types.SafetySetting(category='HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold='BLOCK_MEDIUM_AND_ABOVE'),
                types.SafetySetting(category='HARM_CATEGORY_DANGEROUS_CONTENT', threshold='BLOCK_MEDIUM_AND_ABOVE'),
            ]
        )
        
        models_to_try = [
            "gemini-2.5-flash-lite", 
            "gemini-2.5-flash", 
            "gemini-2.5-pro"
        ]
        
        for model_name in models_to_try:
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    with st.spinner(f"Generating content with {model_name}..."):
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=config
                        )
                        
                        if response.text:
                            return response.text
                            
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "overloaded" in error_msg.lower():
                        if attempt < max_retries:
                            time.sleep(2)
                            continue
                    
                    if model_name == models_to_try[-1] and attempt == max_retries:
                        raise e
                    
                    st.warning(f"Model {model_name} failed: {error_msg}. Trying next 2.5 model...")
                    break
                    
        return None
            
    except Exception as e:
        st.error(f"Error generating text with Gemini 2.5: {str(e)}")
        return None