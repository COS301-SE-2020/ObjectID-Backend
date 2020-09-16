from django.contrib import admin

from .models import Vehicle, Damage, DamageType

# Register your models here.

admin.site.register(Vehicle)
admin.site.register(Damage)
admin.site.register(DamageType)