from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail  import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ConctactMessageSerializer

class ContactMessageCreateView(generics.CreateAPIView):
    serializer_class = ConctactMessageSerializer
    permission_classes = [permissions.AllowAny]
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact_message = serializer.save()

        try:
            self.send_notification_email(contact_message)
        except Exception as e:
            print(f"Email sending failed: {e}")
        return Response({
            'message': 'Thank you for contacting us!We will get back to you soon',
            'data': serializer.data

        }, status=status.HTTP_201_CREATED)
    def send_notification_email(self, contact_message):
        subject = f"New Contact Message:{contact_message.subject}"
        message = f"""
        New contact message received:
        Name: {contact_message.name}
        Email : {contact_message.email}
        phone : {contact_message.phone or 'Not provided'}
        Subject: {contact_message.subject}
    Message: 
    {contact_message.message}
    """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False

        )

class ContactMessageListView(generics.ListAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ConctactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
class ContactMessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ConctactMessageSerializer
    permission_classes = [permissions.IsAdminUser]
    
# Create your views here.
