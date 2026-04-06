import os
import sys

# Make the inner project folder importable for Streamlit on Hugging Face Spaces.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, "email_openenv")
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Importing this module executes the Streamlit app UI.
import email_openenv.app  # noqa: F401
