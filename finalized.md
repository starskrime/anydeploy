# Finalized Tasks

_Completed tasks will be moved here._

- [x] **Initialize Project Directory**
    - Create `artifacts/` directory.
    - Verified Python 3.12 environment.
    - Installed Django and dependencies (`django`, `docker`, `django-htmx`).

- [x] **Scaffold Django Project**
    - Run `django-admin startproject core .`
    - Created `projects` app.

- [x] **Database & Models**
    - Defined `Project` model in `projects/models.py`.
    - Ran migrations.

- [x] **File Storage Logic**
    - Implemented `handle_project_upload` in `projects/utils.py` to save uploads to `artifacts/<project_id>/source.zip`.

- [x] **Docker Client Setup**
    - Created `projects/docker_utils.py` with `get_docker_client`.

- [x] **Dockerfile Generator**
    - Implemented `generate_dockerfile` to auto-detect Python vs Static sites.

- [x] **Build Logic (Threading)**
    - Created `projects/tasks.py` to handle unzipping, Dockerfile generation, and building.
    - Updated `views.py` to trigger `start_build` in a background thread.

- [x] **Port Management**
    - Implemented `find_available_port` in `projects/utils.py`.

- [x] **Container Runner**
    - Implemented `run_container` in `projects/docker_utils.py` to stop old containers and start new ones.

- [x] **Integrate with Build Task**
    - Updated `projects/tasks.py` to find a port and run the container after building.

- [x] **Log Storage (Database)**
    - Added `logs` field to `Project` model.
    - Ran migrations.

- [x] **Capture Build Logs**
    - Updated `projects/tasks.py` to capture Docker build output and exceptions into `project.logs`.

- [x] **Logs UI**
    - Created `project_logs` view and `projects/logs.html`.
    - Added "Logs" link to dashboard.
