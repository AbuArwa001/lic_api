from rest_framework import serializers
from .models import Project
from django.db.models import Sum

class ProjectSerializer(serializers.ModelSerializer):
    total_donated = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    goal_amount = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'goal_amount', 'status', 
            'start_date', 'end_date', 'image', 'total_donated', 'progress_percentage'
        ]
        

    def get_total_donated(self, obj):
        # Calculate sum dynamically from related donations
        result = obj.donations.aggregate(total=Sum('amount'))
        return result['total'] or 0

    def get_progress_percentage(self, obj):
        total = self.get_total_donated(obj)
        if obj.goal_amount > 0:
            # Formula: (Current / Target) * 100
            percentage = (total / obj.goal_amount) * 100
            return min(round(percentage, 2), 100.00) # Caps at 100% if overfunded
        return 0