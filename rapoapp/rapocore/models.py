# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms import ModelForm
from allauth.socialaccount.models import SocialAccount


class Author(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)

    class Admin:
        pass
    def __unicode__(self):
        return self.first_name+" "+self.last_name
    def _get_full_name(self):
        return '%s %s' % (self.first_name,self.last_name)
    full_name= property(_get_full_name)
    class Meta:
        ordering = ["first_name"]
        unique_together =(("first_name","last_name"),)


class Language(models.Model):
    languagename = models.CharField(unique=True,max_length=25)

    def __unicode__(self):
                return self.languagename
    class Meta:
                ordering = ["languagename"]

class Tag(models.Model):
    taglabel = models.CharField(unique=True,max_length=25)
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
                return self.taglabel
    class Meta:
                ordering = ["taglabel"]


class Book(models.Model):
    title = models.CharField(verbose_name="Title of the book",max_length=255)
    author = models.ManyToManyField(Author)
    #publisher = models.ForeignKey(PU)
    tag = models.ManyToManyField(Tag)
    language = models.ForeignKey(Language,default='English')
    ownermember = models.ForeignKey(SocialAccount,related_name='OriginalOwner',verbose_name="Original Owner")
    withmember = models.ForeignKey(SocialAccount,related_name='CurrentlyWith',verbose_name="Currently with")
    datereleased = models.DateTimeField( verbose_name='Date of release',auto_now_add=True)
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ["title"]


class Transaction(models.Model):
    AVAILABLE='A'
    READ='R'
    TRANSIT='T'
    BOOKED='B'
    STATUS_CHOICES = (
        (AVAILABLE,'Available'),
        (READ,'Reading'),
        (TRANSIT,'In Transit'),
        (BOOKED,'Reserved'),
    )
    REC='R'
    SEN='S'
    SHARED = 'D'
    NA = 'N'
    CHARGE_CHOICES = (
        (REC,'Receiver'),
        (SEN,'Sender'),
        (SHARED,'Shared'),
        (NA,'Not Applicable'),
    )
    book = models.ForeignKey(Book)
    from_member = models.OneToOneField(SocialAccount,related_name='from')
    to_member = models.OneToOneField(SocialAccount,related_name='to')
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField(null=True,blank=True)
    via = models.CharField(max_length=100,null=True,blank=True)
    tracking = models.CharField(max_length=30,null=True,blank=True)
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default=AVAILABLE)
    charges = models.CharField(max_length=20,null=True,blank=True)
    charges_on = models.CharField(max_length=1,choices=CHARGE_CHOICES,default=NA)
    comments = models.TextField(null=True,blank=True)

    class Meta:
            ordering = ["date_sent"]

class History(models.Model):
    book = models.ForeignKey(Book)
    member = models.ForeignKey(SocialAccount)
    rating = models.DecimalField(max_digits=2,decimal_places=1)
    review = models.TextField()
    comments = models.TextField(null=True,blank=True)

class Privilege(models.Model):
    privilege = models.ManyToManyField(SocialAccount)

class Queue(models.Model):
    book = models.ForeignKey(Book)
    member = models.ForeignKey(SocialAccount)
    position = models.IntegerField()

class Buylink(models.Model):
    book = models.ForeignKey(Book)
    link = models.URLField()


