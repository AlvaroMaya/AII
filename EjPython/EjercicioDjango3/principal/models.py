from django.db import models

# Create your models here.
#Vino: IdVino, Nombre, Precio, DenominacionOrigen, TiposUvas.
#b) DenominacionOrigen: IdDenominacion, Nombre, Pais.
#c) Pais: IdPais, Nombre.
#d) TipoUva: IdUva, Nombre 

class Pais(models.Model):
    idPais = models.IntegerField(primary_key=True)
    nombre = models.TextField()
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre', )

class Uva(models.Model):
    idUva = models.IntegerField(primary_key=True)
    nombre = models.TextField()
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre', )

class DenominacionOrigen(models.Model):
    idDenominacion = models.IntegerField(primary_key=True)
    nombre = models.TextField(verbose_name='Denominacion')
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre', )

class Vino(models.Model):
    idVino = models.IntegerField(primary_key=True)
    nombre = models.TextField(max_length=30, verbose_name='Nombre')
    precio = models.FloatField(verbose_name='Precio')
    denominacionOrigen = models.ForeignKey(DenominacionOrigen, on_delete=models.SET_NULL,
                                           null=True,verbose_name='Denominacion de origen')
    tiposUvas = models.ManyToManyField(Uva)

    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ('nombre', )

