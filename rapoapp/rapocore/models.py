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
        return self.first_name+' '+self.last_name
    def _get_full_name(self):
        return '%s %s' % (self.first_name,self.last_name)
    full_name= property(_get_full_name)
    class Meta:
        ordering = ['first_name']
        unique_together =(('first_name','last_name'),)


class Language(models.Model):
    languagename = models.CharField(unique=True,max_length=25)

    def __unicode__(self):
                return self.languagename
    class Meta:
                ordering = ['languagename']

class Tag(models.Model):
    taglabel = models.CharField(unique=True,max_length=25)
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
                return self.taglabel
    class Meta:
                ordering = ['taglabel']


class Book(models.Model):
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
    title = models.CharField(verbose_name='Title of the book',max_length=255)
    author = models.ManyToManyField(Author)
    #publisher = models.ForeignKey(PU)
    tag = models.ManyToManyField(Tag)
    language = models.ForeignKey(Language,default='English')
    ownermember = models.ForeignKey(SocialAccount,related_name='OriginalOwner',verbose_name='Original Owner')
    withmember = models.ForeignKey(SocialAccount,related_name='CurrentlyWith',verbose_name='Currently with')
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default=AVAILABLE)
    datereleased = models.DateTimeField( verbose_name='Date of release',auto_now_add=True)
    rqueue = models.ManyToManyField(SocialAccount,through='Queue',related_name='Queue',verbose_name='Reservation Queue')
    comments = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['title']


class Transaction(models.Model):
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
    from_member = models.ForeignKey(SocialAccount,related_name='from')
    to_member = models.ForeignKey(SocialAccount,related_name='to')
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField(null=True,blank=True)
    via = models.CharField(max_length=100,null=True,blank=True)
    tracking = models.CharField(max_length=30,null=True,blank=True)
    charges = models.CharField(max_length=20,null=True,blank=True)
    charges_on = models.CharField(max_length=1,choices=CHARGE_CHOICES,default=NA)
    comments = models.TextField(null=True,blank=True)

    class Meta:
            ordering = ['date_sent']
            unique_together =(('book','from_member','to_member','date_sent'),)

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
    class Meta:
        unique_together =(('book','member'),)


class Buylink(models.Model):
    book = models.ForeignKey(Book)
    link = models.URLField()

class Defect(models.Model):
    OPEN='OP'
    CLOSED='CL'
    NOTDEFECT='ND'
    INFUTURE='FU'
    DEFECT_STATUS_CHOICES = (
        (OPEN,'Open'),
        (CLOSED,'Closed'),
        (NOTDEFECT,'Not a defect'),
        (INFUTURE,'In future'),
    )
    SITEFUNCTIONALITY='SF'
    BOOKRELATED='BK'
    AESTHETIC='AE'
    DESIRABLE='DE'
    OTHER='OT'
    DEFECT_CATEGORY_CHOICES = (
        (SITEFUNCTIONALITY,'Site functionality'),
        (BOOKRELATED,'Books Entry related'),
        (AESTHETIC,'Aesthetic'),
        (DESIRABLE,'Desirable feature'),
        (OTHER,'Other'),
    )
    description = models.TextField() 
    category = models.CharField(max_length=2,choices=DEFECT_CATEGORY_CHOICES,default=OTHER)
    bymember = models.ForeignKey(SocialAccount,related_name='By')
    logdate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2,choices=DEFECT_STATUS_CHOICES,default=OPEN)
    fixedon = models.DateTimeField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)
