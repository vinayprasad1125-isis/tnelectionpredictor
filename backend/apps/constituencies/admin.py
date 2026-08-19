from django.contrib import admin
from apps.constituencies.models import Constituency

@admin.register(Constituency)
class ConstituencyAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'district', 'type')
    search_fields = ('name', 'district', 'number')
    list_filter = ('type', 'district')
