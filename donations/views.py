import requests
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Donation, PaymentAccount
from .serializers import DonationSerializer, PaymentAccountSerializer
from .mpesa import MpesaClient
from .paypal import PayPalClient
from .stripe import StripeClient
from .paystack import PaystackClient
from .permissions import IsAdminOrReadOnly, IsAdminUser, AllowAll, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [AllowAll]
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return [AllowAll()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['post'], )
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
            try:
                order_data = client.create_order(amount)
                return Response({"id": order_data['id']})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif method == 'paystack':
            client = PaystackClient()
            response = client.initialize_transaction(email, amount)
            return Response(response)
        
        return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def capture_paypal_payment(self, request):
        order_id = request.data.get('orderID')
        client = PayPalClient()
        
        try:
            capture_data = client.capture_payment(order_id)
            
            if capture_data['status'] == 'COMPLETED':
                # Update your database
                # Note: We might want to find the donation by order_id if we stored it during initiate
                # But currently initiate doesn't store for PayPal, so we might need to create it here or handle it differently.
                # For now, let's assume we create it here or find it if we change the flow.
                # Given the current flow, we probably want to create the donation record here if it doesn't exist,
                # or update it if we stored the order_id.
                
                # Let's check if we can find a donation with this transaction_id, if not create one.
                # But wait, initiate_payment didn't create a donation for PayPal.
                # We should probably create it here.
                
                donation, created = Donation.objects.get_or_create(
                    transaction_id=order_id,
                    defaults={
                        'user': request.user if request.user.is_authenticated else None,
                        'amount': capture_data['purchase_units'][0]['payments']['captures'][0]['amount']['value'],
                        'payment_method': 'paypal',
                        'status': 'completed'
                    }
                )
                
                if not created:
                    donation.status = 'completed'
                    donation.save()
                    
                return Response({"status": "COMPLETED", "donation_id": donation.id})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Failed to capture payment"}, status=400)

class PaymentAccountViewSet(viewsets.ModelViewSet):
    queryset = PaymentAccount.objects.all()
    serializer_class = PaymentAccountSerializer
    permission_classes = [permissions.IsAdminUser]
