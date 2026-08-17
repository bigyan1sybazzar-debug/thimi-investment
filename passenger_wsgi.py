import os
import sys

# Path to the project root directory
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import WSGI application callable
from backend.wsgi import application
