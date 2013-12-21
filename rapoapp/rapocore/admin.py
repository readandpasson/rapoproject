from django.contrib import admin
from rapocore.models import RealBook,Transaction, Defect
from rapogen.models import Book,Author,Genre,BookReview,Language
from allauth.socialaccount.models import SocialAccount


admin.site.register(Book)
admin.site.register(RealBook)
admin.site.register(BookReview)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Transaction)
admin.site.register(Defect)
