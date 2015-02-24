from django.conf.urls import patterns, include, url
from django.views.static import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'namerater.views.index'),
    url(r'^(?P<page>[0-9]+)$', 'namerater.views.index'),
    url(r'^comment/submit$', 'namerater.views.comment_submit'),
    url(r'^error/(?P<error>[0-9a-z_]+)$', 'namerater.views.error'),
    url(r'^login$', 'namerater.views.login'),
    url(r'^logout$', 'namerater.views.logout'),
    url(r'^name/submit$', 'namerater.views.name_submit'),
    url(r'^help$', 'namerater.views.help'),
    url(r'^name$', 'namerater.views.name'),
    url(r'^profile/(?P<key>[0-9a-z]+)/(.*)$', 'namerater.views.profile'),
    url(r'^search$', 'namerater.views.search'),
    url(r'^top/recent$', 'namerater.views.index', {"method":"top", "options":"recent"}),
    url(r'^top/recent/(?P<page>[0-9]+)$', 'namerater.views.index', {"method":"top", "options":"recent"}),
    url(r'^top/all$', 'namerater.views.index', {"method":"top", "options":"all"}),
    url(r'^top/all/(?P<page>[0-9]+)$', 'namerater.views.index', {"method":"top", "options":"all"}),
    url(r'^random$', 'namerater.views.index', {"method":"random"}),
    url(r'^report/submit$', 'namerater.views.report_submit'),
    url(r'^user$', 'namerater.views.index', {"method":"user"}),
    url(r'^user/(?P<page>[0-9]+)$', 'namerater.views.index', {"method":"user"}),
    url(r'^view/(?P<key>[0-9a-z]+)$', 'namerater.views.view'),
    
    url(r'^ajax/ban/(?P<key>[0-9a-z]+)$', 'namerater.views.ban'),
    url(r'^ajax/delete/(?P<key>[0-9a-z]+)$', 'namerater.views.delete'),
    url(r'^ajax/details$', 'namerater.views.details'),
    url(r'^ajax/vote/(?P<key>[0-9a-z]+)$', 'namerater.views.vote')
    
)

if settings.ENV == "DEV":
    urlpatterns += patterns('', (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}))

handler403 = "namerater.views.error"    
handler404 = "namerater.views.error"
handler500 = "namerater.views.error"