import threading
import os
import zipfile
import shutil
from django.conf import settings
from .models import Project
from .docker_utils import get_docker_client, generate_dockerfile, run_container

def build_project_task(project_id):
    try:
        project = Project.objects.get(project_id=project_id)
        project.status = 'building'
        project.save()

        # Paths
        artifacts_dir = os.path.join(settings.BASE_DIR, 'artifacts', str(project_id))
        zip_path = os.path.join(artifacts_dir, 'source.zip')
        extract_dir = os.path.join(artifacts_dir, 'source')
        
        # 1. Unzip
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # Check for single nested directory
        items = os.listdir(extract_dir)
        if len(items) == 1 and os.path.isdir(os.path.join(extract_dir, items[0])):
            project_root = os.path.join(extract_dir, items[0])
        else:
            project_root = extract_dir
            
        # 2. Generate Dockerfile
        generate_dockerfile(project_root)
        
        # 3. Build Docker Image
        client = get_docker_client()
        if not client:
            raise Exception("Docker not available")
            
        image_tag = f"anydeploy-{project_id}"
        print(f"Building image: {image_tag} from {project_root}")
        
        # Capture logs
        build_logs = []
        try:
            # Use low-level API to stream logs correctly
            # client.api.build returns a generator of dicts if decode=True
            for chunk in client.api.build(path=project_root, tag=image_tag, rm=True, decode=True):
                if 'stream' in chunk:
                    line = chunk['stream']
                    build_logs.append(line)
                    print(line, end='')
                elif 'error' in chunk:
                    raise Exception(chunk['error'])
                    
            project.logs = "".join(build_logs)
            project.save()
            
        except Exception as build_error:
            project.logs = "".join(build_logs) + f"\nBuild Error: {str(build_error)}"
            project.save()
            raise build_error

        # 4. Run Container
        # We don't need find_available_port anymore, Docker handles it
        container_id, port = run_container(project_id, image_tag, 0)
        
        project.status = 'running'
        project.port = port
        project.logs += f"\nContainer started on port {port}"
        project.save()
        print(f"Build success for {project_id}. Running on port {port}")

    except Exception as e:
        import traceback
        error_msg = f"Task failed for {project_id}: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        
        project = Project.objects.get(project_id=project_id)
        project.status = 'failed'
        # Append error to existing logs if any
        project.logs = (project.logs or "") + f"\n\nCRITICAL ERROR:\n{error_msg}"
        project.save()

def start_build(project_id):
    thread = threading.Thread(target=build_project_task, args=(project_id,))
    thread.start()
