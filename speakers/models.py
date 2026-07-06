from django.db import models


class Speaker(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='speakers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    cv_image = models.ImageField(upload_to='speakers/cvs/', blank=True, null=True)
    photo = models.ImageField(upload_to='speakers/', blank=True, null=True)
    schedule_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
