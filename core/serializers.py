from rest_framework import serializers
from .models import(
    SiteSettings,
    Skill,
    Service,
    Testimonial,
    Experience,
    Education,
    SocialLink,

)


class SiteSettingsSerializer(serializers.ModelSerializer):
     class Meta:
        model = SiteSettings
        fields = [
            'id', 'site_name', 'site_title', 'tagline',
            'bio', 'about_text', 'profile_image',
            'contact_email', 'phone', 'location',
            'resume_file',
            'github_url', 'linkedin_url', 'twitter_url', 'instagram_url',
            'meta_description', 'meta_keywords',
            'footer_text', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SkillSerializer(serializers.ModelSerializer):

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_display', read_only=True)

    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'category', 'category_display',
            'proficiency', 'proficiency_display',
            'icon', 'description', 'order', 'is_featured',
            'created_at', 'update_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    


class ServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for services offered.
    """
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'icon',
            'price', 'order', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestimonialSerializer(serializers.ModelSerializer):
    """
    Serializer for client testimonials with rating validation.
    """
    class Meta:
        model = Testimonial
        fields = [
            'id', 'client_name', 'client_position', 'client_company',
            'client_image', 'content', 'rating', 'project_related',
            'is_featured', 'is_approved', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'updated_at']



class ExperienceSerializer(serializers.ModelSerializer):

        employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
        duration = serializers.SerializerMethodField()

        class Meta:
            model =  Experience
            fields = [
            'id', 'company', 'position', 'employment_type', 'employment_type_display',
            'location', 'company_url', 'company_logo',
            'description', 'start_date', 'end_date', 'is_current',
            'duration', 'order',
            'created_at', 'updated_at'
        ]
            read_only_fields = ['id', 'created_at', 'updated_at']
        def get_duration(self, obj):

            from datetime import date

            start =  obj.start_date
            end = obj.end_date  if obj.end_date else date.today()


            years =  end.year - start.year

            months = end.month - start.month
            
            if months < 0:
                years -=1
                months +=12
            if years > 0 and months > 0:
                return f"{years} year{'s' if years > 1 else ''}{months} month{'s'if months >1 else ''}"
            elif years > 0:
                return f"{years} year{'s' if years > 1 else ''}"
            elif months > 0:
                return f"{months} month{'s' if years >1 else ''}"
            else:
                return "less than a month"
        def validate(self, data):
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            is_current = data.get('is_current', False)


            if is_current and end_date:
                raise serializers.ValidationError({
                    'end_date': 'End data should be empty for current job'

                })
            
            if not is_current and end_date and start_date and end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'

                })
            return data
class EducationSerializer(serializers.ModelSerializer):

    
    degree_display = serializers.CharField(source='get_degree_display', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Education
        fields = [
            'id', 'institution', 'degree', 'degree_display',
            'field_of_study', 'location', 'institution_logo',
            'description', 'gpa', 'start_date', 'end_date',
            'is_current', 'duration', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_duration(self, obj):
        
        from datetime import date
        
        start = obj.start_date
        end = obj.end_date if obj.end_date else date.today()
        
        years = end.year - start.year
        months = end.month - start.month
        
        if months < 0:
            years -= 1
            months += 12
        
        if years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        elif months > 0:
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return "Less than a month"
    
    def validate(self, data):
     
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        is_current = data.get('is_current', False)
        gpa = data.get('gpa')
        
     
        if is_current and end_date:
            raise serializers.ValidationError({
                'end_date': 'End date should be empty if currently studying'
            })
        
       
        if not is_current and end_date and start_date and end_date < start_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        
        if gpa is not None and (gpa < 0 or gpa > 4.00):
            raise serializers.ValidationError({
                'gpa': 'GPA must be between 0.00 and 4.00'
            })
        
        return data
class SocialLinkSerializer(serializers.ModelSerializer):

    platform_display = serializers.CharField(source='get_platform_display', read_only=      True)
    class Meta:
        model = SocialLink
        fields = [
            'id', 'platform', 'platform_display',
            'url', 'icon', 'order', 'is_visible',
            'created_at', 'upldated_at'

        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
