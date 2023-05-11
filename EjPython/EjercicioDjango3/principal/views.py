from django.shortcuts import render

# Create your views here.

from principal.models import Genero, Pelicula
#from principal.forms import BusquedaPorFechaForm, BusquedaPorGeneroForm
from principal.populateDB import populateDB
from django.shortcuts import render, redirect

def carga(request):
 
    if request.method=='POST':
        if 'Aceptar' in request.POST:      
            num_peliculas, num_directores, num_generos, num_paises = populateDB()
            mensaje="Se han almacenado: " + str(num_peliculas) +" peliculas, " + str(num_directores) +" directores, " + str(num_generos) +" generos, " + str(num_paises) +" paises"
            return render(request, 'cargaBD.html', {'mensaje':mensaje})
        else:
            return redirect("/")
           
    return render(request, 'confirmacion.html')
