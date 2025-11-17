import streamlit as st

def apply_custom_styles():
    """Apply VS Code dark theme styling to the Streamlit app"""
    st.markdown("""
        <style>
        /* Dark background like VS Code */
        .stApp {
            background-color: #1e1e1e;
        }
        
        /* Container styling */
        .main .block-container {
            background-color: #252526;
            padding: 2rem;
            max-width: 1200px;
        }
        
        /* Title styling */
        h1 {
            color: #d4d4d4;
            text-align: center;
            font-weight: 700;
            padding-bottom: 1rem;
            border-bottom: 2px solid #3e3e42;
            margin-bottom: 1.5rem;
        }
        
        h2, h3 {
            color: #d4d4d4;
            font-weight: 600;
        }
        
        /* Regular text */
        p, label, div {
            color: #d4d4d4;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #2d2d30;
            padding: 0.5rem;
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
            border-radius: 6px;
            padding: 0.5rem 1rem;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #3e3e42;
            color: #ffffff;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #3c3c3c;
            color: #ffffff;
            border: 1px solid #6e6e6e;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #0e639c;
            color: #ffffff;
            border: 1px solid #007acc;
        }
        
        .stButton > button:hover {
            background-color: #1177bb;
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #3e3e42;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border: 1px solid #007acc;
        }
        
        /* Labels */
        .stTextInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stFileUploader > label {
            color: #d4d4d4;
        }
        
        /* File uploader */
        .stFileUploader > div {
            border: 1px dashed #3e3e42;
            background-color: #2d2d30;
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            background-color: #3c3c3c;
            border: 1px solid #3e3e42;
            color: #d4d4d4;
        }
        
        /* Alerts */
        .stSuccess {
            background-color: #1e3a1e;
            border: 1px solid #4ec9b0;
            color: #d4d4d4;
        }
        
        .stWarning {
            background-color: #3a3a1e;
            border: 1px solid #dcdcaa;
            color: #d4d4d4;
        }
        
        .stError {
            background-color: #3a1e1e;
            border: 1px solid #f48771;
            color: #d4d4d4;
        }
        
        .stInfo {
            background-color: #1e2a3a;
            border: 1px solid #569cd6;
            color: #d4d4d4;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #2d2d30;
            border: 1px solid #3e3e42;
            color: #d4d4d4;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #3e3e42;
        }
        
        /* Progress bar */
        .stProgress > div > div > div > div {
            background-color: #007acc;
        }
        
        /* Markdown text */
        .stMarkdown {
            color: #d4d4d4;
        }
        
        /* Text areas */
        textarea {
            color: #d4d4d4 !important;
            background-color: #3c3c3c !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #252526;
        }
        
        /* Code blocks */
        code {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        </style>
    """, unsafe_allow_html=True)