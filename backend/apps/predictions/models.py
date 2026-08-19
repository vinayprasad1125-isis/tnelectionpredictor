from django.db import models

class PredictionHistory(models.Model):
    constituency_name = models.CharField(max_length=255)
    election_year = models.IntegerField()
    predicted_winner_party = models.CharField(max_length=100)
    probabilities = models.JSONField(help_text="JSON representation of winning probabilities by party")
    model_version = models.CharField(max_length=50)
    prediction_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Prediction Histories"
        ordering = ['-prediction_timestamp']

    def __str__(self):
        return f"{self.constituency_name} ({self.election_year}) - Winner: {self.predicted_winner_party} [v{self.model_version}]"
