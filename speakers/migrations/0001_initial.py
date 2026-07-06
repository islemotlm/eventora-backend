import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=200)),
                ('bio', models.TextField(blank=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='speakers/')),
                ('schedule_time', models.DateTimeField(blank=True, null=True)),
                ('event', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='speakers',
                    to='events.event',
                )),
            ],
        ),
    ]
