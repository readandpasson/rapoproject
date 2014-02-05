from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
from rapoapp.rapocore.widgets import MultipleSelectWithPopUp, SelectWithPopUp
from rapocore.models import RealBook,Transaction, Queue, Defect
from rapogen.models import Author,Book,Genre, Language, BookReview, Feedback
from allauth.socialaccount.models import SocialAccount
from django.utils.safestring import mark_safe

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

class Add2QueueForm(ModelForm):
    class Meta:
        model = RealBook
        fields = [  'rqueue' ]

    def __init__(self, bookid, *args, **kwargs):
        super(Add2QueueForm, self).__init__(*args, **kwargs)
        self.id= bookid
        self.fields['rqueue'].queryset= RealBook.objects.get(id=bookid).rqueue.all()

class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = [  'languagename' ]

class GenreForm(ModelForm):
    class Meta:
        model = Genre
        fields = [  'genrelabel' ]

#class Add2QueueForm(ModelForm):
#    class Meta:
#        model = Queue
#        fields = [  'position' ]


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = [ 'first_name', 'last_name' ]

class SearchForm(forms.Form):
    stitle = forms.CharField(label= 'Title contains')
    sauthor = forms.CharField(label='Author contains')
    #slanguage = forms.ModelMultipleChoiceField(Language.objects,label='Language')
    slanguage = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in Language.objects.all()],label ='Language')
# Benitha: 16-Nov-2013 Uncommented the Genre field search 
    sgenre = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in Genre.objects.all()],label ='Genre')
    sownermember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, force_text(u'%s %s (%s)' % (o.user.first_name,o.user.last_name,o.user.username))) for o in SocialAccount.objects.all().order_by(u'user__first_name',u'user__last_name')],label ='Original Owner')
    swithmember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, force_text(u'%s %s (%s)' % (o.user.first_name,o.user.last_name,o.user.username))) for o in SocialAccount.objects.all().order_by(u'user__first_name',u'user__last_name')],label = 'Book currently with')
    sstatus = forms.ChoiceField(choices=tuple([(u'', u'-----')] + list(RealBook.STATUS_CHOICES)),label='Status')
    #scity = forms.ChoiceField(choices=[ (o.id, str(o.city)) for o in SocialAccount.objects.all()],label ='City')

    def __init__(self, user, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['stitle'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sauthor'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sgenre'].widget.attrs.update({'class' : 'form-control'})
        self.fields['slanguage'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sownermember'].widget.attrs.update({'class' : 'form-control'})
        self.fields['swithmember'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sstatus'].widget.attrs.update({'class' : 'form-control'})
        self.fields['stitle'].help_text=mark_safe('Enter the title of the book to search')
        self.fields['sauthor'].help_text=mark_safe('Enter author''s name to search the list of books written by the author')
        self.fields['slanguage'].help_text=mark_safe('Select the language to search the books')
        self.fields['sgenre'].help_text=mark_safe('Select the genre to search the books')
        self.fields['sownermember'].help_text=mark_safe('Select to search the list of books released by the member')
        self.fields['swithmember'].help_text=mark_safe('Select to search the list of books currently with the member')
        self.fields['sstatus'].help_text=mark_safe('Select to search the list of books with a particular status')


class ReleaseBookForm(ModelForm):

    language = forms.ModelChoiceField(Language.objects, widget= SelectWithPopUp) 
    title = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    author = forms.ModelMultipleChoiceField(queryset=Author.objects.order_by('first_name'), widget= MultipleSelectWithPopUp)
    genre = forms.ModelMultipleChoiceField(Genre.objects, widget= MultipleSelectWithPopUp, initial=Genre.objects.filter(genrelabel='Uncategorized'))
#    docfile = forms.FileField(label='Select the book cover', help_text='Max. size 1MB')
    class Meta:
        model = Book
        fields = [ 'language', 'title', 'author', 'genre']

    def __init__(self, user, *args, **kwargs):
        super(ReleaseBookForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['author'].widget.attrs.update({'class' : 'form-control'})
        self.fields['genre'].widget.attrs.update({'class' : 'form-control'})
        self.fields['language'].widget.attrs.update({'class' : 'form-control'})
        #self.ownermember = user
        #self.withmember = user
        #self.status = RealBook.AVAILABLE
        defLanguage = Language.objects.filter(languagename='English')
        self.fields['language'].initial = defLanguage[0].id
        self.fields['language'].help_text=mark_safe('Select the language of the book')
        self.fields['title'].help_text=mark_safe('Enter the title of the book')
        self.fields['author'].help_text = mark_safe('If there are multiple authors, hold down control key and select')
        self.fields['genre'].help_text = mark_safe('If there are multiple genres, hold down control key and select')


class ReceiveBookForm(ModelForm):
    class Meta:
        model = Transaction
        #fields = [ 'book', 'from_member', 'date_sent', 'via','tracking','charges','charges_on']
        fields = [ 'book']

    def __init__(self, user, *args, **kwargs):
        super(ReceiveBookForm, self).__init__(*args, **kwargs)
        self.fields['book'].widget.attrs.update({'class' : 'form-control'})
        self.to_member = user
        self.fields['book'].queryset = RealBook.objects.filter(transaction__to_member=SocialAccount.objects.get(user=user),status=RealBook.TRANSIT)
        #self.fields['from_member'].widget.attrs['readonly'] = True
        #self.fields['date_sent'].widget.attrs['readonly'] = True
        #self.fields['via'].widget.attrs['readonly'] = True
        #self.fields['tracking'].widget.attrs['readonly'] = True
        #self.fields['charges'].widget.attrs['readonly'] = True
        #self.fields['charges_on'].widget.attrs['readonly'] = True


class PassonForm(ModelForm):

    title = forms.ModelChoiceField(RealBook.objects,widget=forms.Select)
    class Meta:
        model = RealBook
        fields = [ 'title' , 'status']

    def __init__(self, user, *args, **kwargs):
        super(PassonForm, self).__init__(*args, **kwargs)
        self.fields['title'].queryset = RealBook.objects.filter(withmember=SocialAccount.objects.get(user=user),status=RealBook.READ)

class SendBookForm(ModelForm):
    book = forms.ModelChoiceField(RealBook.objects,widget=forms.Select(attrs={'onchange':'getmembersinqueue();'}))
    to_member = forms.ModelChoiceField(SocialAccount.objects,widget=forms.Select(attrs={'disabled':'true'}))
    class Meta:
        model = Transaction
        fields = [ 'book','to_member', 'date_sent', 'via', 'tracking', 'charges', 'charges_on' ]

    def __init__(self, user, *args, **kwargs):
        super(SendBookForm, self).__init__(*args, **kwargs)
        self.from_member = user
        self.fields['book'].widget.attrs.update({'class' : 'form-control'})
        self.fields['to_member'].widget.attrs.update({'class' : 'form-control'})
        self.fields['date_sent'].widget.attrs.update({'class' : 'form-control'})
        self.fields['via'].widget.attrs.update({'class' : 'form-control'})
        self.fields['tracking'].widget.attrs.update({'class' : 'form-control'})
        self.fields['charges'].widget.attrs.update({'class' : 'form-control'})
        self.fields['charges_on'].widget.attrs.update({'class' : 'form-control'})
        self.fields['book'].queryset = RealBook.objects.filter(withmember= SocialAccount.objects.get(user= user)).exclude(status=RealBook.TRANSIT)
        self.fields['date_sent'].widget =  widgets.AdminSplitDateTime()
        self.fields['book'].help_text=mark_safe('Enter the title of the book to send')
        self.fields['to_member'].help_text=mark_safe('Select the recipient to send the book')

class SendBookToForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'date_sent', 'via', 'tracking', 'charges', 'charges_on' ]

    def __init__(self,user,bookid,memberid, *args, **kwargs):
        super(SendBookToForm, self).__init__(*args, **kwargs)
        self.from_member = user
        self.fields['date_sent'].widget =  widgets.AdminSplitDateTime()

class ReportDefectForm(ModelForm):
    #category = forms.ModelChoiceField(choices=Defect.DEFECT_CATEGORY_CHOICES,widget=forms.Select)
    #description = forms.TextField()
    class Meta:
        model = Defect
        fields = [ 'category', 'description' ]

    def __init__(self, user, *args, **kwargs):
        super(ReportDefectForm, self).__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class' : 'form-control'})
        self.fields['description'].widget.attrs.update({'class' : 'form-control'})
        self.bymember = user
        self.status = Defect.OPEN
        self.fields['category'].help_text=mark_safe('Select the category of the defect to be reported')
        self.fields['description'].help_text=mark_safe('Enter the details of the defect to be reported')


class CancelRequestForm(ModelForm):
    book = forms.ModelChoiceField(Book.objects,widget=forms.Select)
    class Meta:
        model = Queue
        fields = [ 'book' ]

    def __init__(self, user, *args, **kwargs):
        super(CancelRequestForm, self).__init__(*args, **kwargs)
        self.fields['book'].widget.attrs.update({'class' : 'form-control'})
        self.member = user
        self.fields['book'].queryset = Queue.objects.filter(member= SocialAccount.objects.get(user= user))
        self.fields['book'].help_text=mark_safe('Select the book to be cancelled')


class WriteBookReviewForm(ModelForm):
    #spublisher = forms.CharField(label= 'Publisher')
    #spages= forms.IntegerField(label= 'No. of Pages')
    #sbookprice= forms.FloatField(label='Book Price')
    rating= forms.ChoiceField(label= 'Rating', choices=(('1','1'),('2','2'),('3','3'),('4','4'),('5','5')))
    review= forms.CharField(label= 'Review', widget=forms.Textarea)
    sdeclare = forms.BooleanField(label='Declaration',initial=False)
    
    class Meta:
		model = BookReview
		fields = [ 'rating', 'review']

    def __init__(self, user, bookReviewDetails, *args, **kwargs):
        super(WriteBookReviewForm, self).__init__(*args, **kwargs)
        #self.fields['spublisher'].widget.attrs.update({'class' : 'form-control'})
        #self.fields['spages'].widget.attrs.update({'class' : 'form-control'})
        #self.fields['sbookprice'].widget.attrs.update({'class' : 'form-control'})
        self.fields['rating'].widget.attrs.update({'class' : 'form-control'})
        self.fields['review'].widget.attrs.update({'class' : 'form-control'})
        reviewParam=bookReviewDetails['bookReviews']
		
        if reviewParam:
            if reviewParam.reviewer.user.username == user.username and reviewParam.status == 'S':
                self.fields['review'].initial = reviewParam.review
                self.fields['rating'].initial = reviewParam.rating


