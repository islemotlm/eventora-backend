from django.test import SimpleTestCase

from .models import ExhibitorStand


class ExhibitorStandPriceTests(SimpleTestCase):
    def test_medium_stand_price_is_2000(self):
        stand = ExhibitorStand(stand_type='medium')
        self.assertEqual(stand.price, 2000)

    def test_standard_and_premium_prices_are_updated(self):
        medium_stand = ExhibitorStand(stand_type='medium')
        standard_stand = ExhibitorStand(stand_type='standard')
        premium_stand = ExhibitorStand(stand_type='premium')

        self.assertEqual(medium_stand.price, 2000)
        self.assertEqual(standard_stand.price, 3500)
        self.assertEqual(premium_stand.price, 4500)
