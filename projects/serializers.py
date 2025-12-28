from rest_framework import serializers
from .models import Project, ProjectImage
from django.db.models import Sum

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ['id', 'image']

class ProjectSerializer(serializers.ModelSerializer):
    total_donated = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    goal_amount = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    images = ProjectImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'goal_amount', 'status', 
            'start_date', 'end_date', 'image', 'images', 'total_donated', 'progress_percentage',
            'uploaded_images'
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

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        project = Project.objects.create(**validated_data)
        
        for image in uploaded_images:
            ProjectImage.objects.create(project=project, image=image)
            
        return project

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Add new images
        for image in uploaded_images:
            ProjectImage.objects.create(project=instance, image=image)
            
        return instance