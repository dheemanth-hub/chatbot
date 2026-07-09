from django.contrib import admin

# Register your models here.
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'created_at', 'text')
    list_filter = ('sender',)
    search_fields = ('text',)
    ordering = ('-created_at',)