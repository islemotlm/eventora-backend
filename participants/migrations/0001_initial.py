import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
                ('is_present', models.BooleanField(default=False)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('ticket_sent', models.BooleanField(default=False)),
                ('event', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registrations',
                    to='events.event',
                )),
                ('participant', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registrations',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'unique_together': {('event', 'participant')},
            },
        ),
    ]
