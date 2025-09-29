from django.contrib import admin
from .models import TipoReporte, Reporte, Aviso, AvisoVisto

admin.site.register(TipoReporte)
admin.site.register(Reporte)
admin.site.register(Aviso)
admin.site.register(AvisoVisto)
