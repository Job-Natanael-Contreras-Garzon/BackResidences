from django.db import models
from apps.core.models import BaseModel
from apps.authentication.models import User

class Vivienda(BaseModel):
    """Viviendas del condominio"""
    usuario_propietario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='viviendas_propiedad',
        verbose_name="Propietario"
    )
    usuario_inquilino = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='viviendas_alquiler',
        verbose_name="Inquilino"
    )
    identificador = models.CharField(max_length=20, unique=True, verbose_name="Identificador")
    bloque = models.CharField(max_length=10, blank=True, verbose_name="Bloque")
    piso = models.IntegerField(null=True, blank=True, verbose_name="Piso")
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('apartamento', 'Apartamento'),
            ('casa', 'Casa'),
            ('local', 'Local'),
        ],
        verbose_name="Tipo"
    )
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Metros cuadrados")
    habitaciones = models.IntegerField(default=0, verbose_name="Habitaciones")
    banos = models.IntegerField(default=0, verbose_name="Baños")
    cuota_administracion = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Cuota de administración")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    def __str__(self):
        return f"Vivienda {self.identificador}"

    class Meta:
        verbose_name = "Vivienda"
        verbose_name_plural = "Viviendas"

class PersonaAutorizada(BaseModel):
    """Personas autorizadas por vivienda"""
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    autorizado_por = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autorizado por")
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    parentesco = models.CharField(max_length=50, verbose_name="Parentesco")
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de fin")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.vivienda.identificador}"

    class Meta:
        verbose_name = "Persona Autorizada"
        verbose_name_plural = "Personas Autorizadas"

class Mascota(BaseModel):
    """Mascotas registradas por vivienda"""
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE, verbose_name="Vivienda")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    especie = models.CharField(max_length=50, verbose_name="Especie")
    raza = models.CharField(max_length=100, blank=True, verbose_name="Raza")
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Peso (kg)")
    color = models.CharField(max_length=50, blank=True, verbose_name="Color")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    vacunas_al_dia = models.BooleanField(default=False, verbose_name="Vacunas al día")
    foto_url = models.URLField(null=True, blank=True, verbose_name="Foto")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    def __str__(self):
        return f"{self.nombre} - {self.vivienda.identificador}"

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"