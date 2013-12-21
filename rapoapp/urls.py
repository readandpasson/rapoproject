import settings
import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


import allauth
from allauth.account.views import logout
from django.contrib import admin
admin.autodiscover()

from rapocore.views import ReleaseBook,ReceiveBook,SendBook, GetMembers
from rapocore.views import Search, Browse, SearchResults, PassOn,PassOnBook, Test, MyAccount
from rapocore.views import NewAuthor,NewLanguage, NewTag, ReportDefect, DefectListView, MemberListView
#from rapocore.views import SendBookWizard
from rapocore.models import Book


urlpatterns = patterns('',
    url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'), 
    url(r'^admin/', include(admin.site.urls)),#why not quotes ?SM
#    url(r'^some/', include('djang0byte.urls')),


    #url(r'^$', TemplateView.as_view(template_name="underconstruction.html"), name="index"),
    url(r'^$', 'allauth.account.views.login',name='login'),
    url(r'^home/', TemplateView.as_view(template_name="home.html"), name="index"),
    url(r'^about/', TemplateView.as_view(template_name="about.html"), name="index"),
    url(r'^contact/', TemplateView.as_view(template_name="contact.html"), name="index"),
    url(r'^readme$', TemplateView.as_view(template_name="rapocore/readme.html"), name="index"),
    url(r'^disclaimer$', TemplateView.as_view(template_name="rapocore/disclaimer.html"), name="disclaimer"),

    url(r'^thanks/', TemplateView.as_view(template_name="rapocore/thanks.html"), name="thanks"),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/','rapocore.views.MyAccount' ,name='myaccount'),
    url(r'^logout/', 'allauth.account.views.logout',name='logout'),

    url(r'^releasebook/', 'rapocore.views.ReleaseBook',name='release-book'),
    url(r'^sendbook/', 'rapocore.views.SendBook',name='send-book'),
    url(r'^getmembersinqueue/(?P<bookid>[0-9]*)/', 'rapocore.views.GetMembers',name='send-book-get-members'),
    url(r'^receivebook/', 'rapocore.views.ReceiveBook',name='receive-book'),
    url(r'^passon/', 'rapocore.views.PassOn',name='pass-on'),
    #url(r'^searchby(?P<byfield>.*)/$', 'rapocore.views.Search',name='search'),
    url(r'^search/', 'rapocore.views.Search',name='search'),
    url(r'^searchresults', 'rapocore.views.SearchResults',name='search-results'),
    url(r'^bookbrowse/', 'rapocore.views.Browse', name='book-browse'),
# Benitha to work on Browse details page and view queue page : Date: 06-Nov-2013 	
    url(r'^bookdetails/(?P<bookid>\d+)/$', 'rapocore.views.BookDetails', name='book-details'),
    url(r'^viewqueue/(?P<bookid>\d+)/$', 'rapocore.views.ViewQueue', name='view-queue'),
    url(r'^writebookreview/(?P<bookid>\d+)/$', 'rapocore.views.WriteBookReview', name='write-bookreview'),
    
    url(r'^memberbrowse/', MemberListView.as_view(),name='member-browse'),
    url(r'^test/', 'rapocore.views.Test', name='book-view'),


    url(r'^addauthor/', 'rapocore.views.NewAuthor',name='add-author'),
    url(r'^addtag/', 'rapocore.views.NewTag',name='add-tag'),
    url(r'^addlanguage/', 'rapocore.views.NewLanguage',name='add-language'),
    url(r'^add2queue(?P<bookid>[0-9]*)/$', 'rapocore.views.Add2Queue',name='add-queue'),
    url(r'^cancelrequest(?P<bookid>[0-9]*)/$', 'rapocore.views.CancelRequest',name='cancel-request'),
    url(r'^archiveit(?P<defectid>[0-9]*)/$', 'rapocore.views.Archiveit',name='archiveit'),
    url(r'^closeit(?P<defectid>[0-9]*)/$', 'rapocore.views.Closeit',name='closeit'),
    url(r'^passon(?P<bookid>[0-9]*)/$', 'rapocore.views.PassOnBook',name='passon-book'),

    url(r'^defect/', 'rapocore.views.ReportDefect',name='report-defect'),
    url(r'^defectbrowse/', DefectListView.as_view(),name='defect-browse'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
	    url(r'^static/(?P<path>.*)$', 'serve'),
)
