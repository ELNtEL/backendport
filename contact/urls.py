from django.urls import path
from .views import (
    ContactMessageCreateView,
    ContactMessageListView,
    ContactMessageDetailView
)

urlpatterns = [
    path('', ContactMessageCreateView.as_view(), name='contact-create'),
    path('messages/', ContactMessageListView.as_view(), name='contact-list'),
    path('messages/<int:pk>/', ContactMessageDetailView.as_view(), name='contact-detail'),
]