from django.db import models
class Categoria(models.Model):
    idCategoria = models.IntegerField(primary_key=True)
    nombre = models.TextField(verbose_name='Nombre')
    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ('nombre',)

class Ocupacion(models.Model):
    nombre = models.TextField(verbose_name='Ocupacion')

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ('nombre', )


class Usuario(models.Model):
    idUsuario = models.IntegerField(primary_key=True)
    edad = models.PositiveSmallIntegerField(verbose_name='Edad', help_text='Default', unique=True)
    sexo = models.CharField(verbose_name='Sexo', help_text='Default', max_length=1)
    ocupacion = models.ForeignKey(Ocupacion, on_delete=models.CASCADE)
    codigoPostal = models.IntegerField( verbose_name='Código Postal')


    def __str__(self):
        return self.ocupacion

    class Meta:
        ordering = ('ocupacion', )

class Pelicula(models.Model):
    idPelicula = models.IntegerField(primary_key=True)
    titulo = models.TextField(verbose_name='Titulo')
    fechaEstreno = models.DateField(verbose_name='Fecha de Estreno', null=True)
    imdbUrl = models.URLField(verbose_name='URL en IMDB')
    categorias = models.ManyToManyField(Categoria)
    puntuaciones = models.ManyToManyField(Usuario, through='Puntuacion')
    
    def __str__(self):
        return self.titulo
    
    class Meta:
        ordering = ('titulo', 'fechaEstreno')
        
        
class Puntuacion(models.Model):
    PUNTUACIONES = ((1,'Muy mala'), (2,'Mala'),(3,'Regular'), (4,'Buena'), (5,'Muy buena'))
    idUsuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    idPelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    puntuacion = models.PositiveSmallIntegerField(verbose_name='Puntuacion', help_text='Default')

    def __str__(self):
        return (str(self.puntuacion))   

    class Meta:
        ordering = ('idPelicula', 'idUsuario',) 
