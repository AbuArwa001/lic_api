import requests
from django.conf import settings

class PaystackClient:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"

    def initialize_transaction(self, email, amount):
        """
        Initialize a transaction on Paystack
        amount: Amount in KES (will be converted to kobo/cents if needed, but Paystack expects base currency units usually? 
        Wait, Paystack expects amount in kobo (lowest currency unit). So KES 100 = 10000.
        """
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        # Convert amount to kobo/cents (multiply by 100)
        amount_in_kobo = int(float(amount) * 100)
        
        data = {
            "email": email,
            "amount": amount_in_kobo,
            "currency": "KES",
            # "callback_url": "..." # Optional, can be set in dashboard or here
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            print(f"Paystack Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                 return {"error": e.response.json().get('message', str(e))}
            return {"error": str(e)}

    def verify_transaction(self, reference):
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
             return {"error": str(e)}
