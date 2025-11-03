from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'is_read', 'created_at']
    list_filter = ['status', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('contact information',{
            'fields': ('name', 'email', 'phone')

        }),
        ('Message Details',{
            'fields' : ('subject', 'message')

        }),
        ('Status',{
            'fields':('status', 'is_read')


        }),
        ('Timestamps', {
            'fields':('createc_at', 'updated_at')

        }),
    )
    def mark_as_read(self. request, queryset):
        queryset.update(status='replied')
    mark_as_replied.short_description = "Mark selected as replied"
    actions = [mark_as_read, mark_as_replied]
        

# Register your models here.
