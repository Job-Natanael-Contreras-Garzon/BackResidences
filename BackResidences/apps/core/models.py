from django.db import models

class BaseModel(models.Model):
    """
    Modelo base con campos comunes para auditoría
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        abstract = True

class TimestampedModel(models.Model):
    """
    Modelo base solo con timestamps
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True