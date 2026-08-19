from django.db import models

class Constituency(models.Model):
    CONSTITUENCY_TYPES = [
        ('GEN', 'General'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
    ]

    name = models.CharField(max_length=100)
    number = models.IntegerField(help_text="Constituency Number")
    district = models.CharField(max_length=100, help_text="District where the constituency is located")
    type = models.CharField(max_length=3, choices=CONSTITUENCY_TYPES, default='GEN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Constituencies"
        ordering = ['number']
        unique_together = ['number', 'name']

    def __str__(self):
        return f"{self.number} - {self.name} ({self.district})"
