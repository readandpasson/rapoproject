# Create your views here.
from django.utils.html import escape 
from datetime import datetime
from django.db.models import Q
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse

from django_tables2   import RequestConfig
from rapocore.models import Author,SocialAccount,Book,Transaction
from rapocore.forms import ReleaseBookForm, SendBookForm, ReceiveBookForm, SearchForm
from rapocore.forms import AuthorForm, TagForm, LanguageForm, PassonForm



# make a book release
def ReleaseBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReleaseBookForm(request.user,request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f_user = SocialAccount.objects.get(user_id=request.user)
            f_type = form.save(commit=False)
            f_type.ownermember = SocialAccount.objects.get(user_id = request.user)
            f_type.withmember = SocialAccount.objects.get(user_id = request.user)
            f_type.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = ReleaseBookForm(request.user)
        return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Release a book', 'submitmessage':'Release','formaction':'releasebook'},RequestContext(request))

# send a book
def SendBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SendBookForm(request.user,request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.from_member = SocialAccount.objects.get(user_id = request.user)
            f.save()

            b = form.cleaned_data['book']
            b.status = Book.TRANSIT
            b.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = SendBookForm(request.user)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Send a book', 'submitmessage':'Send','formaction':'sendbook'},RequestContext(request))


# receive a book
def ReceiveBook(request):

    if request.method == 'POST': # If the form has been submitted...
        instance = get_object_or_404(Transaction,to_member=SocialAccount.objects.get(user=request.user))
        form = ReceiveBookForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
        #    # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.book_id = form.cleaned_data['book']
            f.date_received = datetime.now()
            f.save()
            b = Book.objects.get(id=f.book_id)
            b.withmember = SocialAccount.objects.get(user=request.user)
            b.status = Book.READ
            b.save()
            return HttpResponseRedirect('/thanks/')

    else:
        form = ReceiveBookForm(request.user)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Receive a book', 'submitmessage':'Receive','formaction':'receivebook'},RequestContext(request))

def PassOn(request):

    if request.method == 'POST': # If the form has been submitted...
        instance = get_object_or_404(Transaction,to_member=SocialAccount.objects.get(user=request.user))
        form = PassonForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
        #    # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.book_id = form.cleaned_data['book']
            f.save()
            b = form.cleaned_data['book']
            b.status = Book.AVAILABLE
            b.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = PassonForm(request.user)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Pass a book on', 'submitmessage':'Pass On','formaction':'passon'},RequestContext(request))

def Search(request):
    form = SearchForm(request.GET or None)
    if request.method == 'POST':
        if form.is_valid:
            print 'form is valid'
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Search for a book', 'submitmessage':'Search','formaction':'searchresults'},RequestContext(request))

def SearchResults(request):
    stitle = form.cleaned_data['stitle']
    sauthor = form.cleaned_data['sauthor']
    slanguage = form.cleaned_data['slanguage']
    #stag = form.cleaned_data['stag']
    sownermember = form.cleaned_data['sownermember']
    swithmember = form.cleaned_data['swithmember']
    sstatus = form.cleaned_data['sstatus']
    results = Book.objects.all()
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
    
    return render_to_response('rapocore/book_list.html', { 'data': results})

def Thanks(request):
    return HttpResponseRedirect('rapocore/thanks.html')

def Browse(request):
    
    data = Book.objects.all().values('id','title','author__first_name','author__last_name','language__languagename','ownermember__user__first_name','ownermember__user__last_name','withmember__user__first_name','withmember__user__last_name','status')
    return render_to_response('rapocore/book_list.html',{  'data' : data }, RequestContext(request))

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
