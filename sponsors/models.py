from django.db import models


class Sponsor(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='sponsors')
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='sponsors/', blank=True, null=True)

    def __str__(self):
        return self.name
