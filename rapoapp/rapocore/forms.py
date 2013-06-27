from django import forms
from django.forms import ModelForm
from django.db.models import Q
from rapoapp.rapocore.models import Author
from rapoapp.rapocore.models import Book
from rapoapp.rapocore.models import Member
from rapoapp.rapocore.models import Tag
from rapoapp.rapocore.models import Transaction


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = [ 'first_name', 'last_name' ]

class SearchForm(forms.Form):
    stitle = forms.CharField(label= 'Title contains')
    sauthor = forms.CharField(label='Author contains')
    slanguage = forms.ChoiceField(choices=Book.LANG_CHOICES,label='Language')
    #stag = forms.ChoiceField(choices=Tag.objects.all())
    #smember = forms.ChoiceField(choices=Member.objects.all())
    #sstatus = forms.ChoiceField(choices=Transaction.objects.all())
    #scity = forms.ChoiceField(choices=Member.objects.all())

class ReleaseBookForm(ModelForm):
    class Meta:
	model = Book
	exclude = [ 'datereleased', 'ownermember' ]

class SendBookForm(ModelForm):
    class Meta:
	model = Transaction
	fields = [ 'book', 'to_member', 'date_sent', 'via', 'tracking', 'status', 'charges', 'charges_on' ]

class ReceiveBookForm(ModelForm):
    class Meta:
	model = Transaction
	fields = [ 'book', 'date_received' ]
