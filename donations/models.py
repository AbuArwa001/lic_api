from django.db import models
from django.conf import settings
from projects.models import Project
import uuid

class Donation(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('paystack', 'Paystack'),
        ('card', 'Card'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    donation_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    is_anonymous = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"{self.amount} to {self.project.name}"

class PaymentAccount(models.Model):
    TYPE_CHOICES = [
        ('paybill', 'Paybill'),
        ('paypal', 'PayPal'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255) # e.g., "Main M-Pesa Paybill"
    account_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Store details as JSON to be flexible (e.g., paybill number, account number, paypal email)
    # For Paybill: {"business_number": "...", "account_number": "..."}
    # For PayPal: {"email": "...", "client_id": "..."}
    details = models.JSONField(default=dict)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"
