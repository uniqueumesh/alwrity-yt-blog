import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv
import base64
from ai_generator import summarize_youtube_video
from video_transcriber import get_youtube_transcript, extract_video_id
from ui_components import add_custom_css, create_header, create_info_card, create_status_indicator, create_footer

# Load environment variables from .env file (as fallback)
load_dotenv()

def _get_secret_or_env(var_name: str) -> str:
    """Return value from Streamlit secrets if present, else environment, else empty."""
    try:
        if hasattr(st, 'secrets') and var_name in st.secrets:
            return st.secrets.get(var_name, '')
    except Exception:
        pass
    return os.getenv(var_name, '')

def validate_api_keys(assemblyai_key: str, gemini_key: str):
    """Validate that required API keys are present based on provided or env/secrets."""
    missing_keys = []
    if not assemblyai_key:
        missing_keys.append("ASSEMBLYAI_API_KEY")
    if not gemini_key:
        missing_keys.append("GEMINI_API_KEY")
    return missing_keys

def generate_yt_blog(yt_url, assemblyai_api_key: str, gemini_api_key: str):
    """Generate a blog post from a YouTube video"""
    transcript = get_youtube_transcript(yt_url, assemblyai_api_key)
    if not transcript:
        return None
        
    # Check transcript length
    if len(transcript.split()) < 50:  # Less than 50 words
        st.warning("⚠️ The transcript is very short. The generated blog may not be comprehensive.")
        
    return summarize_youtube_video(transcript, gemini_api_key)

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Alwrity - AI YouTube to Blog Generator",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    add_custom_css()
    
    # Create header
    create_header()
    
    # API Keys Section in Sidebar
    st.sidebar.markdown("### 🔐 API Configuration")
    st.sidebar.markdown("""
    <div style="background: #e3f2fd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <small>🔒 Your API keys are stored securely in your session and are never saved permanently.</small>
    </div>
    """, unsafe_allow_html=True)
    
    # AssemblyAI API Key input (never pre-filled)
    st.sidebar.markdown("#### 🎙️ AssemblyAI (Transcription)")
    assemblyai_input = st.sidebar.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="Enter your AssemblyAI API key",
        help="Get your API key from https://www.assemblyai.com/",
        key="assemblyai_input"
    )
    
    # Resolve effective AssemblyAI key (user input takes precedence, else env/secrets)
    effective_assemblyai_key = assemblyai_input or _get_secret_or_env('ASSEMBLYAI_API_KEY')
    if effective_assemblyai_key:
        st.sidebar.markdown(create_status_indicator("success", "AssemblyAI Connected"), unsafe_allow_html=True)
    else:
        st.sidebar.markdown(create_status_indicator("error", "AssemblyAI Not Connected"), unsafe_allow_html=True)
    
    st.sidebar.markdown("#### 🤖 Google Gemini (AI Generation)")
    gemini_input = st.sidebar.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="Enter your Gemini API key",
        help="Get your API key from https://makersuite.google.com/app/apikey",
        key="gemini_input"
    )
    
    # Resolve effective Gemini key (user input takes precedence, else env/secrets)
    effective_gemini_key = gemini_input or _get_secret_or_env('GEMINI_API_KEY')
    if effective_gemini_key:
        st.sidebar.markdown(create_status_indicator("success", "Gemini Connected"), unsafe_allow_html=True)
    else:
        st.sidebar.markdown(create_status_indicator("error", "Gemini Not Connected"), unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Check for missing API keys (based on effective values)
    missing_keys = validate_api_keys(effective_assemblyai_key, effective_gemini_key)
    if missing_keys:
        create_info_card(
            f"""<h4>🔑 API Keys Required</h4>
            <p>Please configure the following API keys in the sidebar:</p>
            <ul>
            {''.join([f'<li><strong>{key}</strong></li>' for key in missing_keys])}
            </ul>""", 
            "warning"
        )
        
        # Create two columns for API key information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🎙️ AssemblyAI Setup
            1. Visit [AssemblyAI](https://www.assemblyai.com/)
            2. Create a free account
            3. Get your API key from the dashboard
            4. Paste it in the sidebar
            
            **Features:** High-quality transcription with language detection
            """)
        
        with col2:
            st.markdown("""
            #### 🤖 Google Gemini Setup
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Generate a new API key
            4. Paste it in the sidebar
            
            **Features:** Advanced AI for blog content generation
            """)
        
        return
    
    # Main content area
    st.markdown("### 🎯 Convert YouTube Video to Blog")
    
    # Create input section with better styling
    with st.container():
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 2rem; border-radius: 15px; margin: 1rem 0; 
                    border: 1px solid #dee2e6;">
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📹 Enter YouTube Video URL")
        
        # URL input with validation
        yt_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            help="📝 Paste any YouTube video URL here. Supports all YouTube URL formats.",
            label_visibility="collapsed"
        )
        
        # URL validation feedback
        if yt_url:
            video_id = extract_video_id(yt_url)
            if video_id:
                st.success(f"✅ Valid YouTube URL detected (Video ID: {video_id})")
            else:
                st.error("❌ Invalid YouTube URL format. Please check your URL.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Pro tips section
    with st.expander("💡 Pro Tips for Better Results", expanded=False):
        st.markdown("""
        **🎯 For best results:**
        - Choose videos with clear audio and speech
        - Educational or tutorial content works exceptionally well
        - Videos between 5-30 minutes are optimal
        - Avoid videos with too much background music
        
        **📊 Supported content:**
        - Tutorials and how-to videos
        - Interviews and podcasts
        - Educational content
        - Product reviews
        - Webinars and presentations
        """)
    
    # Generate button with enhanced styling
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_clicked = st.button(
            "🚀 Generate Blog Post", 
            type="primary", 
            use_container_width=True,
            disabled=not yt_url or not extract_video_id(yt_url) if yt_url else True
        )
    
    # Processing and results
    if generate_clicked:
        if not yt_url:
            st.error("Please enter a YouTube URL.")
        else:
            # Create a results container
            results_container = st.container()
            
            with results_container:
                with st.spinner("🔄 Processing your request..."):
                    blog_content = generate_yt_blog(yt_url, effective_assemblyai_key, effective_gemini_key)
                    
                if blog_content:
                    # Success message with animation
                    st.balloons()
                    create_info_card(
                        "<h4>🎉 Success!</h4><p>Your blog post has been generated successfully!</p>",
                        "success"
                    )
                    
                    # Display the blog content in a nice container
                    st.markdown("---")
                    st.markdown("## 📝 Generated Blog Post")
                    
                    # Blog content display
                    with st.container():
                        st.markdown("""
                        <div style="background: white; padding: 2rem; border-radius: 10px; 
                                    border: 1px solid #e9ecef; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                        """, unsafe_allow_html=True)
                        
                        st.markdown(blog_content)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Action buttons
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 1, 1])
                    
                    with col1:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            # JavaScript to copy to clipboard
                            st.markdown("""
                            <script>
                            navigator.clipboard.writeText(`{}`).then(function() {{
                                console.log('Content copied to clipboard');
                            }});
                            </script>
                            """.format(blog_content.replace('`', '\\`')), unsafe_allow_html=True)
                            st.success("Content copied to clipboard!")
                    
                    with col2:
                        # Download as text file
                        st.download_button(
                            label="💾 Download as TXT",
                            data=blog_content,
                            file_name="youtube_blog_post.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Download as markdown
                        st.download_button(
                            label="📄 Download as MD",
                            data=blog_content,
                            file_name="youtube_blog_post.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    # Raw content for manual copying
                    with st.expander("📋 Raw Content (for manual copying)"):
                        st.text_area(
                            "Blog content:",
                            value=blog_content,
                            height=300,
                            help="Select all (Ctrl+A) and copy (Ctrl+C) this content.",
                            label_visibility="collapsed"
                        )
                else:
                    create_info_card(
                        "<h4>❌ Generation Failed</h4><p>Unable to generate blog content. Please check your YouTube URL and API keys.</p>",
                        "error"
                    )

    # Add footer with enhanced styling
    create_footer()

if __name__ == "__main__":
    main()
