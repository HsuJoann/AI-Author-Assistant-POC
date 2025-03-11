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
        st.session_state.current_document = {
            'title': '',
            'description': '',
            'keywords': [],
            'chapters': [],
            'created_at': '',
            'updated_at': ''
        }
    if 'current_chapter' not in st.session_state:
        st.session_state.current_chapter = {
            'title': '',
            'sections': []
        }
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
                with open(os.path.join(DOCUMENTS_DIR, file), 'r', encoding='utf-8') as f:
                    document = json.load(f)
                    documents.append(document)
        logger.info(f"Loaded {len(documents)} documents")
        return documents
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        return []

def save_document(doc_data: dict) -> bool:
    """Save document to filesystem"""
    try:
        filename = f"{doc_data['title'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare document structure
        document = {
            "title": doc_data['title'],
            "description": doc_data['description'],
            "keywords": doc_data['keywords'],
            "chapters": doc_data['chapters'],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "filename": filename
            }
        }
        
        # Save everything in a single JSON file
        with open(os.path.join(DOCUMENTS_DIR, f"{filename}.json"), 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved document: {doc_data['title']}")
        return True
    except Exception as e:
        logger.error(f"Error saving document: {str(e)}")
        return False

def main():
    st.set_page_config(page_title="Author Assistant", layout="wide")
    
    initialize_session_state()
    create_directories()
    
    ai_service = AIService()

    st.title("📚 Author Assistant")
    st.markdown("---")

    # Main layout
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.subheader("📝 Document Editor")
        
        # Document Details
        title = st.text_input("Book Title", key="doc_title")
        description = st.text_area("Book Description", height=100, key="doc_description")
        keywords = st.text_input("Keywords (comma-separated)", key="doc_keywords")
        
        # Chapter Management
        st.subheader("Chapters")
        
        if 'chapters' not in st.session_state:
            st.session_state.chapters = []
            
        # Add new chapter
        with st.expander("Add New Chapter"):
            chapter_title = st.text_input("Chapter Title")
            chapter_content = st.text_area("Chapter Content", height=200)
            if st.button("Add Chapter"):
                new_chapter = {
                    "title": chapter_title,
                    "content": chapter_content,
                    "sections": []
                }
                st.session_state.chapters.append(new_chapter)
                st.success("Chapter added!")
        
        # Display existing chapters
        for i, chapter in enumerate(st.session_state.chapters):
            with st.expander(f"Chapter {i+1}: {chapter['title']}"):
                # Add delete chapter button at the top
                col1, col2 = st.columns([0.8, 0.2])
                with col2:
                    if st.button("🗑️ Delete Chapter", key=f"del_chapter_{i}"):
                        st.session_state.chapters.pop(i)
                        st.rerun()
                
                with col1:
                    st.write(chapter['content'])
                
                # Add section to chapter
                section_title = st.text_input(f"New Section Title for Chapter {i+1}", key=f"section_title_{i}")
                section_content = st.text_area(f"Section Content", key=f"section_content_{i}")
                if st.button(f"Add Section to Chapter {i+1}", key=f"add_section_{i}"):
                    chapter['sections'].append({
                        "title": section_title,
                        "content": section_content
                    })
                
                # Display sections with delete buttons
                for j, section in enumerate(chapter['sections']):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.markdown(f"**Section {j+1}: {section['title']}**")
                        st.write(section['content'])
                    with col2:
                        if st.button("🗑️", key=f"del_section_{i}_{j}"):
                            chapter['sections'].pop(j)
                            st.rerun()

        # Save Document
        if st.button("💾 Save Document", use_container_width=True):
            if title:
                doc_data = {
                    "title": title,
                    "description": description,
                    "keywords": [k.strip() for k in keywords.split(',') if k.strip()],
                    "chapters": st.session_state.chapters
                }
                if save_document(doc_data):
                    st.success("Document saved successfully!")
                    st.session_state.documents = load_documents()
                else:
                    st.error("Error saving document")
            else:
                st.warning("Please provide at least a title")

    with col2:
        st.subheader("🤖 AI Assistant")
        content = st.text_area("Content", height=300, key="doc_content")
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
        with st.expander(f"📄 {doc['title']} - {doc['metadata']['created_at'][:10]}"):
            st.markdown(doc['description'])
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"**Keywords:** {', '.join(doc['keywords'])}")
            with col2:
                if st.button("📝 Edit", key=f"edit_{doc['metadata']['filename']}"):
                    st.session_state.editing_document = doc
                    st.session_state.chapters = doc['chapters']
                    st.rerun()
                    
            # Display chapters and sections
            for chapter in doc['chapters']:
                st.markdown(f"### {chapter['title']}")
                st.markdown(chapter['content'])
                for section in chapter['sections']:
                    st.markdown(f"#### {section['title']}")
                    st.markdown(section['content'])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")