from django.db import models
import uuid

class Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('building', 'Building'),
        ('running', 'Running'),
        ('failed', 'Failed'),
    ]

    project_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    port = models.IntegerField(null=True, blank=True)
    logs = models.TextField(blank=True)

    def __str__(self):
        return self.name
