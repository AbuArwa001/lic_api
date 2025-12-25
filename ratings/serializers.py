from rest_framework import serializers
from .models import Rating

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = (
            'id', 'user', 'project', 'rating', 'comment', 'rated_at'
        )
        read_only_fields = ['id', 'rated_at']
