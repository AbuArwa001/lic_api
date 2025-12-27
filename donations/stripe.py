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