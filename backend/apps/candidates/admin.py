from django.contrib import admin
from apps.candidates.models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
