import os
import logging

logger = logging.getLogger(__name__)

def create_templates_directory():
    """Create template files for the web UI"""
    os.makedirs('app/templates', exist_ok=True)
    os.makedirs('app/static/css', exist_ok=True)
    os.makedirs('app/static/js', exist_ok=True)
   