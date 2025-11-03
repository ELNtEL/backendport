from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError



class TimeStampedModel(models.Model):


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SiteSettings(TimeStampedModel):


    site_name= models.CharField(max_length=100, default="My Portfolio")
    site_title = models.CharField(max_length=200, help_text="Browser tab title")
    tagline = models.CharField(max_length=200, help_test="short description/slogan")


    bio = models.TextField(help_text="short bio for homepage")
    about_text = models.TextField(help_text="Detailed about text")
    profile_image = models.ImageField(upload_to='profile', blank=True, null=True)


    contact_email = models.EmailField()
    phone  = models.CharField(max_length=20, blank=True)
    location =  models.CharField(max_length=100, blank=True, help_text="City, Country")


    resume_file = models.FileField(upload_to='resume/', blank=True, null=True)


    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    instagram_url = models.URLField(blank=True)


    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    footer_text = models.CharField(max_length=200, default="@ 2024 all rights reserved")

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name= "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError("Only one siteSettings instance is allowed")
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.site_name


class Skill(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('database', 'Database'),
        ('devops', 'DevOps'),
        ('tools', 'Tools'),
        ('other', 'Other'),
    ]
    
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='intermediate')
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class or emoji")
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    is_featured = models.BooleanField(default=False, help_text="show on homepage")

    class Meta:
        ordering = ['order', 'name']
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class Service(TimeStampedModel):


    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.DecimalField(max_digits=10, decimal_places=2, blank=True,null=True, help_text="optional")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
    def __str__(self):
        return self.title
class Testimonial(TimeStampedModel):
    client_name = models.CharField(max_length=100)
    client_position = models.CharField(max_length=100, help_text="e.g., CEO at TechCorp")
    client_company = models.CharField(max_length=100, blank=True)
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    
    content = models.TextField(help_text="The testimonial text")
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    
    project_related = models.CharField(max_length=200, blank=True, help_text="Which project this relates to")
    
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True, help_text="Admin approval")
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.client_name} - {self.rating}⭐"


class Experience(TimeStampedModel):
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100, help_text="Job title")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    location = models.CharField(max_length=100, blank=True)
    company_url = models.URLField(blank=True)
    company_logo = models.ImageField(upload_to='experience/', blank=True, null=True)
    
    description = models.TextField(help_text="Responsibilities and achievements")
    
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if current job")
    is_current = models.BooleanField(default=False, help_text="Currently working here")
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Experiences"
    
    def __str__(self):
        return f"{self.position} at {self.company}"
    
    def save(self, *args, **kwargs):
        """Auto-set end_date to None if current job"""
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)
class Education(TimeStampedModel):
    """
    Educational background
    """
    DEGREE_TYPE_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor Degree'),
        ('master', 'Master Degree'),
        ('phd', 'PhD'),
        ('certification', 'Certification'),
        ('bootcamp', 'Bootcamp'),
        ('other', 'Other'),
    ]
    
    institution = models.CharField(max_length=200, help_text="School/University name")
    degree = models.CharField(max_length=20, choices=DEGREE_TYPE_CHOICES)
    field_of_study = models.CharField(max_length=100, help_text="e.g., Computer Science")
    location = models.CharField(max_length=100, blank=True)
    institution_logo = models.ImageField(upload_to='education/', blank=True, null=True)
    
    description = models.TextField(blank=True, help_text="Achievements, coursework, etc.")
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, help_text="e.g., 3.85")
    
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True, help_text="Leave blank if in progress")
    is_current = models.BooleanField(default=False, help_text="Currently studying")
    
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Education"
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} - {self.institution}"
    
    def save(self, *args, **kwargs):
        """Auto-set end_date to None if currently studying"""
        if self.is_current:
            self.end_date = None
        super().save(*args, **kwargs)


class SocialLink(TimeStampedModel):
    """
    Social media and professional profile links
    """
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('medium', 'Medium'),
        ('dev', 'Dev.to'),
        ('stackoverflow', 'Stack Overflow'),
        ('dribbble', 'Dribbble'),
        ('behance', 'Behance'),
        ('other', 'Other'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    icon = models.CharField(max_length=50, blank=True, help_text="CSS class or emoji")
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'platform']
    
    def __str__(self):
        return f"{self.get_platform_display()}"


  

# Create your models here.
