from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eds.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^upload/', include('pfs.urls', namespace='upload')),
    url(r'^$', 'pfs.views.index', name='index'),
    url(r'^(?P<pf_id>\w+)/portfolio/$', 'pfs.views.pf_detail', name='pf_detail'),
    url(r'^date/$', 'pfs.views.date_querry', name='date_querry'),
)
