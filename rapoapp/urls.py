import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import allauth
from allauth.account.views import logout
from django.contrib import admin
admin.autodiscover()

from rapocore.views import AuthorListView,BookListView,SocialAccountListView
from rapocore.views import ReleaseBook,ReceiveBook,SendBook
from rapocore.views import SearchResults,Search, Browse
from rapocore.views import NewAuthor,NewLanguage, NewTag

urlpatterns = patterns('',
    url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'), 
    url(r'^admin/', include(admin.site.urls)),#why not quotes ?SM


    url(r'^$', TemplateView.as_view(template_name="underconstruction.html"), name="index"),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/',  TemplateView.as_view(template_name="rapocore/myaccount.html") ,name='myaccount'),
    url(r'^logout/', 'allauth.account.views.logout',name='logout'),

    url(r'^releasebook/', 'rapocore.views.ReleaseBook',name='release-book'),
    url(r'^sendbook/', 'rapocore.views.SendBook',name='send-book'),
    url(r'^receivebook/', 'rapocore.views.ReceiveBook',name='receive-book'),
    url(r'^passon/', 'rapocore.views.PassOn',name='pass-on'),
    #url(r'^searchby(?P<byfield>.*)/$', 'rapocore.views.Search',name='search'),
    url(r'^search/', 'rapocore.views.Search',name='search'),
    url(r'^searchresults', 'rapocore.views.SearchResults',name='search-results'),

    url(r'^browse/', 'rapocore.views.Browse', name='book-view'),

    url(r'^addauthor/', 'rapocore.views.NewAuthor',name='add-author'),
    url(r'^addtag/', 'rapocore.views.NewTag',name='add-tag'),
    url(r'^addlanguage/', 'rapocore.views.NewLanguage',name='add-language'),



    url(r'^authors/$', AuthorListView.as_view(), name='author-view'),
    url(r'^members/$', SocialAccountListView.as_view(), name='member-view'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)


urlpatterns += staticfiles_urlpatterns()
