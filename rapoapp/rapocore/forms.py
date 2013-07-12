from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
from rapoapp.rapocore.widgets import MultipleSelectWithPopUp, SelectWithPopUp
#from django.db.models import Q
from rapoapp.rapocore.models import Author,Language, Tag
from rapoapp.rapocore.models import Transaction, Book
from allauth.socialaccount.models import SocialAccount

class LanguageForm(ModelForm):
    class Meta:
        model = Language
        fields = [  'languagename' ]

class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = [  'taglabel' ]

class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = [ 'first_name', 'last_name' ]

class SearchForm(forms.Form):
    stitle = forms.CharField(label= 'Title contains')
    sauthor = forms.CharField(label='Author contains')
    #slanguage = forms.ModelMultipleChoiceField(Language.objects,label='Language')
    slanguage = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in Language.objects.all()],label ='Language')
    stag = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in Tag.objects.all()],label ='Tag')
    sownermember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in SocialAccount.objects.all()],label ='Original Owner')
    swithmember = forms.ChoiceField(choices=[('','-----')]+[ (o.id, str(o)) for o in SocialAccount.objects.all()],label ='Book currently with')
    sstatus = forms.ChoiceField(choices=tuple([(u'', u'-----')] + list(Transaction.STATUS_CHOICES)),label='Status')
    #scity = forms.ChoiceField(choices=[ (o.id, str(o.city)) for o in SocialAccount.objects.all()],label ='City')


class ReleaseBookForm(ModelForm):
    author = forms.ModelMultipleChoiceField(Author.objects, widget= MultipleSelectWithPopUp)
    tag = forms.ModelMultipleChoiceField(Tag.objects, widget= MultipleSelectWithPopUp)
    language = forms.ModelChoiceField(Language.objects, widget= SelectWithPopUp) 
    class Meta:
        model = Book
        fields = [ 'title', 'author', 'tag', 'language']

    def __init__(self, user, *args, **kwargs):
        super(ReleaseBookForm, self).__init__(*args, **kwargs)
        self.ownermember = user
        self.withmember = user


class SendBookForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'book', 'to_member', 'date_sent', 'via', 'tracking', 'charges', 'charges_on' ]

    def __init__(self, user, *args, **kwargs):
        super(SendBookForm, self).__init__(*args, **kwargs)
        self.from_member = user
        self.fields["book"].queryset = Book.objects.filter(withmember= SocialAccount.objects.get(user= user))
        self.fields["to_member"].queryset = SocialAccount.objects.all().exclude(user=user)
        self.fields["date_sent"].widget =  widgets.AdminSplitDateTime()


class ReceiveBookForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'book', 'date_received' ]

    def __init__(self, user, *args, **kwargs):
        super(ReceiveBookForm, self).__init__(*args, **kwargs)
        self.to_member = user
        self.fields["book"].queryset = Book.objects.filter(transaction__to_member=SocialAccount.objects.get(user=user),transaction__status=Transaction.TRANSIT)
        self.fields["date_received"].widget =  widgets.AdminSplitDateTime()

class PassonForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'book' ]

    def __init__(self, user, *args, **kwargs):
        super(PassonForm, self).__init__(*args, **kwargs)
        self.to_member = user
        self.fields["book"].queryset = Book.objects.filter(transaction__to_member=SocialAccount.objects.get(user=user),transaction__status=Transaction.READ)
