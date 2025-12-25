class PaystackClient:
    def initialize_transaction(self, email, amount):
        print(f"Initializing Paystack transaction for {email}, amount: {amount}")
        return {"authorization_url": "https://checkout.paystack.com/...", "access_code": "dummy_access_code"}
