from django.db import models


class User(models.Model):
	id = models.IntegerField(max_length=255, primary_key=True)
	name = models.CharField(max_length=255)
	primary_mobile = models.CharField(max_length=255)
	primary_email = models.EmailField('email')
	practice_id = models.CharField(max_length=255)
	has_photo = models.BooleanField()
	password = models.CharField(max_length=30, default='12345')

class Doctor(models.Model):
	id = models.IntegerField(max_length=255, primary_key=True)
	name = models.CharField(max_length=255)


class Campaign(models.Model):
	campaign_name = models.CharField(max_length=30)
	doctor_id = models.ForeignKey(Doctor)

	def __unicode__(self):
		return ("%s" % (self.campaign_name))



class UserCampaign(models.Model):
	userid = models.ForeignKey(User)
	campaign = models.ForeignKey(Campaign)
	seen_campaign = models.BooleanField()

