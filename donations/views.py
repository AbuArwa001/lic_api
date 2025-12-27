from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Donation, PaymentAccount
from .serializers import DonationSerializer, PaymentAccountSerializer
from .mpesa import MpesaClient
from .paypal import PayPalClient
from .stripe import StripeClient
from .paystack import PaystackClient

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        method = request.data.get('payment_method')
        amount = request.data.get('amount')
        phone = request.data.get('phone')
        email = request.data.get('email')
        project_id = request.data.get('project')


        if method == 'card':
            client = StripeClient()
            # 1. Create the Payment Intent in Stripe
            stripe_res = client.create_payment_intent(amount, metadata={"project_id": project_id})
            
            if "error" in stripe_res:
                return Response(stripe_res, status=status.HTTP_400_BAD_REQUEST)

            # 2. Record the donation in your DB as 'pending'
            donation = Donation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                project_id=project_id,
                amount=amount,
                payment_method='card',
                transaction_id=stripe_res['id'], # Store Stripe Intent ID
                status='pending'
            )
            
            # 3. Return client_secret so the frontend can finish the payment
            return Response({
                "client_secret": stripe_res['client_secret'],
                "donation_id": donation.id
            })
        elif method == 'mpesa':
            client = MpesaClient()
            response = client.stk_push(phone, amount, "Donation", "Donation to LIC")
            return Response(response)
        elif method == 'paypal':
            client = PayPalClient()
            response = client.create_payment(amount)
            return Response(response)
        elif method == 'paystack':
            client = PaystackClient()
            response = client.initialize_transaction(email, amount)
            return Response(response)
        
        return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

class PaymentAccountViewSet(viewsets.ModelViewSet):
    queryset = PaymentAccount.objects.all()
    serializer_class = PaymentAccountSerializer
    permission_classes = [permissions.IsAdminUser]
