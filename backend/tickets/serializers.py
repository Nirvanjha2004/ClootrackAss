from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model.
    Handles validation and serialization of ticket data.
    """
    
    class Meta:
        model = Ticket
        fields = ['id', 'title', 'description', 'category', 'priority', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_title(self, value):
        """Validate that title is not empty and within length limit."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value
    
    def validate_description(self, value):
        """Validate that description is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value
