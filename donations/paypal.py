import requests
from django.conf import settings

class PayPalClient:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.base_url = "https://api-m.sandbox.paypal.com" if settings.DEBUG else "https://api-m.paypal.com"

    def get_access_token(self):
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
        )
        return response.json().get("access_token")

    def create_order(self, amount, currency="USD"):
        token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{"amount": {"currency_code": currency, "value": str(amount)}}]
        }
        response = requests.post(f"{self.base_url}/v2/checkout/orders", json=payload, headers=headers)
        return response.json().get("id")