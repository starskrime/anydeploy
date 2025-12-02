from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from .utils import handle_project_upload
from .tasks import start_build

def index(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/index.html', {'projects': projects})

def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        uploaded_file = request.FILES.get('file')
        
        if name and uploaded_file:
            project = Project.objects.create(name=name, description=description)
            handle_project_upload(project.project_id, uploaded_file)
            
            start_build(project.project_id)
            
            return redirect('index')
            
    return render(request, 'projects/create.html')

def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, project_id=project_id)
        
        # Cleanup Docker container
        from .docker_utils import stop_container
        stop_container(project.project_id)
        
        # Cleanup Artifacts (Optional but good practice)
        import shutil
        import os
        from django.conf import settings
        artifacts_dir = os.path.join(settings.BASE_DIR, 'artifacts', str(project.project_id))
        if os.path.exists(artifacts_dir):
            shutil.rmtree(artifacts_dir)
            
        project.delete()
    return redirect('index')

def project_logs(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    return render(request, 'projects/logs.html', {'project': project})
