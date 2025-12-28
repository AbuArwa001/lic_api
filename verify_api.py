import os
import django
import requests
import sys

# Setup Django environment
sys.path.append('/home/khalfan/Desktop/LIC/lic_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lic_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def verify_api():
    # 1. Get or Create User
    username = "testadmin"
    password = "testpassword123"
    email = "testadmin@example.com"
    
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Created user: {username}")
    else:
        print(f"Using existing user: {username}")

    # 2. Generate Token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"Generated Access Token: {access_token[:20]}...")

    # 3. Fetch Donations
    url = "http://localhost:8000/api/v1/donations/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        print(f"Fetching from {url}...")
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Data Type: {type(data)}")
            if isinstance(data, list):
                print(f"Number of donations: {len(data)}")
                if len(data) > 0:
                    print(f"First donation: {data[0]}")
            else:
                print(f"Data: {data}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    verify_api()
