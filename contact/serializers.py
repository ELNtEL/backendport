from rest_framework import serializers
from .models import ContactMessage

class ConctactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fiels = ['id', 'name', 'email', 'subject', 'message', 'phone', 'status', 'is_read', 'created_at']
        read_only_fields = ['id', 'status', 'is_read', 'created_at']
    def validate_email(self, value):
        """validate email format"""
        if not value:
            raise serializers.ValidationError("Email is required")
        return value.lower()
    def validate_message(self, value):
        """Ensure message is not too short"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value