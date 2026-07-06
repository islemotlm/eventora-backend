from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed demo data for all user roles'

    def handle(self, *args, **options):
        from accounts.models import User
        from events.models import Event
        from speakers.models import Speaker
        from sponsors.models import Sponsor
        from organizers.models import Organizer
        from participants.models import Registration

        self.stdout.write('Seeding demo data...')

        # ── Users ────────────────────────────────────────────────
        admin = self._get_or_create_user('admin', 'admin@eventora.com', 'Admin', 'User', 'admin123', 'admin')
        client = self._get_or_create_user('client1', 'client@eventora.com', 'Alice', 'Martin', 'client123', 'client')
        organizer_user = self._get_or_create_user('organizer1', 'organizer@eventora.com', 'Bob', 'Smith', 'organizer123', 'organizer')
        participant = self._get_or_create_user('participant1', 'participant@eventora.com', 'Carol', 'Jones', 'participant123', 'participant')
        participant2 = self._get_or_create_user('participant2', 'participant2@eventora.com', 'David', 'Lee', 'participant123', 'participant')

        # ── Events ───────────────────────────────────────────────
        themes = ['modern', 'academic', 'techno', 'minimal', 'vibrant']
        events_data = [
            {
                'title': 'TechConf 2025',
                'description': 'Annual technology conference covering AI, cloud, and DevOps trends.',
                'date': timezone.now() + timedelta(days=30),
                'location': 'Palais des Congrès, Paris',
                'max_capacity': 200,
                'theme': 'modern',
                'status': 'approved',
            },
            {
                'title': 'Academic Summit 2025',
                'description': 'International academic conference on computer science research.',
                'date': timezone.now() + timedelta(days=60),
                'location': 'Sorbonne University, Paris',
                'max_capacity': 150,
                'theme': 'academic',
                'status': 'approved',
            },
            {
                'title': 'Startup Pitch Night',
                'description': 'Pitch your startup to investors and industry experts.',
                'date': timezone.now() + timedelta(days=15),
                'location': 'Station F, Paris',
                'max_capacity': 80,
                'theme': 'vibrant',
                'status': 'pending',
            },
            {
                'title': 'Corporate Leadership Forum',
                'description': 'Executive forum on leadership, strategy, and innovation.',
                'date': timezone.now() - timedelta(days=10),
                'location': 'Marriott Hotel, Lyon',
                'max_capacity': 100,
                'theme': 'techno',
                'status': 'approved',
            },
        ]

        created_events = []
        for ed in events_data:
            event, created = Event.objects.get_or_create(
                title=ed['title'],
                defaults={**ed, 'client': client}
            )
            created_events.append(event)
            if created:
                self.stdout.write(f'  Created event: {event.title}')

        # ── Speakers ─────────────────────────────────────────────
        speakers_data = [
            {'first_name': 'Marie', 'last_name': 'Curie', 'title': 'AI Research Lead', 'bio': 'Pioneer in machine learning.'},
            {'first_name': 'Alan', 'last_name': 'Turing', 'title': 'Cryptography Expert', 'bio': 'Father of computer science.'},
            {'first_name': 'Grace', 'last_name': 'Hopper', 'title': 'Software Architect', 'bio': 'Creator of the first compiler.'},
        ]
        for i, sd in enumerate(speakers_data):
            event = created_events[i % len(created_events)]
            Speaker.objects.get_or_create(
                event=event,
                first_name=sd['first_name'],
                last_name=sd['last_name'],
                defaults={**sd, 'schedule_time': event.date + timedelta(hours=i)},
            )

        # ── Sponsors ─────────────────────────────────────────────
        sponsors = [('TechCorp', created_events[0]), ('EduFund', created_events[1]), ('VentureX', created_events[2])]
        for name, event in sponsors:
            Sponsor.objects.get_or_create(event=event, name=name)

        # ── Organizers ───────────────────────────────────────────
        if not Organizer.objects.filter(user=organizer_user).exists():
            Organizer.objects.create(
                event=created_events[0],
                user=organizer_user,
                door_number='A1',
                work_schedule='09:00-18:00',
            )
            self.stdout.write('  Created organizer assignment')

        # ── Registrations ────────────────────────────────────────
        approved_events = [e for e in created_events if e.status == 'approved']
        for ev in approved_events[:2]:
            for p in [participant, participant2]:
                reg, created = Registration.objects.get_or_create(event=ev, participant=p)
                if created:
                    self.stdout.write(f'  Registered {p.username} for {ev.title}')

        # Mark some as present (past event)
        past_event = next((e for e in created_events if e.date < timezone.now()), None)
        if past_event:
            Registration.objects.filter(event=past_event).update(is_present=True)

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write('\n── Demo Credentials ─────────────────────────')
        self.stdout.write('Admin:       admin / admin123')
        self.stdout.write('Client:      client1 / client123')
        self.stdout.write('Organizer:   organizer1 / organizer123')
        self.stdout.write('Participant: participant1 / participant123')
        self.stdout.write('─────────────────────────────────────────────\n')

    def _get_or_create_user(self, username, email, first_name, last_name, password, role):
        from accounts.models import User
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  Created {role}: {username}')
        return user
