from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from user.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class TimestampModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Blog(TimestampModel):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Published', 'Published'),
        ('Archived', 'Archived'),
    ]

    cover = models.ImageField(upload_to='blog')
    title = models.CharField(max_length=100000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    snippet = models.TextField()
    body = RichTextUploadingField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_list')

class Comment(TimestampModel):
    blog = models.ForeignKey(Blog, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    body = models.TextField()

    def __str__(self):
        return self.blog.title

class Speaker(TimestampModel):
    name = models.CharField(max_length=100)
    bio = models.TextField(help_text="Brief biography of the speaker")
    photo = models.ImageField(upload_to='speaker_photos/%Y/%m/%d/', blank=True, null=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Webinar(TimestampModel):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('live', 'Live'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    featured_image = models.ImageField(upload_to='webinar_images/%Y/%m/%d/',help_text="Recommended size: 1200x675 pixels")
    start_datetime = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes",validators=[MinValueValidator(5), MaxValueValidator(480)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],default=0)
    is_featured = models.BooleanField(default=False)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hosted_webinars')
    speakers = models.ManyToManyField(Speaker, related_name='webinars')
    meeting_url = models.URLField(blank=True, help_text="Zoom/Google Meet link")
    recording_url = models.URLField(blank=True, help_text="Link to webinar recording")
    
    class Meta:
        ordering = ['-start_datetime']
        indexes = [
            models.Index(fields=['status', 'start_datetime']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('webinar_detail', kwargs={'pk': self.id})

    @property
    def is_free(self):
        return self.price == 0
    
    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.duration)
    
    def is_upcoming(self):
        return self.status == 'upcoming' and self.start_datetime > timezone.now()
    
    def is_live(self):
        now = timezone.now()
        return (self.status == 'live' or 
                (self.status == 'upcoming' and 
                 self.start_datetime <= now <= self.end_datetime))
  
class WebinarRegistration(TimestampModel):
    status_choices = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "cancelled"),
    )

    webinar = models.ForeignKey(Webinar, related_name='registrations', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=255, choices=status_choices)
    question = models.TextField(verbose_name="Any questions for the speaker", blank=True, null=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.FileField(upload_to="payment", verbose_name="Proof of Payment", blank=True, null=True)
    
    class Meta:
        unique_together = ('webinar', 'email')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.webinar.title}"
