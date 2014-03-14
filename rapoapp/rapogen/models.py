from django.db import models
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User, UserManager
from django.db.models.signals import post_save

# Create your models here.
class Country(models.Model):
    iso_code = models.CharField(unique=True,max_length=2)
    name = models.CharField(max_length=50)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Region(models.Model):
    iso_code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class City(models.Model):
    iso_code = models.CharField(unique=True,max_length=3)
    name = models.CharField(max_length=50)
    region = models.ForeignKey(Region)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

        
#class Profile(User):
#    user = models.OneToOneField(User)
#    city = models.ForeignKey(City)
#    Nbooksreleased = models.IntegerField()
#    Nbookssent = models.IntegerField()
#    Nbookswith = models.IntegerField()
#    rating = models.IntegerField()
#    objects = UserManager()

#def __str__(self):  
#    return "%s's profile" % self.user  
#
#def create_profile(sender, instance, created, **kwargs):
#    if created:
#        profile, created = Profile.objects.get_or_create(user=instance)
#post_save.connect(create_profile, sender=User)

class Language(models.Model):
    languagename = models.CharField(unique=True,max_length=25)

    def __unicode__(self):
                return self.languagename
    class Meta:
                ordering = ['languagename']

class Genre(models.Model):
    genrelabel = models.CharField(unique=True,max_length=25)
    comments = models.TextField(null=True,blank=True)

    def __unicode__(self):
                return self.genrelabel
    class Meta:
                ordering = ['genrelabel']


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



class Book(models.Model):
    title = models.CharField(verbose_name='Title of the book',max_length=255)
    author = models.ManyToManyField(Author)
    genre = models.ManyToManyField(Genre)
    language = models.ForeignKey(Language,default='English')
    publisher = models.CharField(verbose_name='Publisher',max_length=255,null=True,blank=True)
    pages = models.PositiveSmallIntegerField(verbose_name='Number of pages',null=True,blank=True)
    comments = models.TextField(null=True,blank=True)
    imgurl = models.URLField(max_length=2048,null=True,blank=True)
    buyurl = models.URLField(max_length=2048,null=True,blank=True)
    avg_rating = models.FloatField(null=True,blank=True)
    def __unicode__(self):
        return self.title
    class Meta:
        ordering = ['title']


#@receiver(m2m_changed, sender=Book.author.through)
#def verify_uniqueness(sender, **kwargs):
#    book = kwargs.get('instance', None)
#    action = kwargs.get('action', None)
#    authors = kwargs.get('pk_set', None)
#
#    if action == 'pre_add':
#        for auth in authors:
#            if Book.objects.filter(title=book.title).filter(author=auth):
#                raise IntegrityError('Book with name %s already exists for publisher %s' % (book.title, Author.objects.get(pk=auth)))


class EBookFormat(models.Model):
        name = models.CharField(verbose_name="Name of format",max_length=50)
        reader_url = models.URLField(max_length=2048)

class EBook(models.Model):
        FREE='F'        
        PAID='P'
        PRICE_CHOICES = (
                (FREE,'Free'),
                (PAID,'Paid'),
        )
        book = models.ForeignKey(Book)
        eformat = models.ForeignKey(EBookFormat)
        pricestatus = models.CharField(max_length=1,choices=PRICE_CHOICES,default=FREE)
        download_url = models.URLField(max_length=2048)

class BookReview(models.Model):
        SUB ='S'
        APP ='A'
        REJ ='R'
        PUB ='P'
        STATUS_CHOICES =(
                (SUB,'Submitted'),
                (APP,'Approved'),
                (REJ,'Rejected'),
                (PUB,'Published'),
        )
        book = models.ForeignKey(Book)
        reviewer = models.ForeignKey(SocialAccount)
        review = models.TextField(null=True,blank=True)
        rating = models.PositiveSmallIntegerField(verbose_name='Rating')
        status = models.CharField(max_length=1,choices=STATUS_CHOICES,default=SUB)
        comments = models.TextField(null=True,blank=True)

class Feedback(models.Model):
    name = models.TextField()
    email = models.TextField(null=True,blank=True) 
    phone = models.TextField(null=True,blank=True) 
    subject = models.TextField()
    feedback = models.TextField()
    comments = models.TextField(null=True,blank=True)

#class UserProfile(models.Model):  
#    user = models.OneToOneField(User)  
#       location = models.
#    language = models.ForeignKey(Language,default='English')
#    #other fields here
#
#    def __str__(self):  
#          return "%s's profile" % self.user  
#
#       def create_user_profile(sender, instance, created, **kwargs):  
#       if created:  
#                       profile, created = UserProfile.objects.get_or_create(user=instance)  
#
#post_save.connect(create_user_profile, sender=User) 
#
