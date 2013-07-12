# Create your views here.
from datetime import datetime
from django.db.models import Q
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.views.generic import ListView
from django.views.generic import FormView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.utils.html import escape
from django.forms.models import modelform_factory

from django_tables2   import RequestConfig
from rapocore.tables  import BookTable
from rapocore.models import Author,SocialAccount,Book
from rapocore.models import Transaction
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
    else:
        form = ReleaseBookForm(request.user)

    return render_to_response('rapocore/releasebook_form.html',{ 'form': form},RequestContext(request))

# send a book
def SendBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = SendBookForm(request.user,request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f = form.save(commit=False)

            f.from_member = SocialAccount.objects.get(user_id = request.user)
            f.status = Transaction.TRANSIT
            f.save()
    else:
        form = SendBookForm(request.user)

    return render_to_response('rapocore/sendbook_form.html',{ 'form': form},RequestContext(request))


# receive a book
def ReceiveBook(request):

    if request.method == 'POST': # If the form has been submitted...
        instance = get_object_or_404(Transaction,to_member=SocialAccount.objects.get(user=request.user))
        form = ReceiveBookForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
        #    # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.book_id = request.POST.get('book','')
            f.date_received = datetime.now()
            f.status = Transaction.READ
            f.save()
            b = Book.objects.get(id=f.book_id)
            b.withmember = SocialAccount.objects.get(user=request.user)
            b.save()

    else:
        form = ReceiveBookForm(request.user)

    return render_to_response('rapocore/receivebook_form.html',{ 'form': form},RequestContext(request))

def PassOn(request):

    if request.method == 'POST': # If the form has been submitted...
        instance = get_object_or_404(Transaction,to_member=SocialAccount.objects.get(user=request.user))
        form = PassonForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
        #    # Process the data in form.cleaned_data
            f = form.save(commit=False)
            f.book_id = request.POST.get('book','')
            f.status = Transaction.AVAILABLE
            f.save()
    else:
        form = PassonForm(request.user)

    return render_to_response('rapocore/passon_form.html',{ 'form': form},RequestContext(request))

def Search(request):
    form = SearchForm(request.GET or None)
    if request.method == 'POST':
        if form.is_valid:
            print 'form is valid'
    return render_to_response('rapocore/search_form.html',{'form':form},RequestContext(request))

def SearchResults(request):
    stitle = request.POST['stitle']
    sauthor = request.POST['sauthor']
    slanguage = request.POST['slanguage']
    stag = request.POST['stag']
    sownermember = request.POST['sownermember']
    swithmember = request.POST['swithmember']
    #results = Book.objects.all()
    results = Book.objects.values('id','title','author__first_name','author__last_name','language__languagename','tag__taglabel','ownermember','withmember')
    if stitle:
        results = results.filter(title__icontains=stitle)
    if sauthor:
        results = results.filter(Q(author__first_name__icontains=sauthor)|Q(author__last_name__icontains=sauthor))
    if slanguage:
        results = results.filter(language__id__exact=slanguage)
    if stag:
        results = results.filter(tag__taglabel__icontains=stag)
    if sownermember:
        results = results.filter(ownermember__id__exact=sownermember)
    if swithmember:
        results = results.filter(withmember__id__exact=swithmember)
    #if sstatus:
    #    results = results.filter(status=sstatus)

    
    return render_to_response("rapocore/searchresults.html", { "results": results})

class AuthorListView(ListView):
    model = Author

class SocialAccountListView(ListView):
    model = SocialAccount

class BookListView(ListView):
    model = Book


def Browse(request):
    btable = BookTable(Book.objects.all())
    RequestConfig(request).configure(btable)
    return render(request,"rapocore/book_list.html",{"table":btable})

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
