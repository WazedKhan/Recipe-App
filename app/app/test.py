"""
sample test
"""
from django.test import SimpleTestCase

from app import calc


class CalcTest(SimpleTestCase):
    """Test the calc module"""

    def test_add_number(self):
        """Test adding two number together"""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_number(self):
        """Test substract two number together"""
        res = calc.substract(5, 6)

        self.assertEqual(res, 1)
