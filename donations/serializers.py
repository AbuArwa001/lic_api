from rest_framework import serializers
from .models import Donation, PaymentAccount

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'
        read_only_fields = ['id', 'donation_date', 'status']

class PaymentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAccount
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
