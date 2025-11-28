from django.db import models
from datetime import date

class Task(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    importance = models.IntegerField(default=5)  # Scale 1-10
    estimated_hours = models.IntegerField(default=1)
    # Simple JSON field to store dependency IDs [1, 2, 3]
    dependencies = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
