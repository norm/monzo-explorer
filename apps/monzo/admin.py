from django.contrib import admin

from .models import Merchant, Transaction


admin.site.register(Transaction)
admin.site.register(Merchant)
