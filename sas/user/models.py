from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.db import models

CATEGORY = (('', '----'), ('1', _('Student')), ('2', _('Teaching Staff')), ('3', _('Employees')))

class UserProfile(models.Model):
	registration_number = models.CharField(max_length=20)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_user")
	category = models.CharField(choices=CATEGORY, max_length=20)

	def name(self, name):
		if not hasattr(self, 'user'):
			self.user = User()
		names = name.split()
		self.user.first_name = names.pop(0)
		self.user.last_name = str.join(" ", names)

	def full_name(self):
		name = str.join(" ", [self.user.first_name, self.user.last_name])
		return name

	def save(self, *args, **kwargs):
		self.user.save()
		self.user_id = self.user.pk
		super(UserProfile, self).save(*args, **kwargs)