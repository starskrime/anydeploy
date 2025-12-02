import os
import shutil
import socket
from django.conf import settings

ARTIFACTS_DIR = os.path.join(settings.BASE_DIR, 'artifacts')

def handle_project_upload(project_id, uploaded_file):
    """
    Saves the uploaded file to artifacts/<project_id>/source.zip
    """
    project_dir = os.path.join(ARTIFACTS_DIR, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    
    file_path = os.path.join(project_dir, 'source.zip')
    
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
            
    return file_path

def find_available_port(start_port=9000, end_port=9999):
    """
    Finds the first available port in the given range by attempting to bind to it.
    """
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Try to bind to all interfaces. If it succeeds, the port is free.
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise Exception("No available ports found")
