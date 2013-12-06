from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
from rapoapp.rapocore.widgets import MultipleSelectWithPopUp, SelectWithPopUp
from rapoapp.rapocore.models import Author,Language, Tag, Transaction, Book, Queue, Defect
from allauth.socialaccount.models import SocialAccount
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

class Add2QueueForm(ModelForm):
    class Meta:
        model = Book
        fields = [  'rqueue' ]

    def __init__(self, bookid, *args, **kwargs):
        super(Add2QueueForm, self).__init__(*args, **kwargs)
        self.id= bookid
        self.fields['rqueue'].queryset= Book.objects.get(id=bookid).rqueue.all()

class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = [  'languagename' ]

class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = [  'taglabel' ]

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
    stag = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in Tag.objects.all()],label ='Genre')
    sownermember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, force_text(u'%s %s (%s)' % (o.user.first_name,o.user.last_name,o.user.username))) for o in SocialAccount.objects.all().order_by(u'user__first_name',u'user__last_name')],label ='Original Owner')
    #sownermember = forms.ChoiceField(choices=[('','-----')],label ='Original Owner')
    #swithmember = forms.ChoiceField(choices=[('','-----')],label = 'Book currently with')
    swithmember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, force_text(u'%s %s (%s)' % (o.user.first_name,o.user.last_name,o.user.username))) for o in SocialAccount.objects.all().order_by(u'user__first_name',u'user__last_name')],label = 'Book currently with')
    sstatus = forms.ChoiceField(choices=tuple([(u'', u'-----')] + list(Book.STATUS_CHOICES)),label='Status')
    #scity = forms.ChoiceField(choices=[ (o.id, str(o.city)) for o in SocialAccount.objects.all()],label ='City')

    def __init__(self, user, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['stitle'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sauthor'].widget.attrs.update({'class' : 'form-control'})
        self.fields['stag'].widget.attrs.update({'class' : 'form-control'})
        self.fields['slanguage'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sownermember'].widget.attrs.update({'class' : 'form-control'})
        self.fields['swithmember'].widget.attrs.update({'class' : 'form-control'})
        self.fields['sstatus'].widget.attrs.update({'class' : 'form-control'})

class ReleaseBookForm(ModelForm):

    title = forms.CharField(widget=forms.TextInput(attrs={'size':'50'}))
    author = forms.ModelMultipleChoiceField(queryset=Author.objects.order_by('first_name'), widget= MultipleSelectWithPopUp)
    tag = forms.ModelMultipleChoiceField(Tag.objects, widget= MultipleSelectWithPopUp)
    language = forms.ModelChoiceField(Language.objects, widget= SelectWithPopUp) 
#    docfile = forms.FileField(label='Select the book cover', help_text='Max. size 1MB')
    class Meta:
        model = Book
        fields = [ 'title', 'author', 'tag', 'language']

    def __init__(self, user, *args, **kwargs):
        super(ReleaseBookForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class' : 'form-control'})
        self.fields['author'].widget.attrs.update({'class' : 'form-control'})
        self.fields['tag'].widget.attrs.update({'class' : 'form-control'})
        self.fields['language'].widget.attrs.update({'class' : 'form-control'})
        self.ownermember = user
        self.withmember = user
        self.status = Book.AVAILABLE
        self.fields['tag'].label = "Genre"
        self.fields['author'].help_text = "If there are multiple authors, hold down control key and select"
        self.fields['tag'].help_text = "If there are multiple genres, hold down control key and select"
        defLanguage = Language.objects.filter(languagename='English')
        self.fields['language'].initial = defLanguage[0].id


class ReceiveBookForm(ModelForm):
    class Meta:
        model = Transaction
        #fields = [ 'book', 'from_member', 'date_sent', 'via','tracking','charges','charges_on']
        fields = [ 'book']

    def __init__(self, user, *args, **kwargs):
        super(ReceiveBookForm, self).__init__(*args, **kwargs)
        self.fields['book'].widget.attrs.update({'class' : 'form-control'})
        self.to_member = user
        self.fields['book'].queryset = Book.objects.filter(transaction__to_member=SocialAccount.objects.get(user=user),status=Book.TRANSIT)
        #self.fields['from_member'].widget.attrs['readonly'] = True
        #self.fields['date_sent'].widget.attrs['readonly'] = True
        #self.fields['via'].widget.attrs['readonly'] = True
        #self.fields['tracking'].widget.attrs['readonly'] = True
        #self.fields['charges'].widget.attrs['readonly'] = True
        #self.fields['charges_on'].widget.attrs['readonly'] = True


class PassonForm(ModelForm):

    title = forms.ModelChoiceField(Book.objects,widget=forms.Select)
    class Meta:
        model = Book
        fields = [ 'title' , 'status']

    def __init__(self, user, *args, **kwargs):
        super(PassonForm, self).__init__(*args, **kwargs)
        self.fields['title'].queryset = Book.objects.filter(withmember=SocialAccount.objects.get(user=user),status=Book.READ)

class SendBookForm(ModelForm):
    book = forms.ModelChoiceField(Book.objects,widget=forms.Select(attrs={'onchange':'getmembersinqueue();'}))
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
        self.fields['book'].queryset = Book.objects.filter(withmember= SocialAccount.objects.get(user= user)).exclude(status=Book.TRANSIT)
        self.fields['date_sent'].widget =  widgets.AdminSplitDateTime()

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

