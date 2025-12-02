import docker
import os

def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        return None

def generate_dockerfile(project_path):
    """
    Analyzes the project directory and generates a Dockerfile.
    """
    dockerfile_path = os.path.join(project_path, 'Dockerfile')
    
    # Check for existing Dockerfile
    if os.path.exists(dockerfile_path):
        return
        
    # Check for Python
    if os.path.exists(os.path.join(project_path, 'requirements.txt')) or \
       os.path.exists(os.path.join(project_path, 'main.py')):
        content = """
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
CMD ["python", "main.py"]
"""
    # Default to Static Site (Nginx)
    elif os.path.exists(os.path.join(project_path, 'index.html')):
        content = """
FROM nginx:alpine
COPY . /usr/share/nginx/html
"""
    else:
        # Fallback
        content = """
FROM alpine
CMD ["echo", "No recognized project type found"]
"""
        
    with open(dockerfile_path, 'w') as f:
        f.write(content.strip())

def run_container(project_id, image_tag, host_port):
    """
    Runs a container from the given image tag, mapping the host port.
    """
    client = get_docker_client()
    if not client:
        raise Exception("Docker not available")
        
    container_name = f"anydeploy-runner-{project_id}"
    
    # Stop existing container if any
    try:
        existing = client.containers.get(container_name)
        existing.stop()
        existing.remove()
    except docker.errors.NotFound:
        pass
        
    # Determine internal port (default 80, but Python/Node might use others)
    # For MVP, we'll assume the Dockerfile exposes the right port or we default to 80.
    # But wait, our generated python Dockerfile runs `python main.py`. 
    # We need to know what port `main.py` listens on.
    # For the sample project, let's assume it doesn't listen on a port yet (it just prints hello).
    # To make this testable, we need a web server.
    
    # Let Docker assign a random host port by binding to 0
    ports = {'8000/tcp': 0, '80/tcp': 0}
    
    container = client.containers.run(
        image_tag,
        name=container_name,
        ports=ports,
        detach=True
    )
    
    # Reload container to get the assigned port
    container.reload()
    
    # Find the mapped port
    # NetworkSettings -> Ports -> '8000/tcp' -> [{'HostIp': '0.0.0.0', 'HostPort': '32768'}]
    assigned_port = None
    container_ports = container.attrs['NetworkSettings']['Ports']
    
    for internal_port in ['8000/tcp', '80/tcp']:
        if container_ports.get(internal_port):
            assigned_port = container_ports[internal_port][0]['HostPort']
            break
            
    if not assigned_port:
        # Fallback if something weird happens
        assigned_port = 0
        
    return container.id, int(assigned_port)

def stop_container(project_id):
    """
    Stops and removes the container for the given project.
    """
    client = get_docker_client()
    if not client:
        return
        
    container_name = f"anydeploy-runner-{project_id}"
    try:
        container = client.containers.get(container_name)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        pass
    except Exception as e:
        print(f"Error stopping container {container_name}: {e}")

    # Remove image
    image_tag = f"anydeploy-{project_id}"
    try:
        client.images.remove(image_tag, force=True)
    except docker.errors.ImageNotFound:
        pass
    except Exception as e:
        print(f"Error removing image {image_tag}: {e}")

