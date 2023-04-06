from datetime import datetime
from django.test import TestCase

from .servises.servises import add_date_delta, get_ofset_number, set_fixed_args_date, get_ofset_params_date, get_fixed_number, get_fixed_params_date, get_data_with_working_day
from .servises.export_in_doc import *


class ServisesTestCase(TestCase):
    def test_add_date_delta(self):
        date = datetime(day=1, month=1, year=2023)
        first = add_date_delta(date=date, days=5, months=-1, years=-6)
        self.assertEqual(first, datetime(day=6, month=12, year=2016))

        date = datetime(day=1, month=1, year=2023)
        first = add_date_delta(date=date, days=22, months=1, years=1)
        self.assertEqual(first, datetime(day=23, month=2, year=2024))

        date = datetime(day=1, month=1, year=2023)
        first = add_date_delta(date=date, days=0, months=0, years=0)
        self.assertEqual(first, datetime(day=1, month=1, year=2023))

    def test_get_ofset_number(self):
        first = get_ofset_number('+1')
        self.assertEqual(first, 1)

        first = get_ofset_number('-3')
        self.assertEqual(first, -3)

        first = get_ofset_number('2')
        self.assertEqual(first, 0)

    def test_get_ofset_params_date(self):
        first = get_ofset_params_date(days='+1', months='5', years='-1')
        self.assertEqual(first, {'days': 1, 'months': 0, 'years': -1})

    
    def test_get_fixed_number(self):
        first = get_fixed_number('+1')
        self.assertEqual(first, 0)

        first = get_fixed_number('-3')
        self.assertEqual(first, 0)

        first = get_fixed_number('2')
        self.assertEqual(first, 2)

    def test_set_fixed_args_date(self):
        date = datetime(day=1, month=1, year=2023)
        first = set_fixed_args_date(date=date, days=-1, months=-2, years=-3)
        self.assertEqual(first, date)

        date = datetime(day=1, month=1, year=2023)
        first = set_fixed_args_date(date=date, days=5, months=6, years=2025)
        self.assertEqual(first, datetime(day=5, month=6, year=2025))

        date = datetime(day=1, month=1, year=2023)
        first = set_fixed_args_date(date=date, days=0, months=0, years=0)
        self.assertEqual(first, date)

        date = datetime(day=1, month=1, year=2023)
        first = set_fixed_args_date(date=date, days=50, months=6, years=2025)
        self.assertEqual(first, datetime(day=30, month=6, year=2025))

    def test_get_fixed_params_date(self):
        first = get_fixed_params_date(days='+1', months='5', years='-1')
        self.assertEqual(first, {'days': 0, 'months': 5, 'years': 0})

    def test_get_data_with_working_day(self):
        first = get_data_with_working_day(datetime(day=23, month=2, year=2023))
        self.assertEqual(first, datetime(day=22, month=2, year=2023))

        first = get_data_with_working_day(datetime(day=15, month=3, year=2023))
        self.assertEqual(first, datetime(day=15, month=3, year=2023))

        first = get_data_with_working_day(datetime(day=19, month=3, year=2023))
        self.assertEqual(first, datetime(day=17, month=3, year=2023))


class ExportInDocTestCase(TestCase):
    def test_word_doc(self):
        pass