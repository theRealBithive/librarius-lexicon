from django.db import models
from django.utils import timezone


class Audiobook(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('pending', 'Pending Clarification'),
        ('processed', 'Processed'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    series = models.CharField(max_length=255, blank=True)
    narrator = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    input_path = models.CharField(max_length=512)
    output_path = models.CharField(max_length=512, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author}"


