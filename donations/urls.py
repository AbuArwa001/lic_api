from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationViewSet, PaymentAccountViewSet
from .mpesa import MpesaClient

router = DefaultRouter()
router.register(r'accounts', PaymentAccountViewSet)
router.register(r'donations', DonationViewSet)
# Register the MpesaClient ViewSet
router.register(r'mpesa', MpesaClient, basename='mpesa') 

urlpatterns = [
    path('', include(router.urls)),
]