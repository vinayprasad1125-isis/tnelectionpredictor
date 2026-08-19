from django.db import models

class Party(models.Model):
    name = models.CharField(max_length=200, unique=True)
    abbreviation = models.CharField(max_length=50, unique=True, help_text="e.g., DMK, AIADMK, BJP, INC")
    symbol = models.CharField(max_length=100, null=True, blank=True, help_text="Party symbol name or URL to image")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Parties"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
