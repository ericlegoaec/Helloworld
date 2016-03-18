from django.conf.urls import patterns, url
from pfs import views

urlpatterns = patterns('',
    # url(r'^$', views.index, name="home"),  
    url(r'^pf_update$', views.pf_update, name="pf_update"), 
    url(r'^trade_update$', views.trade_update, name="trade_update"), 
)