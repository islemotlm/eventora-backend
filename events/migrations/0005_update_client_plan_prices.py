from decimal import Decimal

from django.db import migrations


def update_plan_prices(apps, schema_editor):
    Plan = apps.get_model('events', 'Plan')
    price_map = {
        'medium': Decimal('500.00'),
        'premium': Decimal('2000.00'),
        'pro': Decimal('3000.00'),
    }

    for plan in Plan.objects.all():
        normalized_name = (plan.name or '').strip().lower()
        if normalized_name in price_map:
            plan.price = price_map[normalized_name]
            plan.save(update_fields=['price'])


class Migration(migrations.Migration):
    dependencies = [
        ('events', '0004_plan_clientpayment_event_plan'),
    ]

    operations = [
        migrations.RunPython(update_plan_prices, migrations.RunPython.noop),
    ]
