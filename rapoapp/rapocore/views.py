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

from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount, SocialToken
from rapocore.models import RealBook,Transaction, Queue, Defect
from rapogen.models import Author,Book,Genre, BookReview, Feedback
from rapocore.forms import ReleaseBookForm, SendBookForm, SendBookToForm, ReceiveBookForm, SearchForm, ReportDefectForm, FeedbackForm
from rapocore.forms import AuthorForm, GenreForm, LanguageForm, PassonForm, Add2QueueForm, CancelRequestForm, WriteBookReviewForm
from rapocore.forms import FeedbackDetailsForm

from django.db.models import Avg, Max, Min
from rapocore.facebook import GraphAPI
from settings import FACEBOOKGROUP_ID

# make a book release
@login_required
def ReleaseBook(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ReleaseBookForm(request.user,request.POST,request.FILES) # A form bound to the POST data
        if form.has_changed():
            if form.is_valid(): # All validation rules pass
                f_type = form.save(commit=False)
                member = SocialAccount.objects.get(user_id = request.user)
                f_type.save()
                form.save_m2m()
                rb = RealBook(book = f_type,ownermember = member, withmember = member,status = RealBook.AVAILABLE)
                rb.save()

                #Message for facebook post
                msg = "Automated message: \nHi all, I released \'"+rb.book.title+"\' Do check it out at http://test.rapo.in/bookdetails/"+str(rb.id)
                try:
                    graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                    #attachment = {}
                    #message = 'test message'
                    #caption = 'test caption'
                    #attachment['caption'] = caption
                    #attachment['name'] = 'test name'
                    #attachment['link'] = 'link_to_picture'
                    #attachment['description'] = 'test description'
                    rb.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                    rb.save(update_fields=['comments'])
                except:
                    logging.debug('Facebook post failed')

                return HttpResponseRedirect('/thanks/')
            else:
                messages.error(request, "Error")
    else:
        form = ReleaseBookForm(request.user)

    #documents = Document.objects.all()
    return render_to_response('rapocore/release.html',{ 'form': form, 
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
            #Message for facebook comment
            if b.comments and FACEBOOKGROUP_ID in b.comments:
                msg = "Automated message: \nGot it"
                try:
                    graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                    graph.put_comment(b.comments,msg)
                except:
                    logging.debug('Facebook post failed')
            else:
                msg = "Automated message: \nGot the book titled \'"+b.book.title+"\' with id "+str(b.id)
                try:
                    graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                    b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                    b.save(update_fields=['comments'])
                except:
                    logging.debug('Facebook post failed')

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
        form = SearchForm(request.GET or None)
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
    #results = RealBook.objects.select_related().get(id= bookid)
    rbook = RealBook.objects.get(id=bookid)
    book = Book.objects.select_related().get(id= rbook.book_id)
    member = SocialAccount.objects.get(user_id=request.user)
    queueDetails = ViewQueue(request, bookid)
    bookReviewDetails = BookReviewDetails(request, book.id)
    booksTran = Transaction.objects.filter(book_id=bookid)
    dateTran = Transaction.objects.filter(book_id=bookid).filter(date_received__isnull = True )
    rapoReview = BookReview.objects.select_related().filter(status = 'A', book_id = book.id).values('rating','review','reviewer_id__user__first_name','reviewer_id__user__last_name')
    data = {  'book' : rbook, 'rapobook': book, 'member': member, 'tran' : booksTran, 'dateNull' : dateTran, 'bookid':bookid , 'bookReviews': bookReviewDetails, 'rapoReview':rapoReview}
    data.update(queueDetails)
    data.update(bookReviewDetails)
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
        #Message for facebook comment
        msg = "Automated message: \nPassing on book id "+str(b.id)+" titled "+b.book.title
        if b.comments and FACEBOOKGROUP_ID in b.comments:
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                b.save(update_fields=['comments'])
            except:
                logging.debug('Facebook post failed')
        return render_to_response('rapocore/passon.html',{ 'book': b.book.title},RequestContext(request))

@login_required
def ViewQueue(request, bookid):
        b = RealBook.objects.get(id= bookid)
        if b.status  == RealBook.TRANSIT:
            try:
                temp_tr = Transaction.objects.get(book=b,date_received__isnull = True )
            except Transaction.DoesNotExist:
                temp_tr = None
            if temp_tr:
                to_member = SocialAccount.objects.get(id=temp_tr.to_member.id)
                from_member = SocialAccount.objects.get(id=temp_tr.from_member.id)
            else:
                to_member = ()
                from_member = ()
        else:
            to_member = ()
            from_member = ()
        if Queue.objects.filter(book=b).exists() :
            qset = Queue.objects.filter(book=b).order_by('id').values('member__user__first_name','member__user__last_name')
        else :
            qset = ()
        return {'queue':qset,'to_member':to_member,'from_member':from_member}
#        return render_to_response('rapocore/viewqueue.html',{ 'book': b.title,'queue':qset,'to_member':to_member}, RequestContext(request))

@login_required
def BookReviewDetails(request, bookid):
    try:
        user = SocialAccount.objects.get(user_id = request.user)
        bookReviews = BookReview.objects.select_related().get(book_id= bookid, reviewer_id=user.id)
    except Exception:
        bookReviews = None
    return {'bookReviews': bookReviews}

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
             #Message for facebook comment
        if b.comments and FACEBOOKGROUP_ID in b.comments:
            msg = "Automated message: \nI would like to read it please!"
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                graph.put_comment(b.comments,msg)
            except:
                logging.debug('Facebook post failed')
        else:
            msg = "Automated message: \nI would like to read the book titled \'"+b.book.title+"\' with id "+str(b.id)+" currently with "+str(b.withmember.user.first_name)+" "+str(b.withmember.user.last_name)
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                b.save(update_fields=['comments'])
            except:
                logging.debug('Facebook post failed')


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
            #Message for facebook comment
            if b.comments and FACEBOOKGROUP_ID in b.comments:
                msg = "Automated message: \nI sent it on "+f.date_sent+"via"+f.via
                try:
                    graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                    graph.put_comment(b.comments,msg)
                except:
                    logging.debug('Facebook post failed')
            else:
                msg = "Automated message: \nI sent the book titled\'"+b.book.title+"\' with id "+str(b.id)
                try:
                    graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                    b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                    b.save(update_fields=['comments'])
                except:
                    logging.debug('Facebook post failed')

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
def WithdrawBook(request,bookid):
        b = RealBook.objects.get(id= bookid)
        Queue.objects.filter(book=b).delete() # Delete all queued entries for the book
        msg = "Automated message: \nI don't want to part with"+b.book.title+" with id "+str(b.id)+". Changed my mind. Sorry!Thanks!"
        if b.comments and FACEBOOKGROUP_ID in b.comments:
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                graph.put_comment(b.comments,msg)
            except:
                logging.debug('Facebook post failed')
        else:
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                #b.save(update_fields=['comments'])
            except:
                logging.debug('Facebook post failed')

        b.delete()
        success = True # Success will be false when sender has already sent to this person - To be implemented TBD
        return render_to_response('rapocore/withdrawbook.html',{ 'book': b.book.title, 'success': success}, RequestContext(request))


@login_required
def CancelRequest(request,bookid):
        b = RealBook.objects.get(id= bookid)
        instance = Queue.objects.get(member=SocialAccount.objects.get(user_id=request.user),book=b)
        instance.delete()
         
        if b.comments and FACEBOOKGROUP_ID in b.comments:
            msg = "Automated message: \nI don't want it. Changed my mind. Thanks!"
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                graph.put_comment(b.comments,msg)
            except:
                logging.debug('Facebook post failed')
        else:
            msg = "Automated message: \nI don't want the book titled "+b.book.title+" with id "+str(b.id)+". Changed my mind! Thanks!"
            try:
                graph = GraphAPI(SocialToken.objects.get(account = SocialAccount.objects.get(user = request.user)).token)
                b.comments = graph.put_wall_post(msg, {},FACEBOOKGROUP_ID)['id'] # permalink
                b.save(update_fields=['comments'])
            except:
                logging.debug('Facebook post failed')

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
        #rbook = RealBook.objects.select_related().get(id= bookid)
        book = Book.objects.select_related().get(id= bookid)
        bookReviewDetails = BookReviewDetails(request, book.id)
        if request.method == 'POST': # If the form has been submitted...
                form = WriteBookReviewForm(request.user,bookReviewDetails,request.POST) # A form bound to the POST data
                if form.has_changed():
                        if form.is_valid():
                                f_type = form.save(commit=False)
                                f_type.reviewer = SocialAccount.objects.get(user_id = request.user)
                                f_type.book_id = book.id
                                if bookReviewDetails['bookReviews'] and bookReviewDetails['bookReviews'].status == 'S':
                                        f_type.id = bookReviewDetails['bookReviews'].id
                                f_type.save()
                                #book.publisher = form.cleaned_data['spublisher']
                                #book.save()
                                #form.save_m2m()
                                #print "the form is valid"
                                return HttpResponseRedirect('/thanks/')
                        else:
                                 messages.error(request, "Error")
        else:
                form = WriteBookReviewForm(request.user, bookReviewDetails)
        return render_to_response('rapocore/write_bookreviewform.html',{ 'form': form, 
                                'formtitle':'Write book review', 
                                'formnote':'Share your views of the book with others...', 
                                'book':book,
                                'submitmessage':'Submit Review', 'formaction':'writebookreview/'+bookid},RequestContext(request))

@login_required
def RAPOBookReviewsList(request,bookid):
        #rbook = RealBook.objects.select_related().get(id= bookid)
        book = Book.objects.select_related().get(id= bookid)
        #rapoReviewDetails = RAPOReviewDetails(request, book.id)
        avg_rating = BookReview.objects.select_related().filter(status = 'A', book_id = book.id).aggregate(Avg('rating'))
        rapoReview = BookReview.objects.select_related().filter(status = 'A', book_id = book.id).values('id','rating','review','reviewer_id__user__first_name','reviewer_id__user__last_name')
        data = {  'book' : book,  'rapoReview': rapoReview, 'avg_rating':avg_rating['rating__avg']}
        return render_to_response('rapocore/rapo_bookreview_list.html', data, RequestContext(request))


@login_required
def RAPOBookReviewsDetails(request,bookid,reviewid):
        book = Book.objects.select_related().get(id= bookid)
        #rbook = RealBook.objects.select_related().get(book_id= bookid)
        avg_rating = BookReview.objects.select_related().filter(status = 'A', book_id = bookid).aggregate(Avg('rating'))
        rapoReview = BookReview.objects.select_related('id','rating','review','reviewer_id__user__first_name','reviewer_id__user__last_name').get(id = reviewid)
        reviewer = SocialAccount.objects.select_related().get(id=rapoReview.reviewer_id)
        #reviewername = User.objects.select_related().get(id = reviewer.user_id)
        bookReviewDetails = BookReviewDetails(request, bookid)
        data = {  'book' : book, 'rapoReview': rapoReview, 'avg_rating':avg_rating['rating__avg'], 'reviewer': reviewer.user.first_name+" " + reviewer.user.last_name,'bookReviews': bookReviewDetails}
        data.update(bookReviewDetails)
        return render_to_response('rapocore/rapo_bookreview_details.html', data, RequestContext(request))


@login_required
def FeedbackPage(request):
        #feedbackList = Feedback.objects.all().order_by('-id').select_related()
        return render_to_response('rapocore/feedback.html',{  
                        'formtitle': 'Feedback/Query Page' }, RequestContext(request))

@login_required

def MemberProfile(request,username):
    try:
        uid = User.objects.get(username = username)
        me = SocialAccount.objects.get(user_id=uid)
    except User.DoesNotExist:
        print "User does not exist"
    else:
        booksreleased = RealBook.objects.filter(ownermember = me).order_by('datereleased')
        booksrequested = Queue.objects.filter(member= me).select_related()
        bookswith = RealBook.objects.filter(withmember=me).select_related().exclude(status=RealBook.TRANSIT)
        booksintransitfromme = Transaction.objects.filter(Q(book__withmember=me)&Q(from_member=me)&Q(book__status=RealBook.TRANSIT)).select_related()
        booksintransittome = Transaction.objects.filter(Q(date_received__isnull=True)&Q(to_member=me)&Q(book__status=RealBook.TRANSIT)).select_related()
    return render_to_response('rapocore/memberprofile.html',{ 'member': me, 'booksreleased': booksreleased, 'booksrequested': booksrequested,'bookswith': bookswith, 'booksintransitfromme': booksintransitfromme,'booksintransittome': booksintransittome}, RequestContext(request))

class MemberListView(ListView):
    model  = SocialAccount
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MemberListView, self).get_context_data(**kwargs)
        return context

