from django.db import models
from django.conf import settings


class Organizer(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='organizers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organizer_assignments')
    door_number = models.CharField(max_length=50)
    work_schedule = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} – {self.event.title}"
