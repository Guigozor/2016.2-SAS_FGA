from django.test import TestCase
from booking.models import *
from django.test import Client
from booking.factories import *
from datetime import datetime
from user.factories import UserFactory

class TestBookTime(TestCase):

	def test_add_days(self):
		book = BookTime()
		book.date_booking = datetime.strptime("01022010", "%d%m%Y")
		book.add_days(5)
		self.assertEqual(book.date_booking.strftime("%d%m%Y"), "06022010")

	def test_next_week_day(self):
		book = BookTime()
		book.date_booking = datetime.strptime("21092016", "%d%m%Y")
		book.next_week_day(4)
		self.assertEqual(book.date_booking.strftime("%d%m%Y"), "23092016")
		book.date_booking = datetime.strptime("21092016", "%d%m%Y")
		book.next_week_day(2)
		self.assertEqual(book.date_booking.strftime("%d%m%Y"), "28092016")
		book.date_booking = datetime.strptime("20092016", "%d%m%Y")
		book.next_week_day(0)
		self.assertEqual(book.date_booking.strftime("%d%m%Y"), "26092016")

	def test_get_str_weekday(self):
		book = BookTime()
		book.date_booking = datetime.strptime("21092016", "%d%m%Y")
		self.assertEqual(book.get_str_weekday(), "Wednesday")


class TestBooking(TestCase):

	def setUp(self):
		self.booking = Booking()

	def test_save(self):
		self.booking.user = UserFactory.create()
		self.booking.name = "Teste"
		self.booking.start_date = datetime.now()
		self.booking.end_date = datetime.now()
		self.booking.place = PlaceFactory.create()
		self.booking.save()
		self.assertEqual(self.booking.pk, 1)