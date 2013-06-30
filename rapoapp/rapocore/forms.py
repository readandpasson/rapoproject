from django import forms
from django.forms import ModelForm
from django.contrib.admin import widgets
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
    stag = forms.ChoiceField(choices=[ (o.id, str(o)) for o in Tag.objects.all()],label ='Tag')
    smember = forms.ChoiceField(choices=[ (o.id, str(o)) for o in Member.objects.all()],label ='Member')
    sstatus = forms.ChoiceField(choices=Transaction.STATUS_CHOICES,label='Status')
    smember = forms.ChoiceField(choices=[ (o.id, str(o)) for o in Member.objects.all()],label ='Member')
    scity = forms.ChoiceField(choices=[ (o.id, str(o.city)) for o in Member.objects.all()],label ='City')

class ReleaseBookForm(ModelForm):
    class Meta:
        model = Book
        fields = [ 'title', 'author', 'tag', 'language']

    def __init__(self, user, *args, **kwargs):
        super(ReleaseBookForm, self).__init__(*args, **kwargs)
        self.ownermember = user

class SendBookForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'book', 'to_member', 'date_sent', 'via', 'tracking', 'status', 'charges', 'charges_on' ]

    def __init__(self, user, *args, **kwargs):
        super(SendBookForm, self).__init__(*args, **kwargs)
        self.from_member = user
        self.fields["book"].queryset = Book.objects.filter(ownermember= Member.objects.get(username= user))
        self.fields["to_member"].queryset = Member.objects.all().exclude(username=user)
        self.fields["date_sent"].widget =  widgets.AdminSplitDateTime()


class ReceiveBookForm(ModelForm):
    class Meta:
        model = Transaction
        fields = [ 'book', 'date_received' ]

    def __init__(self, user, *args, **kwargs):
        super(ReceiveBookForm, self).__init__(*args, **kwargs)
        self.to_member = user
        self.fields["book"].queryset = Transaction.objects.filter(to_member= Member.objects.get(username= user))
        self.fields["date_received"].widget =  widgets.AdminSplitDateTime()
