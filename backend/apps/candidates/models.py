from django.db import models

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    metadata = models.JSONField(null=True, blank=True, help_text="Additional information like age, gender, education, etc.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
