from django.contrib import admin
from .models import PredictionHistory

@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('constituency_name', 'election_year', 'predicted_winner_party', 'model_version', 'prediction_timestamp')
    search_fields = ('constituency_name', 'predicted_winner_party', 'model_version')
    list_filter = ('election_year', 'model_version')
