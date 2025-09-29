from django.contrib import admin
from .models import TipoPago, Deuda, DetalleDeuda, Pago

admin.site.register(TipoPago)
admin.site.register(Deuda)
admin.site.register(DetalleDeuda)
admin.site.register(Pago)