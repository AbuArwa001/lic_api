import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeClient:
    def create_payment_intent(self, amount, currency='kes', metadata=None):
        try:
            # Stripe amounts are in cents/smallest unit (e.g. 1000 = 10.00 KES)
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),
                currency=currency,
                metadata=metadata or {},
                payment_method_types=['card'],
            )
            return {
                "client_secret": intent.client_secret,
                "id": intent.id
            }
        except Exception as e:
            return {"error": str(e)}

    def get_balance(self):
        try:
            balance = stripe.Balance.retrieve()
            # Return available balance in first currency found (usually default)
            available = balance['available'][0]
            return {
                "amount": available['amount'] / 100, # Convert cents to main unit
                "currency": available['currency']
            }
        except Exception as e:
            return {"error": str(e)}

    def get_transactions(self, limit=10):
        try:
            transactions = stripe.BalanceTransaction.list(limit=limit)
            return [
                {
                    "id": t.id,
                    "amount": t.amount / 100,
                    "currency": t.currency,
                    "status": t.status,
                    "created": t.created,
                    "description": t.description or t.type
                }
                for t in transactions.auto_paging_iter()
            ][:limit]
        except Exception as e:
            return {"error": str(e)}