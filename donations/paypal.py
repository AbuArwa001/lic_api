class PayPalClient:
    def create_payment(self, amount, currency="USD"):
        print(f"Creating PayPal payment for {amount} {currency}")
        return {"payment_id": "dummy_paypal_id", "approval_url": "https://www.sandbox.paypal.com/..."}
