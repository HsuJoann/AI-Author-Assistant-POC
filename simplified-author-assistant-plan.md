# Simplified Author Assistant WebApp - Python Proof of Concept

## Project Overview
Create a lightweight, single-user proof of concept for a non-fiction writing assistant using Python. The app will integrate with Anthropic API (Claude) for AI assistance and VoyageAI for RAG capabilities. All data will be stored locally in files rather than using a database system.

## Tech Stack
- **Backend**: Python with FastAPI
- **Frontend**: Streamlit (for rapid development)
- **Storage**: Local filesystem for document storage
- **APIs**: Anthropic API, VoyageAI API
- **Data Format**: JSON files for structured data, Markdown for content

## Project Structure

```
author-assistant-poc/
├── app/
│   ├── main.py            # Main Streamlit application entry point
│   ├── config.py          # Configuration and environment variables
│   ├── utils/
│   │   ├── file_manager.py    # Handles local file operations
│   │   ├── text_processor.py  # Text manipulation utilities
│   │   └── helpers.py         # General utility functions
│   ├── services/
│   │   ├── anthropic_service.py  # Claude API integration
│   │   ├── voyage_service.py     # VoyageAI integration
│   │   └── editor_service.py     # Text editing functionality
│   ├── models/
│   │   ├── project.py       # Project data model
│   │   ├── document.py      # Document data model
│   │   └── research.py      # Research data model
│   ├── components/
│   │   ├── sidebar.py       # Sidebar UI component
│   │   ├── editor.py        # Editor UI component
│   │   ├── ai_assistant.py  # AI assistance panel
│   │   └── research_panel.py # Research management panel
│   └── pages/
│       ├── home.py          # Home/dashboard page
│       ├── editor.py        # Writing editor page
│       ├── research.py      # Research management page
│       └── settings.py      # App settings page
├── data/
│   ├── projects/            # Project data stored as JSON files
│   ├── documents/           # Document content stored as Markdown
│   └── research/            # Research materials
├── requirements.txt
├── .env.example
└── README.md
```

## Implementation Plan

### Phase 1: Project Setup and Basic Structure

1. **Environment Setup**
   ```python
   # Install required packages
   pip install fastapi uvicorn streamlit python-dotenv anthropic voyageai pydantic
   ```

2. **Configuration Module**
   ```python
   # config.py
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
   VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
   DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
   PROJECTS_DIR = os.path.join(DATA_DIR, "projects")
   DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")
   RESEARCH_DIR = os.path.join(DATA_DIR, "research")
   
   # Create directories if they don't exist
   for directory in [DATA_DIR, PROJECTS_DIR, DOCUMENTS_DIR, RESEARCH_DIR]:
       os.makedirs(directory, exist_ok=True)
   ```

3. **Data Models with Pydantic**
   ```python
   # models/project.py
   from pydantic import BaseModel
   from typing import List, Optional
   from datetime import datetime
   
   class Project(BaseModel):
       id: str
       title: str
       subtitle: Optional[str] = None
       topic: str
       created_at: datetime = datetime.now()
       updated_at: datetime = datetime.now()
       documents: List[str] = []  # List of document IDs
       research_items: List[str] = []  # List of research item IDs
   ```

### Phase 2: File Management System

1. **File Manager Implementation**
   ```python
   # utils/file_manager.py
   import json
   import os
   from datetime import datetime
   import uuid
   from ..config import PROJECTS_DIR, DOCUMENTS_DIR, RESEARCH_DIR
   
   def create_project(title, subtitle="", topic=""):
       """Create a new project and save to local filesystem"""
       project_id = str(uuid.uuid4())
       project_data = {
           "id": project_id,
           "title": title,
           "subtitle": subtitle,
           "topic": topic,
           "created_at": datetime.now().isoformat(),
           "updated_at": datetime.now().isoformat(),
           "documents": [],
           "research_items": []
       }
       
       project_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
       with open(project_path, 'w') as f:
           json.dump(project_data, f, indent=2)
       
       return project_data
   
   def save_document(project_id, title, content, document_id=None):
       """Save document content to filesystem"""
       if not document_id:
           document_id = str(uuid.uuid4())
           
       # Save content as markdown file
       doc_path = os.path.join(DOCUMENTS_DIR, f"{document_id}.md")
       with open(doc_path, 'w') as f:
           f.write(content)
           
       # Update project metadata
       project_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
       with open(project_path, 'r') as f:
           project_data = json.load(f)
           
       if document_id not in project_data["documents"]:
           project_data["documents"].append(document_id)
           
       project_data["updated_at"] = datetime.now().isoformat()
       
       # Save updated project data
       with open(project_path, 'w') as f:
           json.dump(project_data, f, indent=2)
           
       # Create document metadata
       doc_meta = {
           "id": document_id,
           "project_id": project_id,
           "title": title,
           "created_at": datetime.now().isoformat(),
           "updated_at": datetime.now().isoformat(),
       }
       
       # Save document metadata
       doc_meta_path = os.path.join(DOCUMENTS_DIR, f"{document_id}.json")
       with open(doc_meta_path, 'w') as f:
           json.dump(doc_meta, f, indent=2)
           
       return document_id, doc_meta
   
   def get_all_projects():
       """Get all projects from filesystem"""
       projects = []
       for filename in os.listdir(PROJECTS_DIR):
           if filename.endswith('.json'):
               with open(os.path.join(PROJECTS_DIR, filename), 'r') as f:
                   projects.append(json.load(f))
       return projects
   
   def get_document_content(document_id):
       """Get document content from filesystem"""
       doc_path = os.path.join(DOCUMENTS_DIR, f"{document_id}.md")
       if not os.path.exists(doc_path):
           return ""
       with open(doc_path, 'r') as f:
           return f.read()
   ```

### Phase 3: AI Service Integration

1. **Anthropic Service Implementation**
   ```python
   # services/anthropic_service.py
   import anthropic
   from ..config import ANTHROPIC_API_KEY
   
   client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
   
   def improve_writing(content, instruction):
       """Use Claude to improve writing based on instruction"""
       prompt = f"""
       Please help improve the following non-fiction writing according to this instruction: {instruction}
       
       Here is the content to improve:
       
       {content}
       
       Please provide the improved version.
       """
       
       response = client.messages.create(
           model="claude-3-7-sonnet-20250219",
           max_tokens=4000,
           messages=[
               {"role": "user", "content": prompt}
           ]
       )
       
       return response.content[0].text
   
   def analyze_argument(content):
       """Use Claude to analyze the logical structure of an argument"""
       prompt = f"""
       Please analyze the logical structure of the following non-fiction content:
       
       {content}
       
       Provide feedback on:
       1. The main thesis/argument
       2. The evidence presented
       3. Logical flow and connections
       4. Potential gaps or weaknesses
       5. Suggestions for improvement
       """
       
       response = client.messages.create(
           model="claude-3-7-sonnet-20250219",
           max_tokens=4000,
           messages=[
               {"role": "user", "content": prompt}
           ]
       )
       
       return response.content[0].text
   
   def generate_outline(topic, depth=3):
       """Generate an outline for a given topic"""
       prompt = f"""
       Please create a detailed outline for a non-fiction piece on this topic: {topic}
       
       Include:
       - A clear structure with sections and subsections up to {depth} levels deep
       - Key points to address in each section
       - Potential sources or evidence types to include
       
       The outline should be comprehensive but focused on the most important aspects of the topic.
       """
       
       response = client.messages.create(
           model="claude-3-7-sonnet-20250219",
           max_tokens=3000,
           messages=[
               {"role": "user", "content": prompt}
           ]
       )
       
       return response.content[0].text
   ```

2. **VoyageAI Service Implementation**
   ```python
   # services/voyage_service.py
   import os
   import json
   import voyageai
   from ..config import VOYAGE_API_KEY, DOCUMENTS_DIR, RESEARCH_DIR
   
   client = voyageai.Client(api_key=VOYAGE_API_KEY)
   
   def generate_embedding(text):
       """Generate embedding for text using VoyageAI"""
       response = client.embed(
           text=text,
           model="voyage-2"
       )
       return response.embeddings[0]
   
   def index_document(document_id):
       """Generate and store embeddings for a document"""
       content = ""
       doc_path = os.path.join(DOCUMENTS_DIR, f"{document_id}.md")
       
       with open(doc_path, 'r') as f:
           content = f.read()
           
       if not content:
           return None
           
       # Generate embedding
       embedding = generate_embedding(content)
       
       # Store embedding
       embedding_path = os.path.join(DOCUMENTS_DIR, f"{document_id}_embedding.json")
       with open(embedding_path, 'w') as f:
           json.dump(embedding, f)
           
       return embedding
   
   def find_similar_content(query, project_id):
       """Find similar content to query in project documents"""
       query_embedding = generate_embedding(query)
       
       # Get all document ids for the project
       project_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
       with open(project_path, 'r') as f:
           project_data = json.load(f)
           document_ids = project_data.get("documents", [])
       
       similarities = []
       
       # Compare query embedding with document embeddings
       for doc_id in document_ids:
           embedding_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}_embedding.json")
           if not os.path.exists(embedding_path):
               # Generate embedding if it doesn't exist
               index_document(doc_id)
               
           if os.path.exists(embedding_path):
               with open(embedding_path, 'r') as f:
                   doc_embedding = json.load(f)
                   
               # Get document metadata
               doc_meta_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.json")
               with open(doc_meta_path, 'r') as f:
                   doc_meta = json.load(f)
                   
               # Calculate similarity score
               similarity = calculate_cosine_similarity(query_embedding, doc_embedding)
               
               # Get document content snippet
               content = get_document_content(doc_id)
               snippet = content[:200] + "..." if len(content) > 200 else content
               
               similarities.append({
                   "document_id": doc_id,
                   "title": doc_meta.get("title", "Untitled"),
                   "similarity": similarity,
                   "snippet": snippet
               })
       
       # Sort by similarity score descending
       similarities.sort(key=lambda x: x["similarity"], reverse=True)
       
       return similarities[:5]  # Return top 5 matches
   
   def calculate_cosine_similarity(vec1, vec2):
       """Calculate cosine similarity between two vectors"""
       import numpy as np
       vec1 = np.array(vec1)
       vec2 = np.array(vec2)
       return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
   ```

### Phase 4: Streamlit UI Implementation

1. **Main App Entry Point**
   ```python
   # main.py
   import streamlit as st
   from components import sidebar
   from pages import home, editor, research, settings
   
   st.set_page_config(
       page_title="Author Assistant",
       page_icon="📝",
       layout="wide"
   )
   
   # Initialize session state
   if "current_page" not in st.session_state:
       st.session_state.current_page = "home"
   if "current_project" not in st.session_state:
       st.session_state.current_project = None
   if "current_document" not in st.session_state:
       st.session_state.current_document = None
   
   # Render sidebar
   selected_page = sidebar.render_sidebar()
   
   # Display selected page
   if selected_page == "home":
       home.render_home_page()
   elif selected_page == "editor":
       editor.render_editor_page()
   elif selected_page == "research":
       research.render_research_page()
   elif selected_page == "settings":
       settings.render_settings_page()
   ```

2. **Sidebar Component**
   ```python
   # components/sidebar.py
   import streamlit as st
   from utils.file_manager import get_all_projects, create_project
   
   def render_sidebar():
       with st.sidebar:
           st.title("Author Assistant")
           
           # Navigation
           pages = {
               "home": "📋 Dashboard",
               "editor": "✏️ Editor",
               "research": "🔍 Research",
               "settings": "⚙️ Settings"
           }
           
           selected_page = st.radio("Navigation", list(pages.values()), 
                                    format_func=lambda x: x)
           
           # Map back to page key
           for key, value in pages.items():
               if value == selected_page:
                   selected_page = key
           
           st.divider()
           
           # Project selector
           projects = get_all_projects()
           project_titles = [p["title"] for p in projects]
           
           if projects:
               selected_project_title = st.selectbox(
                   "Select Project", 
                   project_titles
               )
               
               # Find selected project
               for project in projects:
                   if project["title"] == selected_project_title:
                       st.session_state.current_project = project
           
           # Create new project
           with st.expander("New Project"):
               new_title = st.text_input("Project Title")
               new_topic = st.text_input("Topic")
               
               if st.button("Create Project"):
                   if new_title:
                       new_project = create_project(new_title, topic=new_topic)
                       st.session_state.current_project = new_project
                       st.success(f"Created project: {new_title}")
                       st.rerun()
           
           return selected_page
   ```

3. **Editor Page**
   ```python
   # pages/editor.py
   import streamlit as st
   from utils.file_manager import save_document, get_document_content
   from services.anthropic_service import improve_writing, analyze_argument
   import json
   import os
   from config import DOCUMENTS_DIR
   
   def render_editor_page():
       st.title("Writing Editor")
       
       if not st.session_state.current_project:
           st.warning("Please select or create a project first.")
           return
       
       # Layout: Editor on the left, AI Assistant on the right
       col1, col2 = st.columns([0.7, 0.3])
       
       with col1:
           project = st.session_state.current_project
           st.subheader(f"Project: {project['title']}")
           
           # Document selector
           documents = []
           for doc_id in project.get("documents", []):
               doc_meta_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.json")
               if os.path.exists(doc_meta_path):
                   with open(doc_meta_path, 'r') as f:
                       doc_meta = json.load(f)
                       documents.append(doc_meta)
           
           doc_titles = ["New Document"] + [doc["title"] for doc in documents]
           selected_doc = st.selectbox("Select Document", doc_titles)
           
           if selected_doc == "New Document":
               st.session_state.current_document = None
               doc_title = st.text_input("Document Title")
               doc_content = st.text_area("Content", height=500)
               
               if st.button("Save Document"):
                   if doc_title and doc_content:
                       doc_id, _ = save_document(
                           project["id"], 
                           doc_title, 
                           doc_content
                       )
                       st.success(f"Saved document: {doc_title}")
                       st.rerun()
           else:
               # Find selected document
               current_doc = None
               for doc in documents:
                   if doc["title"] == selected_doc:
                       current_doc = doc
                       break
               
               if current_doc:
                   st.session_state.current_document = current_doc
                   doc_content = get_document_content(current_doc["id"])
                   
                   doc_title = st.text_input("Document Title", value=current_doc["title"])
                   updated_content = st.text_area("Content", value=doc_content, height=500)
                   
                   if st.button("Update Document"):
                       save_document(
                           project["id"], 
                           doc_title, 
                           updated_content,
                           document_id=current_doc["id"]
                       )
                       st.success("Document updated!")
                       st.rerun()
       
       with col2:
           st.subheader("AI Assistant")
           
           if st.session_state.current_document:
               doc_content = get_document_content(st.session_state.current_document["id"])
               
               with st.expander("Improve Writing"):
                   improvement_type = st.selectbox(
                       "Improvement Type",
                       ["Clarity", "Conciseness", "Structure", "Flow", "Academic Tone", "Simplify Language"]
                   )
                   
                   if st.button("Get Suggestions"):
                       with st.spinner("Getting AI suggestions..."):
                           improved = improve_writing(doc_content, improvement_type)
                           st.text_area("Suggested Improvements", value=improved, height=300)
                           if st.button("Apply Suggestions"):
                               save_document(
                                   project["id"],
                                   st.session_state.current_document["title"],
                                   improved,
                                   document_id=st.session_state.current_document["id"]
                               )
                               st.success("Applied suggestions!")
                               st.rerun()
               
               with st.expander("Analyze Argument"):
                   if st.button("Analyze"):
                       with st.spinner("Analyzing argument structure..."):
                           analysis = analyze_argument(doc_content)
                           st.write(analysis)
   ```

### Phase 5: Research Management

1. **Research Page Implementation**
   ```python
   # pages/research.py
   import streamlit as st
   import os
   import json
   from utils.file_manager import get_document_content
   from services.voyage_service import find_similar_content
   from config import RESEARCH_DIR
   
   def render_research_page():
       st.title("Research Management")
       
       if not st.session_state.current_project:
           st.warning("Please select or create a project first.")
           return
       
       project = st.session_state.current_project
       
       col1, col2 = st.columns([0.5, 0.5])
       
       with col1:
           st.subheader("Research Notes")
           
           # Simple research note taking
           note_title = st.text_input("Note Title")
           note_content = st.text_area("Note Content", height=200)
           tags = st.text_input("Tags (comma separated)")
           
           if st.button("Save Note"):
               if note_title and note_content:
                   note_id = save_research_note(
                       project["id"],
                       note_title,
                       note_content,
                       tags.split(",") if tags else []
                   )
                   st.success(f"Saved research note: {note_title}")
       
       with col2:
           st.subheader("Semantic Search")
           
           search_query = st.text_input("Search Query")
           
           if search_query and st.button("Search"):
               with st.spinner("Searching..."):
                   results = find_similar_content(search_query, project["id"])
                   
                   if results:
                       for result in results:
                           st.write(f"**{result['title']}** - Similarity: {result['similarity']:.2f}")
                           st.write(result["snippet"])
                           st.divider()
                   else:
                       st.info("No similar content found.")
   
   def save_research_note(project_id, title, content, tags=[]):
       """Save a research note to the filesystem"""
       import uuid
       from datetime import datetime
       
       note_id = str(uuid.uuid4())
       
       note_data = {
           "id": note_id,
           "project_id": project_id,
           "title": title,
           "tags": tags,
           "created_at": datetime.now().isoformat(),
           "updated_at": datetime.now().isoformat()
       }
       
       # Save note content
       note_path = os.path.join(RESEARCH_DIR, f"{note_id}.md")
       with open(note_path, 'w') as f:
           f.write(content)
           
       # Save note metadata
       meta_path = os.path.join(RESEARCH_DIR, f"{note_id}.json")
       with open(meta_path, 'w') as f:
           json.dump(note_data, f, indent=2)
           
       # Update project
       project_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
       with open(project_path, 'r') as f:
           project_data = json.load(f)
           
       if "research_items" not in project_data:
           project_data["research_items"] = []
           
       if note_id not in project_data["research_items"]:
           project_data["research_items"].append(note_id)
           
       with open(project_path, 'w') as f:
           json.dump(project_data, f, indent=2)
           
       return note_id
   ```

### Running the Application

```python
# Run the Streamlit app
# Command: streamlit run app/main.py
```

## Core Features

1. **Simple Project Management**
   - Create and manage non-fiction writing projects
   - Organize documents within projects
   - Store all data in local filesystem

2. **Markdown-based Editor**
   - Basic text editor with Markdown support
   - Save and edit document content
   - Auto-save functionality

3. **Claude AI Integration**
   - Writing improvement suggestions
   - Argument analysis
   - Content generation assistance

4. **VoyageAI RAG Implementation**
   - Semantic search across documents
   - Find related content
   - Research organization

5. **Research Management**
   - Take and organize research notes
   - Tag and categorize research
   - Link research to documents

## Next Steps

After testing this proof of concept, you can expand it by:

1. Adding a proper database (SQLite for simplicity or PostgreSQL for production)
2. Implementing user authentication
3. Enhancing the UI with more advanced components
4. Adding export functionality
5. Implementing collaborative features
6. Deploying to a web server

This simplified plan allows you to quickly test the core functionality with local storage before committing to a more complex architecture.
