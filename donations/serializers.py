from rest_framework import serializers
from .models import Donation, PaymentAccount
from projects.models import Project
from users.models import User
class DonationSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), 
        required=False
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    payment_method = serializers.CharField(required=False)
    class Meta:
        model = Donation
        fields = [
            'id', 'user', 'project', 'amount', 'donation_date', 
            'payment_method', 'is_anonymous', 'transaction_id', 'status'
        ]
        read_only_fields = ['id', 'donation_date']

class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = ['id', 'name', 'account_type', 'details', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
