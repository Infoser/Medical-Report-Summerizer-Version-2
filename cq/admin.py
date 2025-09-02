from django.contrib import admin
from cq.models import contactd, queryd
# Register your models here.
class AdminContact(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'message')
admin.site.register(contactd , AdminContact)

class AdminQuery(admin.ModelAdmin):
    list_display = ('name', 'message')
admin.site.register(queryd , AdminQuery)
