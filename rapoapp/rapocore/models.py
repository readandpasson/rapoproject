# Create your models here.

from django.db import models
from datetime import datetime
from datetime import date
from django.contrib.auth.models import User
from django.forms import ModelForm
from allauth.socialaccount.models import SocialAccount
from rapogen.models import Book,Author,Genre, Language



class RealBook(models.Model):
    AVAILABLE='A'
    READ='R'
    TRANSIT='T'
    BOOKED='B'
    LOST='L'
    DELETED='D'
    STATUS_CHOICES = (
        (AVAILABLE,'Available'),
        (READ,'Reading'),
        (TRANSIT,'In Transit'),
        (BOOKED,'Reserved'),
        (LOST,'Lost'),
        (DELETED,'Deleted'),
    )
    book= models.ForeignKey(Book)
    ownermember = models.ForeignKey(SocialAccount,related_name='OriginalOwner',verbose_name='Original Owner')
    withmember = models.ForeignKey(SocialAccount,related_name='CurrentlyWith',verbose_name='Currently with')
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default=AVAILABLE)
    datereleased = models.DateTimeField( verbose_name='Date of release',auto_now_add=True)
    rqueue = models.ManyToManyField(SocialAccount,through='Queue',related_name='Queue',verbose_name='Reservation Queue')
    fb_permalink = models.TextField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)
    def __unicode__(self):
        return self.book.title
    class Meta:
        ordering = ['book']

    @property
    def is_new(self):
        if (date.today() -  self.datereleased.date()).total_seconds() < 604800:  # 7 days
           return True
        return False

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
    book = models.ForeignKey(RealBook)
    from_member = models.ForeignKey(SocialAccount,related_name='from')
    to_member = models.ForeignKey(SocialAccount,related_name='to')
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField(null=True,blank=True)
    via = models.CharField(max_length=100,null=True,blank=True)
    tracking = models.CharField(max_length=256,null=True,blank=True,verbose_name='Tracking id/url')
    charges = models.CharField(max_length=20,null=True,blank=True)
    charges_on = models.CharField(max_length=1,choices=CHARGE_CHOICES,default=NA)
    comments = models.TextField(null=True,blank=True)

    class Meta:
            ordering = ['date_sent']
            unique_together =(('book','from_member','to_member','date_sent'),)

    def __unicode__(self):
        return u'%s : %s %s --> %s %s ON %s' % (self.book,self.from_member.user.first_name,self.from_member.user.last_name,self.to_member.user.first_name,self.to_member.user.last_name,self.date_sent)

class Queue(models.Model):
    book = models.ForeignKey(RealBook)
    member = models.ForeignKey(SocialAccount)
    class Meta:
        ordering = ['id']
        unique_together =(('book','member'),)
    def __unicode__(self):
        return "%s " % (self.book.title)


class Defect(models.Model):
    OPEN='OP'
    CLOSED='CL'
    NOTDEFECT='ND'
    INFUTURE='FU'
    ARCHIVED='AR'
    DEFECT_STATUS_CHOICES = (
        (OPEN,'Open'),
        (CLOSED,'Closed'),
        (NOTDEFECT,'Not a defect'),
        (INFUTURE,'In future'),
        (ARCHIVED,'Archived'),
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
    def __unicode__(self):
        return self.description
    class Meta:
        ordering = ['-logdate']

# Benitha: 13-Nov-2013 Model for book cover img
#class Document(models.Model):
#       docfile = models.FileField(upload_to='documents/%Y/%m/%d')
