# Create your views here.
from django.utils.html import escape 
from datetime import datetime
from django.db.models import Q
from django.conf.urls import patterns, include, url
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.views.generic.list import ListView
#from django.contrib.formtools.wizard.views import SessionWizardView

from django_tables2   import RequestConfig
from rapocore.models import Author,SocialAccount,Book,Transaction, Queue, Defect
from rapocore.forms import ReleaseBookForm, SendBookForm, ReceiveBookForm, SearchForm, ReportDefectForm
from rapocore.forms import AuthorForm, TagForm, LanguageForm, PassonForm, Add2QueueForm

#class SendBookWizard(SessionWizardView):
#    def done(self, form_list, **kwargs):
#        return HttpResponseRedirect('/thanks/')
#

# make a book release
@login_required
def ReleaseBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReleaseBookForm(request.user,request.POST) # A form bound to the POST data
        if form.has_changed():
            if form.is_valid(): # All validation rules pass
                # Process the data in form.cleaned_data
                f_type = form.save(commit=False)
                f_type.ownermember = SocialAccount.objects.get(user_id = request.user)
                f_type.withmember = SocialAccount.objects.get(user_id = request.user)
                f_type.save()
                return HttpResponseRedirect('/thanks/')
    else:
        form = ReleaseBookForm(request.user)
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Release a book', 'submitmessage':'Release','formaction':'releasebook'},RequestContext(request))

# send a book
# receive a book
@login_required
def ReceiveBook(request):

    if request.method == 'POST': # If the form has been submitted...
        b = request.POST['book']
        instance = Transaction.objects.get(to_member=SocialAccount.objects.get(user=request.user),book=b)
        form = ReceiveBookForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
        #    # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.book_id = form.cleaned_data['book']
            f.date_received = datetime.now()
            f.save()
            b = form.cleaned_data['book']
            b.withmember = SocialAccount.objects.get(user=request.user)
            b.status = Book.READ
            b.save()
            return HttpResponseRedirect('/thanks/')

    else:
        form = ReceiveBookForm(request.user)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Receive a book', 'submitmessage':'Receive','formaction':'receivebook'},RequestContext(request))

@login_required
def PassOn(request):
    results = Book.objects.filter(withmember=SocialAccount.objects.get(user=request.user), status=Book.READ).values('id','title','author__first_name','author__last_name','language__languagename','ownermember__user__first_name','ownermember__user__last_name','withmember__user__username','withmember__user__first_name','withmember__user__last_name','status')
    return render_to_response('rapocore/book_list.html',{  'data' : results }, RequestContext(request))

@login_required
def Search(request):
    form = SearchForm(request.GET or None)
    if form.has_changed():
        if form.is_valid():
            print "the form is valid"
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Search for a book', 'submitmessage':'Search','formaction':'searchresults'},RequestContext(request))


@login_required
def SearchResults(request):

    stitle = request.POST['stitle']
    sauthor = request.POST['sauthor']
    slanguage = request.POST['slanguage']
    #stag = request.POST['stag']
    sownermember = request.POST['sownermember']
    swithmember = request.POST['swithmember']
    sstatus = request.POST['sstatus']
    results = Book.objects.all()
    if stitle or sauthor or slanguage or sownermember or swithmember or sstatus:
        if stitle:
            results = results.filter(title__icontains=stitle)
        if sauthor:
            results = results.filter(Q(author__first_name__icontains=sauthor)|Q(author__last_name__icontains=sauthor))
        if slanguage:
            results = results.filter(language__id__exact=slanguage)
        if sownermember:
            results = results.filter(ownermember__id__exact=sownermember)
        if swithmember:
            results = results.filter(withmember__id__exact=swithmember)
        if sstatus:
            results = results.filter(status=sstatus)

        results = results.values('id','title','author__first_name','author__last_name','language__languagename','ownermember__user__first_name','ownermember__user__last_name','withmember__user__first_name','withmember__user__last_name','status')
        
        return render_to_response('rapocore/book_list.html',{  'data' : results }, RequestContext(request))
    else:
        return render_to_response('rapocore/book_list.html',{  'data' : [] }, RequestContext(request))



@login_required
def Browse(request):
    
    results = Book.objects.all().values('id','title','author__first_name','author__last_name','language__languagename','ownermember__user__first_name','ownermember__user__last_name','withmember__user__username','withmember__user__first_name','withmember__user__last_name','status')
    return render_to_response('rapocore/book_list.html',{  'data' : results }, RequestContext(request))

@login_required
def NewAuthor(request):
    return handlePopAdd(request, AuthorForm, 'author')

@login_required
def NewLanguage(request):
    return handlePopAdd(request, LanguageForm, 'language')

@login_required
def NewTag(request):
    return handlePopAdd(request, TagForm, 'tag')

def handlePopAdd(request, addForm, field):

    if request.method == "POST":
        form = addForm(request.POST)
        if form.is_valid():
            try:
                newObject = form.save()
            except forms.ValidationError, error:
                newObject = None
            if newObject:
                return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                    (escape(newObject._get_pk_val()), escape(newObject)))
    else:
        form = addForm()

    return render_to_response('rapocore/addanother.html',{ 'form': form , 'field' : field }, RequestContext(request))

@login_required
def PassOnBook(request, bookid):
        b = Book.objects.get(id= bookid)
        b.status = Book.AVAILABLE
        b.save()
        return render_to_response('rapocore/passon.html',{ 'book': b.title},RequestContext(request))

@login_required
def Add2Queue(request, bookid):
        b = Book.objects.get(id= bookid)
        m = SocialAccount.objects.get(user_id=request.user)
        if Queue.objects.filter(book=b,member=m).exists() :
            success = False
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        else:
            q=Queue(book=b,member=m)
            q.save()
            success = True
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        return render_to_response('rapocore/add2queue.html',{ 'book': b.title,'queue':qset, 'success': success}, RequestContext(request))

@login_required
def SendBook(request):
    if request.method == "POST":
        form = SendBookForm(request.user, request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.from_member = SocialAccount.objects.get(user_id = request.user)
            f.save()

            b = form.cleaned_data['book']
            b.status = Book.TRANSIT
            b.save()
            
            m = form.cleaned_data['to_member']
            Queue.objects.get(book=b,member=m).delete()
            return HttpResponseRedirect('/thanks/')
    else:
        form = SendBookForm(request.user)

    return render_to_response('rapocore/sendbook_form.html',{ 'form': form, 'formtitle':'Send a book', 'submitmessage':'Send','formaction':'sendbook'},RequestContext(request))


def GetMembers(request,bookid):
    # Expect an auto 'type' to be passed in via Ajax and POST
    if request.is_ajax():
    #   from django.core import serializers
        b = Book.objects.get(id=bookid)
    #   json_members = serializers.serialize("json", Queue.objects.filter(book_id=b).order_by('id').values('member'))
    #   return HttpResponse(json_members, mimetype="application/javascript")
        members = Queue.objects.filter(book_id=b).order_by('id').values('member','member__user__first_name','member__user__last_name')

        return render_to_response('rapocore/getmembers.html', { 'members': members },RequestContext(request))

@login_required
def ReportDefect(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReportDefectForm(request.user,request.POST) # A form bound to the POST data
        if form.has_changed():
            if form.is_valid(): # All validation rules pass
                # Process the data in form.cleaned_data
                f = form.save(commit=False)
                f.bymember = SocialAccount.objects.get(user_id = request.user)
                f.save()
                return HttpResponseRedirect('/thanks/')
    else:
        form = ReportDefectForm(request.user)
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Report a defect', 'submitmessage':'Report','formaction':'defect'},RequestContext(request))

# send a book
# receive a book

class DefectListView(ListView):
    model  = Defect
