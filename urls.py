from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from managepatients.views import index, start_campaign, login_as_doctor, login_as_patient, came_to_know_campaign
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', index, name="home"),
    url(r'^start/', start_campaign, name="start_campaign"),
    url(r'^login/doctor', login_as_doctor, name="login_as_doctor"),
    url(r'^login/patient', login_as_patient, name="login_as_patient"),
    url(r'^know/', came_to_know_campaign, name="came_to_know_campaign"),

)
