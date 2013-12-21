from django.utils.html import escape 
from datetime import datetime
from django.db.models import Q
from django.conf.urls import patterns, include, url
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.views.generic.list import ListView

from allauth.socialaccount.models import SocialAccount
from rapocore.models import RealBook,Transaction, Queue, Defect
from rapogen.models import Author,Book,Genre
from rapocore.forms import ReleaseBookForm, SendBookForm, SendBookToForm, ReceiveBookForm, SearchForm, ReportDefectForm
from rapocore.forms import AuthorForm, GenreForm, LanguageForm, PassonForm, Add2QueueForm, CancelRequestForm, WriteBookReviewForm

# make a book release
@login_required
def ReleaseBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReleaseBookForm(request.user,request.POST,request.FILES) # A form bound to the POST data
        if form.has_changed():
            if form.is_valid(): # All validation rules pass
                f_type = form.save(commit=False)
                f_type.ownermember = SocialAccount.objects.get(user_id = request.user)
                f_type.withmember = SocialAccount.objects.get(user_id = request.user)
#		f_type.doc = Document(docfile = request.FILES['docfile'])
#		f_type.doc.save()
                f_type.save()
                form.save_m2m()
                return HttpResponseRedirect('/thanks/')
	    else:
		messages.error(request, "Error")
    else:
        form = ReleaseBookForm(request.user)

    #documents = Document.objects.all()
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 
			'formtitle':'Release a book', 
			'formnote':'Do you want to release a book? Please Fill in the details in the form below and click on Release.', 
			'submitmessage':'Release',
			'formaction':'releasebook'},RequestContext(request))

# receive a book
@login_required
def ReceiveBook(request):

    if request.method == 'POST': # If the form has been submitted...
        b = request.POST['book']
        instance = Transaction.objects.get(to_member=SocialAccount.objects.get(user=request.user),book=b)
        form = ReceiveBookForm(request.user,request.POST,instance=instance) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.book_id = form.cleaned_data['book']
            f.date_received = datetime.now()
            f.save()
            b = form.cleaned_data['book']
            b.withmember = SocialAccount.objects.get(user=request.user)
            b.status = RealBook.READ
            b.save()
            return HttpResponseRedirect('/thanks/')

    else:
        form = ReceiveBookForm(request.user)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 
		'formtitle':'Receive a book', 
		'formnote':'Has a book sent to you by another member reached you? Please confirm here by choosing the book received by you.', 
		'submitmessage':'Receive',
		'formaction':'receivebook'},RequestContext(request))

@login_required
def PassOn(request): # Pass On is the act of moving a book from status 'Reading' to 'Available' 

    results = RealBook.objects.filter(withmember=SocialAccount.objects.get(user=request.user), status=RealBook.READ).select_related()
    member = SocialAccount.objects.get(user_id=request.user)
    return render_to_response('rapocore/book_list.html',{  'data' : results, 
			'formtitle':'Pass On',
			'formnote':'Finished reading a book? Let others know. Select which book you have completed/read and click on Pass On', 
			'member': member, 
			'search' : False ,
			'passon' : True}, RequestContext(request))

@login_required
def Search(request):
    form = SearchForm(request.GET or None)
    if form.has_changed():
        if form.is_valid():
            print "the form is valid"
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 
			'formtitle':'Search for a book', 
			'formnote':'Looking for something? Search our repository by providing search criteria', 
			'submitmessage':'Search',
			'formaction':'searchresults'},RequestContext(request))


@login_required
def SearchResults(request):

    stitle = request.POST['stitle']
    sauthor = request.POST['sauthor']
    slanguage = request.POST['slanguage']
    sgenre = request.POST['sgenre']
    sownermember = request.POST['sownermember']
    swithmember = request.POST['swithmember']
    sstatus = request.POST['sstatus']
    results = RealBook.objects.all().select_related()
    if stitle or sauthor or slanguage or sgenre or sownermember or swithmember or sstatus:
        if stitle:
            results = results.filter(book__title__icontains=stitle).select_related()
        if sauthor:
            results = results.filter(Q(book__author__first_name__icontains=sauthor)|Q(book__author__last_name__icontains=sauthor)).select_related()
        if slanguage:
            results = results.filter(book__language__id__exact=slanguage).select_related()
	if sgenre:
	    results = results.filter(book__genre__id__exact=sgenre).select_related()
        if sownermember:
            results = results.filter(ownermember__id__exact=sownermember).select_related()
        if swithmember:
            results = results.filter(withmember__id__exact=swithmember).select_related()
        if sstatus:
            results = results.filter(status=sstatus).select_related()

        #results = results.values('id','title','author__first_name','author__last_name','language__languagename','ownermember__user__first_name','ownermember__user__last_name','withmember__user__first_name','withmember__user__last_name','status')
        
        member = SocialAccount.objects.get(user_id=request.user)
	form = SearchForm(request.GET or None)
        return render_to_response('rapocore/book_list.html',{  'data' : results, 'member': member, 'search': True, 'form':form }, RequestContext(request))
    else:
        member = SocialAccount.objects.get(user_id=request.user)
        return render_to_response('rapocore/book_list.html',{  'data' : [], 'member': member, 'search': True, 'form':form }, RequestContext(request))



@login_required
def Browse(request):
    results = RealBook.objects.all().order_by('-id').select_related()
    member = SocialAccount.objects.get(user_id=request.user)
    bookqueue = Queue.objects.all().order_by('id').select_related()
    transaction = Transaction.objects.filter(date_received__isnull = True).order_by('-id').select_related()

    return render_to_response('rapocore/book_list.html',{  'data' : results, 
			'formtitle': 'Browse books',
			'member': member, 'bookqueue': bookqueue, 'transaction': transaction, 'search' : False }, RequestContext(request))

# Benitha: added code for Book details page: 06-Nov-2013

@login_required
def BookDetails(request,bookid):
    results = RealBook.objects.select_related().get(id= bookid)
    book = RealBook.objects.get(id=bookid)
    member = SocialAccount.objects.get(user_id=request.user)
    queueDetails = ViewQueue(request, bookid)
    booksTran = Transaction.objects.filter(book_id=bookid)
    dateTran = Transaction.objects.filter(book_id=bookid).filter(date_received__isnull = True )
    data = {  'book' : results, 'member': member, 'tran' : booksTran, 'dateNull' : dateTran, 'bookid':bookid }
    data.update(queueDetails)
    return render_to_response('rapocore/book_details.html', data, RequestContext(request))

@login_required
def NewAuthor(request):
    return handlePopAdd(request, AuthorForm, 'author')

@login_required
def NewLanguage(request):
    return handlePopAdd(request, LanguageForm, 'language')

@login_required
def NewGenre(request):
    return handlePopAdd(request, GenreForm, 'genre')

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
        b = RealBook.objects.get(id= bookid)
        b.status = RealBook.AVAILABLE
        b.save()
        return render_to_response('rapocore/passon.html',{ 'book': b.book.title},RequestContext(request))

@login_required
def ViewQueue(request, bookid):
        b = RealBook.objects.get(id= bookid)
        if b.status  == RealBook.TRANSIT:
            temp_tr = Transaction.objects.get(book=b,date_received__isnull = True )
            to_member = SocialAccount.objects.get(id=temp_tr.to_member.id)
        else:
            to_member = ()
        if Queue.objects.filter(book=b).exists() :
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        else :
            qset = ()
	return {'queue':qset,'to_member':to_member}
#        return render_to_response('rapocore/viewqueue.html',{ 'book': b.title,'queue':qset,'to_member':to_member}, RequestContext(request))

@login_required
def Add2Queue(request, bookid):
        b = RealBook.objects.get(id= bookid)
        m = SocialAccount.objects.get(user_id=request.user)
        if Queue.objects.filter(book=b,member=m).exists() :
            success = False
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        else:
            q=Queue(book=b,member=m)
            q.save()
            success = True
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        return render_to_response('rapocore/add2queue.html',{ 'book': b.book.title,'queue':qset, 'success': success}, RequestContext(request))


# send a book
@login_required
def SendBook(request):
    if request.method == "POST":
        form = SendBookForm(request.user, request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.from_member = SocialAccount.objects.get(user_id = request.user)
            f.save()

            b = form.cleaned_data['book']
            b.status = RealBook.TRANSIT
            b.save()
            
            m = form.cleaned_data['to_member']
            Queue.objects.get(book=b,member=m).delete()
            return HttpResponseRedirect('/thanks/')
    else:
        form = SendBookForm(request.user)

    return render_to_response('rapocore/sendbook_form.html',{ 'form': form, 
		'formtitle':'Send a book', 
		'formnote':'Have you physically sent a book to another member in the queue? Fill in the details below.', 
		'submitmessage':'Send',
		'formaction':'sendbook'},RequestContext(request))

# send a book to a particular member
@login_required
def SendBookTo(request,bookid,memberid):
    if request.method == "POST":
        form = SendBookToForm(request.user, bookid, memberid, request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            f = form.save(commit=False)
            f.from_member = SocialAccount.objects.get(user_id = request.user)
            f.to_member = SocialAccount.objects.get(uid = memberid)
            f.book = RealBook.objects.get(id=bookid)
            f.save()

            b = f.book
            b.status = RealBook.TRANSIT
            b.save()
            
            m = f.to_member
            Queue.objects.get(book=b,member=m).delete()
            return HttpResponseRedirect('/thanks/')
    else:
        form = SendBookToForm(request.user,bookid,memberid)
        b = RealBook.objects.get(id=bookid)
        m = SocialAccount.objects.get(uid = memberid)

    return render_to_response('rapocore/generic_form.html',{ 'form': form, 'formtitle':'Send the book \''+ b.title + '\' to '+m.user.first_name+' '+m.user.last_name, 'submitmessage':'Send','formaction':'sendbookto'+memberid+'/'+ bookid},RequestContext(request))



@login_required
def GetMembers(request,bookid):
    if request.is_ajax():
        b = RealBook.objects.get(id=bookid)
        members = Queue.objects.filter(book_id=b).order_by('id').values('member','member__user__first_name','member__user__last_name','member__user__username')
        return render_to_response('rapocore/getmembers.html', { 'members': members },RequestContext(request))

@login_required
def ReportDefect(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReportDefectForm(request.user,request.POST) # A form bound to the POST data
        if form.has_changed():
            if form.is_valid(): # All validation rules pass
                f = form.save(commit=False)
                f.bymember = SocialAccount.objects.get(user_id = request.user)
                f.save()
                return HttpResponseRedirect('/thanks/')
    else:
        form = ReportDefectForm(request.user)
    return render_to_response('rapocore/generic_form.html',{ 'form': form, 
		'formtitle':'Report a defect', 
		'formnote':'Have you noticed any error in the database? Or a bug in the application? Do you need a new feature? Please let us know', 
		'submitmessage':'Report',
		'formaction':'defect'},RequestContext(request))

class DefectListView(ListView):
    model  = Defect
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DefectListView, self).get_context_data(**kwargs)
        context['archived'] = Defect.objects.filter(status=Defect.ARCHIVED)
        return context

@login_required
def Closeit(request, defectid):
        d = Defect.objects.get(id= defectid)
        d.status = Defect.CLOSED
        d.save()
        return render_to_response('rapocore/closeit.html',{ 'defect': d.description}, RequestContext(request))

@login_required
def Archiveit(request, defectid):
        d = Defect.objects.get(id= defectid)
        d.status = Defect.ARCHIVED
        d.save()
        return render_to_response('rapocore/archiveit.html',{ 'defect': d.description}, RequestContext(request))

@login_required
def CancelRequest(request,bookid):
        b = RealBook.objects.get(id= bookid)
        instance = Queue.objects.get(member=SocialAccount.objects.get(user_id=request.user),book=b)
        instance.delete()
        success = True # Success will be false when sender has already sent to this person  - To be implemented TBD
        return render_to_response('rapocore/cancelrequest.html',{ 'book': b.book.title, 'success': success}, RequestContext(request))

class MemberListView(ListView):
    model  = SocialAccount
    template_name = "rapocore/socialaccount_list.html"



@login_required
def Test(request):
    member = SocialAccount.objects.get(user_id=request.user)
    booksreleased = RealBook.objects.filter(ownermember = member).order_by('datereleased')
    #booksrequested_available = Queue.objects.filter(member= member) 
    booksrequested = Queue.objects.filter(member= member).select_related()
    bookssentome = Transation.objects.filter(tomember=member).select_related()
    bookswith = RealBook.objects.filter(withmember=member).select_related()
    #booksread = RealBook.objects.filter(withmember=member).select_related()
    return render_to_response('rapocore/try.html',{ 'booksreleased': booksreleased, 'booksrequested': booksrequested,'bookssenttome':bookssentome,'bookswith': bookswith}, RequestContext(request))

@login_required
def MyAccount(request):
    me = SocialAccount.objects.get(user_id=request.user)
    booksreleased = RealBook.objects.filter(ownermember = me).order_by('datereleased')
    #booksrequested_available = Queue.objects.filter(member= member) 
    booksrequested = Queue.objects.filter(member= me).select_related()
    bookswith = RealBook.objects.filter(withmember=me).select_related().exclude(status=RealBook.TRANSIT)
    bookswithqlist = []
    for bk in bookswith:
    	bookswithqlist.extend(list(Queue.objects.filter(book=bk).order_by('id').values('book__id','member__user__first_name','member__user__last_name')))

    booksintransitfromme = Transaction.objects.filter(Q(book__withmember=me)&Q(from_member=me)&Q(book__status=RealBook.TRANSIT)).select_related()
    booksintransittome = Transaction.objects.filter(Q(date_received__isnull=True)&Q(to_member=me)&Q(book__status=RealBook.TRANSIT)).select_related()
    return render_to_response('rapocore/dashboard.html',{ 'booksreleased': booksreleased, 'booksrequested': booksrequested,'bookswith': bookswith, 'bookswithqlist' : bookswithqlist,'booksintransitfromme': booksintransitfromme,'booksintransittome': booksintransittome}, RequestContext(request))

@login_required
def WriteBookReview(request,bookid):
	rbook = RealBook.objects.select_related().get(id= bookid)
	book = Book.objects.select_related().get(id= rbook.book_id)
	if request.method == 'POST': # If the form has been submitted...
		form = WriteBookReviewForm(request.user,request.POST) # A form bound to the POST data
		if form.has_changed():
			if form.is_valid():
				f_type = form.save(commit=False)
				f_type.reviewer = SocialAccount.objects.get(user_id = request.user)
				f_type.book_id = book.id
				f_type.save()
				#book.publisher = form.cleaned_data['spublisher']
				#book.save()
				#form.save_m2m()
				#print "the form is valid"
				return HttpResponseRedirect('/thanks/')
			else:
				 messages.error(request, "Error")
	else:
		form = WriteBookReviewForm(request.user)
	return render_to_response('rapocore/write_bookreviewform.html',{ 'form': form, 
				'formtitle':'Write book review', 
				'formnote':'Share your views of the book with others...', 
				'book':book,
				'submitmessage':'Submit Review', 'formaction':'writebookreview/'+bookid},RequestContext(request))
