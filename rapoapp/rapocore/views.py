# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponse
from django.views.generic import ListView
from django.views.generic import FormView
from rapocore.models import Author,Member,Book
from rapocore.forms import ReleaseBookForm, SendBookForm, ReceiveBookForm, SearchForm



# make a book release
def ReleaseBook(request):
    form = ReleaseBookForm()
    context = Context({'title': 'Release a book', 'form': form})
    return render_to_response('rapocore/releasebook_form.html',context)

def Search(request,byfield):
    form = SearchForm(request.GET or None)
    if request.method == 'POST':
		if form.is_valid:
			print 'form is valid'
    context = Context({'title': 'Search a book', 'form': form})
    return render_to_response('rapocore/search_form.html',context)

def SearchResults(request):
    query = request.GET.get('q', '')
    field = request.GET.get('field', '')
    if query:
        qset = (
            Q(title__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        )
        results = Book.objects.filter(qset).distinct()
    else:
        results = []
    return render_to_response("rapocore/search.html", { "results": results, "query": query , "field": field})

class AuthorListView(ListView):
    model = Author

class MemberListView(ListView):
    model = Member

class BookListView(ListView):
    model = Book


# receive a book
def ReceiveBook(request):

    form = ReceiveBookForm()
	#context = Context({'title': 'Add Item', 'form': form})
    return render_to_response('rapocore/receivebook_form.html',context)


# send a book
def SendBook(request):

    form = SendBookForm()
	#context = Context({'title': 'Add Item', 'form': form})
    return render_to_response('rapocore/sendbook_form.html',context)


