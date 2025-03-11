import os
from dotenv import load_dotenv
from loguru import logger

# Set up logging
logger.add("app.log", rotation="500 MB", level="DEBUG")

# Load environment variables
load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is required")

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCUMENTS_DIR = os.path.join(DATA_DIR, "documents")

# Create required directories
for directory in [DATA_DIR, DOCUMENTS_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Created directory: {directory}")