import requests
from django.conf import settings

class PayPalClient:
    def __init__(self):
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self.environment = settings.PAYPAL_MODE
        self.base_url = "https://api-m.sandbox.paypal.com" if self.environment == "sandbox" else "https://api-m.paypal.com"
        # self.check_environment()

    def check_environment(self):
        print(self.environment)
        print(self.base_url)
        print(self.client_id)
        print(self.client_secret)

    def get_access_token(self):
        response = requests.post(
            f"{self.base_url}/v1/oauth2/token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
        )
        response.raise_for_status()
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
        response.raise_for_status()
        return response.json()

    def capture_payment(self, order_id):
        token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(f"{self.base_url}/v2/checkout/orders/{order_id}/capture", headers=headers)
        response.raise_for_status()
        return response.json()

    def get_balance(self):
        try:
            token = self.get_access_token()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            # PayPal Balances API
            response = requests.get(f"{self.base_url}/v1/reporting/balances", headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Find primary currency balance
            for balance in data.get('balances', []):
                if balance.get('primary', False):
                    return {
                        "amount": float(balance['total_balance']['value']),
                        "currency": balance['total_balance']['currency_code']
                    }
            
            # Fallback to first if no primary
            if data.get('balances'):
                balance = data['balances'][0]
                return {
                    "amount": float(balance['total_balance']['value']),
                    "currency": balance['total_balance']['currency_code']
                }
                
            return {"amount": 0.0, "currency": "USD"}
            
        except Exception as e:
            return {"error": str(e)}

    def create_payout(self, amount, receiver, receiver_type="EMAIL", currency="USD"):
        try:
            token = self.get_access_token()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            
            # PayPal Payouts API
            payload = {
                "sender_batch_header": {
                    "sender_batch_id": f"Payouts_{amount}_{receiver}",
                    "email_subject": "You have a payout!",
                    "email_message": "You have received a payout! Thanks for using our service."
                },
                "items": [
                    {
                        "recipient_type": receiver_type,
                        "amount": {
                            "value": str(amount),
                            "currency": currency
                        },
                        "note": "Thanks for your patronage!",
                        "receiver": receiver,
                        "sender_item_id": "201403140001",
                    }
                ]
            }
            
            response = requests.post(f"{self.base_url}/v1/payments/payouts", json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {"error": str(e)}

    def get_transactions(self, start_date=None, end_date=None):
        try:
            token = self.get_access_token()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            
            # Default to last 30 days if not provided
            if not start_date:
                from datetime import datetime, timedelta
                end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-0000")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S-0000")

            params = {
                "start_date": start_date,
                "end_date": end_date,
                "fields": "all"
            }
            
            response = requests.get(f"{self.base_url}/v1/reporting/transactions", headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            transactions = []
            for t in data.get('transaction_details', []):
                info = t.get('transaction_info', {})
                transactions.append({
                    "id": info.get('transaction_id'),
                    "amount": float(info.get('transaction_amount', {}).get('value', 0)),
                    "currency": info.get('transaction_amount', {}).get('currency_code'),
                    "status": info.get('transaction_status'),
                    "created": info.get('transaction_initiation_date'),
                    "description": info.get('transaction_note') or info.get('transaction_subject')
                })
                
            return transactions
            
        except Exception as e:
            return {"error": str(e)}