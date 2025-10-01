from django.apps import AppConfig


class CommonAreasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.common_areas'
    verbose_name = 'Áreas Comunes'
    
    def ready(self):
        """
        Configuración inicial de la aplicación
        """
        # Importar señales si las hubiera
        # import apps.common_areas.signals
        pass