from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageSerializer
from rest_framework.permissions import AllowAny

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        
        # Send email to admin
        subject = f"New Contact Message from {instance.first_name} {instance.last_name}"
        message = f"Name: {instance.first_name} {instance.last_name}\nEmail: {instance.email}\n\nMessage:\n{instance.message}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@langataislamiccenter.org')
        recipient_list = ['admin@langataislamiccenter.org']
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            # We don't want to fail the request if email fails, but we should log it
            print(f"Error sending email: {e}")
