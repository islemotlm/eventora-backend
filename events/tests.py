from decimal import Decimal

from django.test import SimpleTestCase

from .models import Plan
from .serializers import PlanSerializer


class PlanPricingTests(SimpleTestCase):
    def test_plan_serializer_uses_client_subscription_prices(self):
        plan = Plan(name='Premium', price=Decimal('999.99'))
        data = PlanSerializer(plan).data

        self.assertEqual(data['price'], '2000.00')
