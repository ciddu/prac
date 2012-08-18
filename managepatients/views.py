import requests
import simplejson as json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext

from managepatients.forms import CampaignForm, LoginForm, KnowForm
from managepatients.models import Campaign, UserCampaign, User, Doctor


API_URL = "https://ray.practo.com/api/v1/%s"
SESSION_API_URL = API_URL % "sessions"
ROLE_API_URL = API_URL % "roles"
PATIENT_API_URL = API_URL % "patients"
DOCTOR_API_URL = API_URL % "practice/profile"



def connect_to_api(username, password):
	"""
	Connects to Practo API
	"""
	data = {'username':username, 'password':password}
	r = requests.post(SESSION_API_URL, data=data)

	return r

def index(request):
	return render_to_response('index.html',{},RequestContext(request))

def login_as_doctor(request):
	patients = []
	a = []
	form = LoginForm(request.POST or None)
	try:
		content  = request.session['content']
		headers = request.session['headers']
	except:
		request.session['loggedin'] = 0
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			r = connect_to_api(username, password)
			request.session['content'] = r.content
			request.session['headers'] = r.headers
			return HttpResponseRedirect('/login/doctor')
	else:		

		request.session['loggedin'] = 1
		print request.session['headers']
		xauth_token = headers['set-cookie'].split(';')[0]
		xauth_token = xauth_token.split('=')[1]
		headers = {'X-AUTH-TOKEN' : xauth_token}

		try:
			patients = request.session['patients']
		except:
			r = requests.get(PATIENT_API_URL, headers=headers)
			patients = json.loads(r.content)['patients']
			request.session['patients'] = patients

		for users in patients:
			try:
				primary_mobile = users['primary_mobile']
			except:
				primary_mobile = "Mobile not Given"
			try:
				primary_email = users['primary_email']
			except:
				primary_email = "Email not Given"
			save_user(users['id'], 
					  users['name'],
					  primary_email, 
					  primary_mobile, 
					  users['practice_id'], 
					  users['has_photo'])
		try:
			doctor = request.session['doctor']
			print doctor
		except:
			r = requests.get(DOCTOR_API_URL, headers=headers)
			doctor = json.loads(r.content)
			request.session['doctor'] = doctor
		save_doctor(doctor['id'], doctor['name'])
		campaigns = Campaign.objects.filter(doctor_id=doctor['id'])
		for items in campaigns:
			user_campaign = UserCampaign.objects.filter(campaign=items.id, seen_campaign=True)
			a.append((len(user_campaign), items.campaign_name))

	loggedin = request.session['loggedin']
	return render_to_response('login_as_doctor.html',{'content':patients,
													  'campaign':a,
													  'form':form,
													  'loggedin':loggedin},RequestContext(request))

def login_as_patient(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		try:
			user = User.objects.get(primary_email=username,
									password=password)
		except:
			print 'password not matching'
		else:
			request.session['user'] = user
			return HttpResponseRedirect('/know')

	return render_to_response('login_as_patient.html',{'form':form},RequestContext(request))

def start_campaign(request):
	try:
		not_patient = request.session['not_patient']
	except:
		request.session['not_patient'] = []
	no_patient = request.GET.get('no_patients', '')
	if no_patient == 'yes':
		get = 1
	else:
		get = 0
	not_patient = []
	form = CampaignForm(request.POST or None)
	if form.is_valid():

		print request.POST
		campaign_name = form.cleaned_data['campaign']
		doctor_id = Doctor.objects.get(id=request.session['doctor']['id'])
		campaign = save_campaign(campaign_name, doctor_id)

		patients = form.cleaned_data['patients']
		patients = list(set(patients.split(',\t')))
		for email in patients:
			email = email.strip()

			try:
				user = User.objects.get(primary_email=email)
			except:
				not_patient.append(email)
				print not_patient
			else:
				save_user_campaign(campaign, user)

		if  len(not_patient) == 0:
			return HttpResponseRedirect('/start/')
		else:
			request.session['not_patient'] = not_patient
			return HttpResponseRedirect('/start/?no_patients=yes')
	return render_to_response('start_campaign.html',{'form':form, 
													 'content':request.session['patients'],
													 'not_patient':request.session['not_patient'],
													 'get':get},
													 RequestContext(request))

def came_to_know_campaign(request):
	user = request.session['user']
	usercampaign = UserCampaign.objects.filter(userid=user.id)
	form = KnowForm(request.POST or None)
	if form.is_valid():
		know = form.cleaned_data['know']
		campaign = Campaign.objects.get(campaign_name=know)
		save_user_campaign(campaign, user)
	return render_to_response('came_to_know_campaign.html',{'usercampaign':usercampaign,
															'form':form},
													 RequestContext(request))



def save_campaign(campaign_name, doctor_id):
	try:
		campaign = Campaign.objects.get(campaign_name=campaign_name, doctor_id=doctor_id)	
	except:
		campaign  = Campaign(campaign_name=campaign_name, doctor_id=doctor_id)		
		campaign.save()

	return campaign


def save_user_campaign(campaign_id, user_id):
	try:
		user_campaign = UserCampaign.objects.get(userid=user_id.id, campaign=campaign_id.id)
	except:
		user_campaign = UserCampaign(userid=user_id, campaign=campaign_id)
		user_campaign.save()
	else:
		try:
			user_campaign = UserCampaign.objects.get(userid=user_id.id, campaign=campaign_id.id, seen_campaign=True)
		except:
			user_campaign = UserCampaign(id=user_campaign.id, userid=user_campaign.userid, campaign=user_campaign.campaign, seen_campaign=True)

			user_campaign.save()


def save_user(id, name, primary_email, primary_mobile, practice_id, has_photo):
	try:
		user = User.objects.get(primary_email=primary_email)
	except:
		user = User(id=id,
					name=name,
					primary_email=primary_email,
					primary_mobile=primary_mobile,
					practice_id=practice_id,
					has_photo=has_photo)
		user.save()

def save_doctor(id, name):
	try:
		doctor = Doctor.objects.get(id=id)
	except:
		doctor = Doctor(id=id,
						name=name)
		doctor.save()