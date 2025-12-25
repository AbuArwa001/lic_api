from django.core.management.base import BaseCommand
from projects.models import Project
from datetime import date

class Command(BaseCommand):
    help = 'Seeds the database with initial projects'

    def handle(self, *args, **kwargs):
        projects_data = [
            {
                "id": "revert-center-establishment", # Using UUIDs in model, but we can try to force ID or just let it generate and update frontend mapping. 
                # Actually, since frontend uses slugs/IDs, we should probably add a 'slug' field to Project model or just use the generated UUIDs and update frontend.
                # For simplicity now, I'll let UUIDs generate and we'll fetch the list.
                "name": "Revert Center Establishment",
                "description": "About Project Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                "start_date": date(2025, 4, 18),
                "goal_amount": 5000000.00,
                "current_amount": 1250000.00,
                "status": "ongoing",
                # Image handling requires actual files. I'll skip image upload in seed for now or point to a URL if I had one.
            },
            {
                "name": "College Construction",
                "description": "About Project Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                "start_date": date(2025, 4, 18),
                "goal_amount": 10000000.00,
                "current_amount": 3500000.00,
                "status": "ongoing",
            },
             {
                "name": "Revert Center Establishment 2",
                "description": "About Project Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
                "start_date": date(2025, 4, 18),
                "goal_amount": 2000000.00,
                "current_amount": 50000.00,
                "status": "ongoing",
            }
        ]

        for p_data in projects_data:
            Project.objects.create(
                name=p_data["name"],
                description=p_data["description"],
                start_date=p_data["start_date"],
                goal_amount=p_data["goal_amount"],
                current_amount=p_data["current_amount"],
                status=p_data["status"]
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created project "{p_data["name"]}"'))
