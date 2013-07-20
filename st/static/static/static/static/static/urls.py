import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import allauth
from allauth.account.views import logout
from django.contrib import admin
admin.autodiscover()

from rapocore.views import ReleaseBook,ReceiveBook,SendBook, GetMembers
from rapocore.views import Search, Browse, SearchResults, PassOn,PassOnBook
from rapocore.views import NewAuthor,NewLanguage, NewTag, ReportDefect, DefectListView
#from rapocore.views import SendBookWizard
from rapocore.models import Book


urlpatterns = patterns('',
    url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'), 
    url(r'^admin/', include(admin.site.urls)),#why not quotes ?SM


    url(r'^$', TemplateView.as_view(template_name="underconstruction.html"), name="index"),
    url(r'^thanks/', TemplateView.as_view(template_name="rapocore/thanks.html"), name="thanks"),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/',  TemplateView.as_view(template_name="rapocore/myaccount.html") ,name='myaccount'),
    url(r'^logout/', 'allauth.account.views.logout',name='logout'),

    url(r'^releasebook/', 'rapocore.views.ReleaseBook',name='release-book'),
    #url(r'^sendbook/', SendBookWizard.as_view([SendBookForm1,SendBookForm2])),
    url(r'^sendbook/', 'rapocore.views.SendBook',name='send-book'),
    url(r'^getmembersinqueue/(?P<bookid>[0-9]*)/', 'rapocore.views.GetMembers',name='send-book-get-members'),
    url(r'^receivebook/', 'rapocore.views.ReceiveBook',name='receive-book'),
    url(r'^passon/', 'rapocore.views.PassOn',name='pass-on'),
    #url(r'^searchby(?P<byfield>.*)/$', 'rapocore.views.Search',name='search'),
    url(r'^search/', 'rapocore.views.Search',name='search'),
    url(r'^searchresults', 'rapocore.views.SearchResults',name='search-results'),
    url(r'^browse/', 'rapocore.views.Browse', name='book-view'),


    url(r'^addauthor/', 'rapocore.views.NewAuthor',name='add-author'),
    url(r'^addtag/', 'rapocore.views.NewTag',name='add-tag'),
    url(r'^addlanguage/', 'rapocore.views.NewLanguage',name='add-language'),
    url(r'^add2queue(?P<bookid>[0-9]*)/$', 'rapocore.views.Add2Queue',name='add-queue'),
    url(r'^passon(?P<bookid>[0-9]*)/$', 'rapocore.views.PassOnBook',name='passon-book'),

    url(r'^defect/', 'rapocore.views.ReportDefect',name='report-defect'),
    url(r'^listdefect/', DefectListView.as_view(),name='browse-defects')
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)


urlpatterns += staticfiles_urlpatterns()
#if settings.DEBUG:
urlpatterns += patterns('django.contrib.staticfiles.views',
    url(r'^static/(?P<path>.*)$', 'serve'),
)
