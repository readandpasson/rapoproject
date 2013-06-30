# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.views.generic import FormView
from rapocore.models import Author,Member,Book
from rapocore.models import Transaction
from rapocore.forms import ReleaseBookForm, SendBookForm, ReceiveBookForm, SearchForm



# make a book release
def ReleaseBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReleaseBookForm(request.user,request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f_user = Member.objects.get(username=request.user.id)
            f_type = form.save(commit=False)
            f_type.ownermember = Member.objects.get(username = request.user)
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
            f_user = Member.objects.get(username=request.user.id)
            f_type = form.save(commit=False)

            f_type.from_member = Member.objects.get(username = request.user)
            f_type.save()
    else:
        form = SendBookForm(request.user)

    return render_to_response('rapocore/sendbook_form.html',{ 'form': form},RequestContext(request))


# receive a book
def ReceiveBook(request):

    if request.method == 'POST': # If the form has been submitted...
        instance = get_object_or_404(Transaction, id=id)
        form = ReceiveBookForm(request.user,request.POST,instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            f_user = Member.objects.get(username=request.user.id)
            f_type = form.save(commit=False)

            f_type.from_member = Member.objects.get(username = request.user)
            f_type.save()
    else:
        form = ReceiveBookForm(request.user)

    return render_to_response('rapocore/receivebook_form.html',{ 'form': form},RequestContext(request))


def Search(request,byfield):
    form = SearchForm(request.GET or None)
    if request.method == 'POST':
                if form.is_valid:
                        print 'form is valid'
    #context = Context({'title': 'Search a book', 'form': form})
    return render_to_response('rapocore/search_form.html',{'form':form},RequestContext(request))

def SearchResults(request):
    query = request.POST.get('q', '')
    stitle = request.POST.get('stitle', '')
    if query:
        qset = (
            Q(title__icontains=stitle) 
            #Q(author__first_name__icontains=query) |
            #Q(author__last_name__icontains=query)
        )
        results = Book.objects.filter(qset).distinct()
    else:
        results = []
    return render_to_response("rapocore/search.html", { "results": results, "query": query })

class AuthorListView(ListView):
    model = Author

class MemberListView(ListView):
    model = Member

class BookListView(ListView):
    model = Book


