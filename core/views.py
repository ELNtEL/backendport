from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    SiteSettings,
    Skill,
    Service,
    Testimonial,
    Experience,
    Education,
    SocialLink,
)
from .serializers import (
    SiteSettingsSerializer,
    SkillSerializer,
    ServiceSerializer,
    TestimonialSerializer,
    ExperienceSerializer,
    EducationSerializer,
    SocialLinkSerializer,
    
)

class SiteSettingsView(APIView):


    permission_classes = [permissions.AllowAny]

    def get(self, request):

        try:
            settings = SiteSettings.objects.first()
            if settings:
                serializer = SiteSettingsSerializer(settings)
                return Response(serializer.data)
            return response({
                'message': 'Site settings not configured yet'

            },status=404)
        except Exception as e:
            return Response({
                'error': str(e)

            }, status=500)
        
class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        queryset =Skill.objects.all()
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)


            proficiency = self.request.query_params.get('preficiency', None)
            if proficiency:
                queryset = queryset.filter(proficiency=proficiency)
            is_featured = self.request.query_params.get('featured', None)
            if is_featured:
                queryset = queryset.filter(is_featured=True)
            return queryset
class SkillDetailView(generics.RetrieveAPIView):
    queryset = Skill.objects.all
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
class SerivceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]
class TestimonialSerializer(generics.ListCreateAPIView):

    queryset + Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        queryset = Testimonial.objects.filter(is_approved=True)

        is_featured = self.request.query_params.get('featured', None)
        if is_featured:
            queryset = queryset.filter(is_featured=True)
        return queryset
class TestimonialDetailView(generics.RetrieveAPIView):
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
class ExperienceListView(generics.ListAPIView):


    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Experience.objects.all()

        employment_type = self.request.query_params.get('type', None)
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        is_current = self.request.query_params.get('current', None)
        if is_current:
            queryset = queryset.filter(is_current=True)
        return queryset
class ExperienceDetailView(generics.RetrieveAPIView):

    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.AllowAny]
class EducationListView(generics.ListAPIView):


    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        queryset = Education.objects.all()

        degree = queryset.filter('degree', None)
        if degree:
            queryset = queryset.filter(degree=degree)
        is_current  = self.request.query_params.get('current', None)
        if is_current:
            queryset = queryset.filter(is_current=True)
        return queryset
class EducationDetailView(generics.RetrieveAPIView):

    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.AllowAny]

class SocialLinkView(generics.ListAPIView):

    queryset = SocialLink.objects.filter(is_visible=True)
    serializer_class = SocialLinkSerializer
    permission_classes = [permissions.AllowAny]
class SocialLinkDetailView(generics.RetrieveAPIView):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer
    permission_classes =[permissions.AllowAny]





# Create your views here.
