from django.contrib import admin
from rapocore.models import Book,Author,Member,Tag,Transaction,Queue,Privilege,Buylink,History

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Member)
admin.site.register(Tag)
admin.site.register(Transaction)
admin.site.register(Queue)
admin.site.register(Privilege)
admin.site.register(Buylink)
admin.site.register(History)
