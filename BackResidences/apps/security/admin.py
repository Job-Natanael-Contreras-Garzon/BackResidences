from django.contrib import admin
from .models import TipoEvento, EventoSeguridad, VehiculoAutorizado, CredentialAcceso, Zona, Camara

admin.site.register(TipoEvento)
admin.site.register(EventoSeguridad)
admin.site.register(VehiculoAutorizado)
admin.site.register(CredentialAcceso)
admin.site.register(Zona)
admin.site.register(Camara)