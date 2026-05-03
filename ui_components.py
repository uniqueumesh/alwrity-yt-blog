import streamlit as st

def add_custom_css():
    """Add custom CSS for better styling"""
    st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
        text-align: center; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .header-subtitle { font-size: 1.2rem; opacity: 0.9; margin-bottom: 0; }
    .info-card {
        background: #f8f9fa; padding: 1.5rem; border-radius: 10px;
        border-left: 4px solid #667eea; margin: 1rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .success-card { background: #d4edda; border-left-color: #28a745; color: #155724; }
    .warning-card { background: #fff3cd; border-left-color: #ffc107; color: #856404; }
    .error-card { background: #f8d7da; border-left-color: #dc3545; color: #721c24; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border: none; border-radius: 25px; padding: 0.75rem 2rem;
        font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4); }
    .stTextInput > div > div > input { border-radius: 10px; border: 2px solid #e9ecef; padding: 0.75rem; transition: all 0.3s ease; }
    .stTextInput > div > div > input:focus { border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
    .stProgress > div > div > div > div { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
    .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
    .status-success { background-color: #28a745; }
    .status-error { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create an attractive header section"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🎬 Alwrity</div>
        <div class="header-subtitle">Transform YouTube Videos into Engaging Blog Posts with AI</div>
    </div>
    """, unsafe_allow_html=True)

def create_info_card(content, card_type="info"):
    """Create styled info cards"""
    card_class = f"info-card {card_type}-card" if card_type != "info" else "info-card"
    st.markdown(f"""
    <div class="{card_class}">{content}</div>
    """, unsafe_allow_html=True)

def create_status_indicator(status, text):
    """Create status indicators with colored dots"""
    status_class = f"status-{status}"
    return f'<span class="status-indicator {status_class}"></span>{text}'

def create_footer():
    """Add footer with enhanced styling"""
    st.markdown("<br><br>---", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; text-align: center; 
                color: white; margin-top: 2rem;">
        <h4 style="margin-bottom: 1rem; color: white;">🚀 Alwrity - AI Content Generator</h4>
        <p style="margin-bottom: 1rem; opacity: 0.9;">Transform your YouTube content into engaging blog posts with the power of AI</p>
        <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
            <small>Made with ❤️ by ALwrity team • Powered by AssemblyAI & Google Gemini</small>
        </div>
    </div>
    """, unsafe_allow_html=True)