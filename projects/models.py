from django.db import models
import uuid

class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('planned', 'Planned'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    image = models.ImageField(upload_to='projects/', null=True, blank=True)

    def __str__(self):
        return self.name

def project_image_path(instance, filename):
    # projects/<slug>/<filename>
    # Since we don't have a slug field, we'll use the project name (sanitized) or ID
    # Let's use ID for safety and uniqueness, or name if preferred. 
    # User asked for: "projects/revert_center/revert_1.jpg"
    # So we should try to use a slugified name.
    import re
    slug = re.sub(r'[^a-z0-9]', '_', instance.project.name.lower())
    return f'projects/{slug}/{filename}'

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=project_image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.project.name}"
