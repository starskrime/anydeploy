from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_project, name='create_project'),
    path('delete/<uuid:project_id>/', views.delete_project, name='delete_project'),
    path('logs/<uuid:project_id>/', views.project_logs, name='project_logs'),
]
