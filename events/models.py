from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid

class Plan(models.Model):
    name = models.CharField(max_length=50) # e.g., Medium, Premium, Pro
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} - {self.price}"

class ClientPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    receipt_image = models.ImageField(upload_to='receipts/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.username} - {self.plan.name} ({self.status})"
class Event(models.Model):
    THEME_CHOICES = [
        ('modern', 'Modern'),
        ('academic', 'Academic'),
        ('techno', 'Techno'),
        ('minimal', 'Minimal'),
        ('vibrant', 'Vibrant'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    TICKET_TYPE_CHOICES = [
        ('free', 'Free'),
        ('paid', 'Paid'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=300)
    max_capacity = models.PositiveIntegerField(default=100)
    logo = models.ImageField(upload_to='event_logos/', blank=True, null=True)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='modern')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES, default='free')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ccp_number = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(unique=True, blank=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events'
    )
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
