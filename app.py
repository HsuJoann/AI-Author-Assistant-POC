import streamlit as st
import os
import json
from datetime import datetime
from loguru import logger
from ai_service import AIService
from config import DOCUMENTS_DIR

def initialize_session_state():
    """Initialize session state variables"""
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'current_document' not in st.session_state:
        st.session_state.current_document = {'title': '', 'content': ''}
    if 'ai_feedback' not in st.session_state:
        st.session_state.ai_feedback = ''

def create_directories():
    """Ensure required directories exist"""
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    logger.info(f"Ensured directory exists: {DOCUMENTS_DIR}")

def load_documents():
    """Load all documents from filesystem"""
    documents = []
    try:
        for file in os.listdir(DOCUMENTS_DIR):
            if file.endswith('.json'):
                with open(os.path.join(DOCUMENTS_DIR, file), 'r') as f:
                    metadata = json.load(f)
                    with open(os.path.join(DOCUMENTS_DIR, f"{metadata['filename']}.md"), 'r') as content_file:
                        content = content_file.read()
                        documents.append({**metadata, "content": content})
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        return []

def save_document(title: str, content: str) -> bool:
    """Save document to filesystem"""
    try:
        filename = f"{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save content
        with open(os.path.join(DOCUMENTS_DIR, f"{filename}.md"), 'w') as f:
            f.write(content)
        
        # Save metadata
        metadata = {
            "title": title,
            "created_at": datetime.now().isoformat(),
            "filename": filename
        }
        with open(os.path.join(DOCUMENTS_DIR, f"{filename}.json"), 'w') as f:
            json.dump(metadata, f)
            
        logger.info(f"Saved document: {title}")
        return True
    except Exception as e:
        logger.error(f"Error saving document: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="Simple Author Assistant", layout="wide")
    
    # Initialize session state and directories
    initialize_session_state()
    create_directories()
    
    # Initialize AI Service
    ai_service = AIService()

    # Header
    st.title("💡 Simple Author Assistant")
    st.markdown("---")

    # Main layout
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader("📝 Document Editor")
        title = st.text_input("Document Title", key="doc_title")
        content = st.text_area("Content", height=300, key="doc_content")
        
        col1_1, col1_2, col1_3 = st.columns([1, 1, 1])
        with col1_1:
            if st.button("💾 Save Document", use_container_width=True):
                if title and content:
                    if save_document(title, content):
                        st.success("Document saved successfully!")
                        st.session_state.documents = load_documents()
                    else:
                        st.error("Error saving document")
                else:
                    st.warning("Please provide both title and content")

    with col2:
        st.subheader("🤖 AI Assistant")
        if content:
            if st.button("✨ Improve Writing", use_container_width=True):
                with st.spinner("Getting suggestions..."):
                    improved = ai_service.improve_writing(content)
                    st.text_area("Improved Version", improved, height=200)
            
            if st.button("🔍 Analyze Content", use_container_width=True):
                with st.spinner("Analyzing..."):
                    analysis = ai_service.analyze_content(content)
                    st.info("Analysis Results")
                    st.markdown(analysis)

    # Document List
    st.markdown("---")
    st.subheader("📚 Your Documents")
    
    # Load and display documents
    documents = load_documents()
    for doc in documents:
        with st.expander(f"📄 {doc['title']} - {doc['created_at'][:10]}"):
            st.markdown(doc['content'])
            if st.button("📝 Edit", key=f"edit_{doc['filename']}"):
                st.session_state.current_document = doc
                st.experimental_rerun()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")