from django.utils.translation import ugettext as _
from django.forms import ModelForm
from .models import Booking, BookTime, Place, Building
from .models import WEEKDAYS
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, datetime, timedelta
from booking.models import date_range
import copy

class SearchBookingForm(forms.Form):
	SEARCH_CHOICES = (
        ('opt_day_room', ' Day x Room'),
        ('opt_booking_week', ' Booking x Week'),
		('opt_building_day', ' Building x Day'),
		('opt_room_period', ' Room x Period'),
    )

	search_options = forms.ChoiceField(choices=SEARCH_CHOICES,widget=forms.RadioSelect())

	start_date = forms.DateField(
		label=_('Start Date:'),
		widget=forms.widgets.DateInput(attrs={'placeholder': ''}), required=False)

	booking_name = forms.CharField(
		label=_('Booking Name:'),
		widget=forms.TextInput(attrs={'placeholder': ''}), required=False)

	room_name = forms.ModelChoiceField(queryset=Place.objects, label=_('Place:'), required=False)
	building_name = forms.ModelChoiceField(
		queryset=Building.objects,
		label=_('Building:'), required=False)

	start_date = forms.DateField(
		label=_('Start Date:'),
		widget=forms.widgets.DateInput(attrs={'placeholder': ''}), required=False)

	end_date = forms.DateField(
		label=_('End Date:'),
		widget=forms.widgets.DateInput(attrs={'placeholder': ''}), required=False)

	def clean(self):
		cleaned_data = super(SearchBookingForm,self).clean()
		today = date.today()
		now = datetime.now()

		try:
			option = cleaned_data.get('search_options')
			start_date = cleaned_data.get('start_date')

			if(option == 'opt_building_day'):
				building_name = cleaned_data.get('building_name').name
				if not Building.objects.filter(name=building_name).exists():
					msg = _('Doesnt exist any building with this name')
					self.add_error('building_name', msg)
					raise forms.ValidationError(msg)
			if(option == 'opt_day_room' or option == 'opt_room_period'):
				room_name = cleaned_data.get('room_name').name
				if not Place.objects.filter(name=room_name).exists():
					msg = _('Doesnt exist any room with this name')
					self.add_error('room_name', msg)
					raise forms.ValidationError(msg)

			if(option == 'opt_booking_week'):
				booking_name = cleaned_data.get('booking_name')
				if not Booking.objects.filter(name=booking_name).exists():
					msg = _('Doesnt exist any booking with this name')
					self.add_error('booking_name', msg)
					raise forms.ValidationError(msg)

			if(option == 'opt_room_period'):
				end_date = cleaned_data.get('end_date')
				if not(today <= start_date <= end_date):
					msg = _('Invalid booking period: Booking must be in future date')
					self.add_error('start_date', msg)
					self.add_error('end_date', msg)
					raise forms.ValidationError(msg)

				elif(end_date < start_date):
					msg = _('End date must be after Start date')
					self.add_error('start_date', msg)
					self.add_error('end_date', msg)
					raise forms.ValidationError(msg)

		except Exception as e:
			msg = _('Inputs are in invalid format')
			print(e)
			raise forms.ValidationError(msg)

class SearchBooking(forms.Form):
    room_name = forms.CharField(
         label=_('Room Name:'),
         widget=forms.TextInput(attrs={'placeholder': ''}))
    start_date = forms.DateField(
         label=_('Start Date:'),
         widget=forms.widgets.DateInput(attrs={'placeholder': ''}))
    end_date = forms.DateField(
         label=_('End Date:'),
         widget=forms.widgets.DateInput(attrs={'placeholder': ''}))

    def search(self):
        cleaned_data = super(SearchBooking,self).clean()
        all_bookings = Booking.objects.all()
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        bookings = []

        for booking in all_bookings:
            if not(booking.end_date < start_date or booking.start_date > end_date):
                bookings.append(booking)

        return bookings


class BookingForm(forms.Form):
	name = forms.CharField(
		label=_('Booking Name:'),
		widget=forms.TextInput(attrs={'placeholder': ''}))
	start_hour = forms.TimeField(
		label=_('Start Time:'),
		widget=forms.widgets.TimeInput(attrs={'placeholder': ''}))
	end_hour = forms.TimeField(
		label=_('End Time:'),
		widget=forms.widgets.TimeInput(attrs={'placeholder': ''}))
	start_date = forms.DateField(
		label=_('Start Date:'),
		widget=forms.widgets.DateInput(attrs={'placeholder': ''}))
	end_date = forms.DateField(
		label=_('End Date:'),
		widget=forms.widgets.DateInput(attrs={'placeholder': ''}))
	building = forms.ModelChoiceField(
		queryset=Building.objects,
		label=_('Building:'))
	place = forms.ModelChoiceField(queryset=Place.objects, label=_('Place:'))
	week_days = forms.MultipleChoiceField(label=_("Days of week: "),
						required=False, choices=WEEKDAYS,
						widget=forms.CheckboxSelectMultiple())

	def save(self, user, force_insert=False, force_update=False, commit=True):
		booking = Booking()
		booking.user = user
		booking.name = self.cleaned_data.get("name")
		booking.start_date = self.cleaned_data.get("start_date")
		booking.end_date = self.cleaned_data.get("end_date")
		booking.place = self.cleaned_data.get("place")
		weekdays = self.cleaned_data.get("week_days")

		book = BookTime()
		book.date_booking = booking.start_date
		book.start_hour = self.cleaned_data.get("start_hour")
		book.end_hour = self.cleaned_data.get("end_hour")
		try:
			booking.save()
			if booking.exists(book.start_hour, book.end_hour, weekdays):
				return None
			else:
				for day in date_range(book.date_booking, booking.end_date):
					if(day.isoweekday()-1 in map(int, weekdays)):
						newBookTime = BookTime(start_hour=book.start_hour,
										end_hour=book.end_hour,
										date_booking=day)
						newBookTime.save()
						booking.time.add(newBookTime)
				booking.save()
		except Exception as e:
			booking.delete()
			msg = _('Failed to book selected period')
			print(e)
			raise forms.ValidationError(msg)
			return None
		return booking
		# do custom stuff

	def clean_week_days(self):
		weekdays = self.cleaned_data['week_days']
		start_date = self.cleaned_data['start_date']
		end_date = self.cleaned_data['end_date']
		if((end_date-start_date).days > 7 and not weekdays):#7 days in a week
			msg = _('Select a repeating standard for the period you selected')
			self.add_error('week_days', msg)
		elif not weekdays:
			period = date_range(start_date, end_date)
			for day in period:
				weekdays.append(day.weekday())
		return weekdays

	def clean(self):
		cleaned_data = super(BookingForm, self).clean()
		today = date.today()
		now = datetime.now()

		try:
			start_date = cleaned_data.get('start_date')
			end_date = cleaned_data.get('end_date')
			start_hour = cleaned_data.get('start_hour')
			end_hour = cleaned_data.get('end_hour')
			if not (today <= start_date <= end_date):
				msg = _('Invalid booking period: Booking must be'
						' in future dates')
				self.add_error('start_date', msg)
				self.add_error('end_date', msg)
				raise forms.ValidationError(msg)
			elif ( (start_date == today <= end_date) and
					not(now.time() < start_hour < end_hour) ):
				msg = _('Invalid booking hours: Time must be after'
						' current hour')
				self.add_error('start_hour', msg)
				self.add_error('end_hour', msg)
				raise forms.ValidationError(msg)
		except Exception as e:
			msg = _('Inputs are in an invalid format')
			print(e)
			raise forms.ValidationError(msg)
