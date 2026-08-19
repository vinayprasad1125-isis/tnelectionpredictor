from django.contrib import admin
from apps.elections.models import Election, ElectionResult

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('year', 'election_type', 'state')
    search_fields = ('year', 'election_type')
    list_filter = ('election_type',)

@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = ('election', 'constituency', 'candidate', 'party', 'votes_received', 'is_winner')
    search_fields = ('candidate__name', 'party__abbreviation', 'constituency__name')
    list_filter = ('is_winner', 'election__year', 'party__abbreviation')
