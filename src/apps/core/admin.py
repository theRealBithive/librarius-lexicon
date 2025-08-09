from django.contrib import admin
from .models import Audiobook


@admin.register(Audiobook)
class AudiobookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'series', 'narrator', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'author', 'series', 'narrator')
    ordering = ('-created_at',)
