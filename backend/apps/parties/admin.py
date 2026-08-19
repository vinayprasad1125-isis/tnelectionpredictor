from django.contrib import admin
from apps.parties.models import Party

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name')
    search_fields = ('abbreviation', 'name')
