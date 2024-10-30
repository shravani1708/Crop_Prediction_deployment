import sys
import os

# Add the project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.append(project_home)

from app import app as application  # Import the Flask app from app.py

if __name__ == "__main__":
    application.run()
