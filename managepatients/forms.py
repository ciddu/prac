from django import forms
from django.forms.widgets import Select, RadioSelect, CheckboxSelectMultiple

from managepatients.models import Campaign

class CampaignForm(forms.Form):

    campaign = forms.CharField(label="",
                            help_text='',
                            widget=forms.TextInput(
                                      attrs={'class':'required','placeholder':'Enter a campaign name'}))
    
    patients = forms.CharField(label="patients",widget=forms.Textarea(attrs={}))

class LoginForm(forms.Form):

	username = forms.CharField(label="",
                            help_text='',
                            widget=forms.TextInput(
                                      attrs={'class':'required','placeholder':'username'}))

	password = forms.CharField(label="",
                            help_text='',
                            widget=forms.TextInput(
                                      attrs={'class':'required','placeholder':'password'}))


class KnowForm(forms.Form):
  know = forms.CharField(label="campaign",widget=forms.Textarea(attrs={}))

