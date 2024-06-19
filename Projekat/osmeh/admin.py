from django.contrib import admin
from .models import *


# Register your models here.
#OVDE TREBAJU DA SE REGISTRUJU MODELI ZA ADMINA(SUPERUSERA)

admin.site.register(Korisnik)
admin.site.register(Admninistrator)
admin.site.register(Ordinacija)
admin.site.register(Pacijent)
admin.site.register(Rezervacija)
admin.site.register(Stomatolog)
admin.site.register(Usluga)