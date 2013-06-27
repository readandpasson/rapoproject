from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import allauth
import settings
from django.contrib import admin
admin.autodiscover()

from rapocore.views import AuthorListView
from rapocore.views import BookListView
from rapocore.views import MemberListView
from rapocore.views import ReleaseBook
from rapocore.views import ReceiveBook
from rapocore.views import SendBook
from rapocore.views import SearchResults
from rapocore.views import Search
from rapocore.models import Book

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="underconstruction.html"), name="index"),

#    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'STATIC_URL': settings.STATIC_URL}),
    url(r'^accounts/', include('allauth.urls')),
    #url(r'^login/', 'rapocore.views.Login',name='login'),
    url(r'^accounts/profile/',  TemplateView.as_view(template_name="myaccount.html") ,name='myaccount'),
    #url(r'^signup/', 'rapocore.views.SignUp',name='signup'),
    url(r'^releasebook/', 'rapocore.views.ReleaseBook',name='release-book'),
    url(r'^sendbook/', 'rapocore.views.SendBook',name='send-book'),
    url(r'^receivebook/', 'rapocore.views.ReceiveBook',name='receive-book'),
    url(r'^searchby(?P<byfield>.*)/$', 'rapocore.views.Search',name='search'),
    url(r'^searchresults/$', 'rapocore.views.SearchResults',name='search-results'),



    url(r'^authors/$', AuthorListView.as_view(), name='author-view'),
    url(r'^members/$', MemberListView.as_view(), name='member-view'),
    url(r'^books/$', BookListView.as_view(), name='book-view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),#why not quotes ?SM

#    url(r'^facebook/', include('rapoapp.fb.urls')),
# (r'^', include('rapoapp.web.urls')),
)


urlpatterns += staticfiles_urlpatterns()
