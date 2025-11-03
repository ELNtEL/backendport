from django.db import models

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'archived'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject =  models.CharField(max_length=200)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'contact messages'
    def __str__(self):
        return f"{self.name} - {self.subject}"        
# Create your models here.
