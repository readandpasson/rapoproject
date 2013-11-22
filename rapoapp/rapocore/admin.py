from django.contrib import admin
from rapocore.models import Book,Author,Tag,Transaction,Privilege,Buylink,Queue,Language, Defect
from allauth.socialaccount.models import SocialAccount

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(Language)
admin.site.register(Transaction)
admin.site.register(Queue)
admin.site.register(Defect)
