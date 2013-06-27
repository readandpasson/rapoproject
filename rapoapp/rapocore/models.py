# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.forms import ModelForm


class Author(models.Model):
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    email = models.EmailField(null=True,blank=True)
    comments = models.TextField(null=True,blank=True)

    class Admin:
	pass
    def __unicode__(self):
	return self.first_name+" "+self.last_name
    class Meta:
	ordering = ["first_name"]

class Tag(models.Model):
    taglabel = models.CharField(unique=True,max_length=25)
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
	return self.taglabel
    class Meta:
	ordering = ["taglabel"]


class Member(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
	(MALE,'Male'),
	(FEMALE,'Female'),
    )
    ADMIN = 'A'
    BASIC = 'B'
    GUEST = 'G'
    REGISTERED = 'R'
    EXPIRED = 'E'
    LOYAL = 'L'
    TYPE_CHOICES = (
 	(ADMIN,'Admin'),
	(BASIC,'Basic Member'),
	(GUEST,'Guest'),
	(REGISTERED,'Registered'),
	(EXPIRED,'Membership expired'),
	(LOYAL,'Loyal Member'),
    )
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    gender = models.CharField(max_length=1,choices=GENDER_CHOICES,default=MALE)
    username = models.ForeignKey(User)
    facebook_id = models.IntegerField(blank=True, null=True)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=25)
    address = models.CharField(max_length=150,null=True,blank=True)
    city = models.CharField(max_length=20)
    phone = models.CharField(max_length=20,null=True,blank=True)
    mobile = models.CharField(max_length=20,null=True,blank=True)
    datesince = models.DateTimeField(null=True,blank=True)
    membertype = models.CharField(max_length=1,choices=TYPE_CHOICES,default=GUEST)
    #pic = models.ImageField()
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
	return self.first_name+" "+self.last_name
    class Meta:
	ordering = ["first_name"]


class Book(models.Model):
    ENG='ENG'
    TAM='TAM'
    TEL='TEL'
    MAL='MAL'
    KAN='KAN'
    HIN='HIN'
    LANG_CHOICES = (
	(ENG,'English'),
	(TAM,'Tamil'),
	(TEL,'Telugu'),
	(MAL,'Malayalam'),
	(KAN,'Kannada'),
	(HIN,'Hindi'),
    )
    title = models.CharField(max_length=255)
    author = models.ManyToManyField(Author)
    #publisher = models.ForeignKey(PU)
    tag = models.ManyToManyField(Tag)
    language = models.CharField(max_length=3,choices=LANG_CHOICES,default=ENG)
    ownermember = models.ForeignKey(Member)
    datereleased = models.DateTimeField('date of release')
    def __unicode__(self):
	return self.title
    class Meta:
	ordering = ["title"]


class Transaction(models.Model):
    AVAIL='A'
    READ='R'
    TRANS='I'
    BOOKED='B'
    STATUS_CHOICES = (
 	(AVAIL,'Available'),
	(READ,'Reading'),
	(TRANS,'In Transit'),
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
    from_member = models.ForeignKey(Member,related_name='from')
    to_member = models.ForeignKey(Member,related_name='to')
    date_sent = models.DateTimeField()
    date_received = models.DateTimeField(null=True,blank=True)
    via = models.CharField(max_length=100,null=True,blank=True)
    tracking = models.CharField(max_length=30,null=True,blank=True)
    status = models.CharField(max_length=1,choices=STATUS_CHOICES,default=AVAIL)
    charges = models.CharField(max_length=20,null=True,blank=True)
    charges_on = models.CharField(max_length=1,choices=CHARGE_CHOICES,default=NA)
    comments = models.TextField(null=True,blank=True)

class History(models.Model):
    book = models.ForeignKey(Book)
    member = models.ForeignKey(Member)
    rating = models.DecimalField(max_digits=2,decimal_places=1)
    review = models.TextField()
    comments = models.TextField(null=True,blank=True)

class Privilege(models.Model):
    privilege = models.ManyToManyField(Member)

class Queue(models.Model):
    book = models.ForeignKey(Book)
    member = models.ForeignKey(Member)
    position = models.IntegerField()

class Buylink(models.Model):
    book = models.ForeignKey(Book)
    link = models.URLField()


class BookReleaseForm(ModelForm):
    class Meta:
	model = Book

class BookSendForm(ModelForm):
    class Meta:
	model = Transaction

