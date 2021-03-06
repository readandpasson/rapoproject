import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, ListView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import allauth
from allauth.account.views import logout
from django.contrib import admin
admin.autodiscover()

from allauth.socialaccount.models import SocialAccount
from rapocore.views import ReleaseBook,ReceiveBook,SendBook, GetMembers, WriteBookReview, WithdrawBook
from rapocore.views import Search, Browse, SearchResults, PassOn,PassOnBook, Test, MyAccount, FeedbackPage
from rapocore.views import NewAuthor,NewLanguage, NewGenre, ReportDefect, DefectListView, MemberListView, MemberProfile
from rapocore.models import Book


urlpatterns = patterns('',
    url(r'^admin/jsi18n/$', 'django.views.i18n.javascript_catalog'), 
    url(r'^admin/', include(admin.site.urls)),#why not quotes ?SM


    #url(r'^$', TemplateView.as_view(template_name="underconstruction.html"), name="index"),
    url(r'^$', 'allauth.account.views.login',name='login'),
    url(r'^home/', TemplateView.as_view(template_name="home.html"), name="index"),
    url(r'^about/', TemplateView.as_view(template_name="about.html"), name="index"),
    #url(r'^contact/', TemplateView.as_view(template_name="contact.html"), name="index"),
    url(r'^readme$', TemplateView.as_view(template_name="rapocore/readme.html"), name="index"),
    url(r'^disclaimer$', TemplateView.as_view(template_name="rapocore/disclaimer.html"), name="disclaimer"),
    url(r'^meet1$', TemplateView.as_view(template_name="rapocore/rapofirstmeet.html"), name="meet1"),
    url(r'^contest1$', TemplateView.as_view(template_name="rapocore/ReviewContestDec2013.html"), name="meet1"),

    url(r'^thanks/', TemplateView.as_view(template_name="rapocore/thanks.html"), name="thanks"),

    url(r'^accounts/profile/','rapocore.views.MyAccount' ,name='myaccount'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/memberprofile/(?P<username>.*)/', 'rapocore.views.MemberProfile',name='member-profile'),
    url(r'^logout/', 'allauth.account.views.logout',name='logout'),
    url(r'^feedback/', 'rapocore.views.FeedbackPage', name="feedback"),
    url(r'^meets/', 'rapocore.views.MeetsHome', name="meets"),
    url(r'^qea/', 'rapocore.views.QEAHome', name="qea"),
    url(r'^howitworks/', TemplateView.as_view(template_name="rapocore/howitworks.html"), name="howitworks"),
    #url(r'^feedbacklist/', 'rapocore.views.FeedbackList', name="feedback-list"),
    #url(r'^feedbackdetails/(?P<feedbackid>\d+)/$', 'rapocore.views.FeedbackDetails', name="feedback-details"),    

    url(r'^releasebook/', 'rapocore.views.ReleaseBook',name='release-book'),
    url(r'^withdrawbook(?P<bookid>[0-9]*)/', 'rapocore.views.WithdrawBook',name='withdraw-book'),
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

    #url(r'^memberbrowse/', MemberListView.as_view(),name='member-browse'),
    url(r'^writebookreview/(?P<bookid>\d+)/$', 'rapocore.views.WriteBookReview', name='write-bookreview'),
    url(r'^rapobookreviewslist/(?P<bookid>\d+)/$', 'rapocore.views.RAPOBookReviewsList', name='rapo-bookreview-list'),
    url(r'^rapobookreviewsdetails/(?P<bookid>\d+)/(?P<reviewid>\d+)/$', 'rapocore.views.RAPOBookReviewsDetails', name='rapo-bookreview-details'),
    
    url(r'^addauthor/', 'rapocore.views.NewAuthor',name='add-author'),
    url(r'^addgenre/', 'rapocore.views.NewGenre',name='add-genre'),
    url(r'^addlanguage/', 'rapocore.views.NewLanguage',name='add-language'),
    url(r'^add2queue(?P<bookid>[0-9]*)/$', 'rapocore.views.Add2Queue',name='add-queue'),
    url(r'^cancelrequest(?P<bookid>[0-9]*)/$', 'rapocore.views.CancelRequest',name='cancel-request'),
    url(r'^archiveit(?P<defectid>[0-9]*)/$', 'rapocore.views.Archiveit',name='archiveit'),
    url(r'^closeit(?P<defectid>[0-9]*)/$', 'rapocore.views.Closeit',name='closeit'),
    url(r'^passon(?P<bookid>[0-9]*)/$', 'rapocore.views.PassOnBook',name='passon-book'),

    url(r'^defect/', 'rapocore.views.ReportDefect',name='report-defect'),
    url(r'^defectbrowse/', DefectListView.as_view(),name='defect-browse'),
    url(r'^memberbrowse/', MemberListView.as_view(queryset=SocialAccount.objects.order_by("user__first_name","user__last_name")),name='member-browse'),
    url(r'^$', 'allauth.account.views.login',name='login'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += patterns('django.contrib.staticfiles.views',
	    url(r'^static/(?P<path>.*)$', 'serve'),
)
