from django.conf.urls import url
import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^createuser$', views.createUser),
    url(r'^login$', views.userLogin),
    url(r'^logout$', views.userLogout),
    url(r'^ticket$', views.ticket),
    url(r'^searchticket/(?P<ticket_id>.*)$', views.searchTicket),
    
    url(r'^adminticket$', views.adminTicket),
]