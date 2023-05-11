#encoding:utf-8
from main.models import Categoria, Ocupacion, Usuario, Pelicula
from datetime import datetime

path = "datos"

def populateOcupacion():
    Ocupacion.objects.all().delete()
    
    ocupacion=[]
    fileobj=open(path+"\\u.occupation", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        ocupacion.append(Ocupacion(nombre=str(rip[0].strip())))
    fileobj.close()
    Ocupacion.objects.bulk_create(ocupacion)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return len(ocupacion)

def populateUser():
    Usuario.objects.all().delete()

    users = []
    fileobj=open(path+"\\u.user","r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        users.append(Users(idUsuario=int(rip[0].strip()),edad=int(rip[1].strip()) ,sexo=str(rip[2].strip()),
                           ocupacion = Ocupacion.objects.get(nombre=str(rip[3].strip())),
                           codigoPostal=int(rip[4].strip())))
    fileobj.close()
    Users.objects.bulk_create(users)
    return len(users)

def populateCategoria():
    Categoria.objects.all().delete()

    categorias = []
    fileobj=open(path+"\\u.genre","r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        categorias.append(Categoria(idCategoria =(int(rip[1].strip())), nombre=str(rip[0].strip())))
    Categoria.objects.bulk_create(categorias)
    return len(categorias)


def populatePelicula():
    Pelicula.objects.all().delete()

    peliculas = []
    
    dic = {}
    fileobj=open(path+"\\u.item","r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        fecha = None if rip[2] == ' ' else datetime.strptime(rip[2], "%d %B, %Y")
        peliculas.append(Pelicula(idPelicula=int(rip[0].strip()), título = str(rip[1].strip()),
        fechaEstreno = fecha, imdbUrl= str(rip[3])))
        p = Pelicula.object.create(idPelicula=int(rip[0].strip()), título = str(rip[1].strip()),
        fechaEstreno = fecha, imdbUrl= str(rip[3]))
        ##las categorias
        categorias = []
        for i in range(5,len(rip)):
            categorias = categorias.append(Categorias.objects.get(idCategoria = i-5))
        p.Categoria.set(categorias)
    
    fileobj.close()
        #dic[rip[0]] = categorias
    #Pelicula.objects.bulk_create(peliculas)
    #for pelic in

def populate():
    o = populateOcupacion()
    u = populateUser()
    c = populateCategoria()
    p = populatePelicula()
    return (o,u,c,p)