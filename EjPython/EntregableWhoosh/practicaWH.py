#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, NUMERIC, TEXT, DATETIME, KEYWORD, ID
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

# lineas para evitar error SSL
import ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="Esta seguro que quiere recargar los datos. Esta operación puede ser lenta")
    if respuesta:
        almacenar_datos()
  
 
def extraer_receta():
    #devuelve una lista de tuplas. Cada tupla tiene la información requerida de un elemento
    lista_x = []
        
    lista_pagina = extraer_url_recetas("https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html")
    lista_x.extend(lista_pagina)
        
    return lista_x 
    
#extrae todas los elementos que hay en una página y devuelve una lista    
def extraer_url_recetas(url):
    
    lista =[]
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    lista_link_recetas = s.find_all("div", class_="resultado link")
    for link in lista_link_recetas:
        texto =  link.a["href"]
  
        p = urllib.request.urlopen(texto)
        sp = BeautifulSoup(p, "lxml")        
        
        datos = sp.find("div",class_="nombre_autor")
        
        autor = datos.find("a",class_="ga").string.strip()
        fecha = datos.find("span",class_="date_publish").string.strip()
        if "Actualizado" in fecha:
            fecha = fecha.replace("Actualizado: ", "")
        
        meses={'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06','julio':'07','agosto':'08','septiembre':'09',
           'octubre':'10','noviembre':'11','diciembre':'12'}
        dia, mes, year = fecha.split()
        traduccion = meses[mes]
        
        fecha1 = dia +"/"+ traduccion +"/"+ year
        fecha = datetime.strptime(fecha1, '%d/%m/%Y')
        intro = sp.find("div", class_="intro")
        print(intro)
        
        introduccion = "".join(intro.stripped_strings)
        print(introduccion)        
        
        
        titulo = sp.find("h1", class_ ="titulo titulo--articulo").string.strip()
        
        receta_contenido = sp.find("div", class_ = "recipe-info")
        
        if "Receta" in titulo:
            receta_contenido = sp.find("div", class_ = "recipe-info")
        
            if receta_contenido.find("span", class_ = "property comensales"):
                comensales = receta_contenido.find("span", class_ = "property comensales").string.strip()[0]
                comensales = int(comensales)
            else:
                comensales = 0 
            
            
            if receta_contenido.find("div", class_ = "properties inline"):
                caracteristicas = receta_contenido.find("div", class_ = "properties inline").get_text()
                caracteristicas_ad = caracteristicas.replace("Características adicionales:", "")
            else:
                caracteristicas_ad = "No hay características adicionales" 
        
        
        
        else:
            comensales = 0 
            caracteristicas_ad = "No hay características adicionales" 
        
        print(titulo,comensales, autor, fecha, caracteristicas_ad, introduccion)
        
        
        #Lista para añadir los atributos            
        lista.append((titulo,comensales, autor, fecha, caracteristicas_ad, introduccion))
        
    return lista


#almacena cada pelicula en un documento de un Ã­ndice. Usa la funciÃ³n extraer_peliculas() para obtener la lista de peliculas 
def almacenar_datos():
    
    #define el esquema de la informacion
    receta_schema = Schema(
    titulo= TEXT (stored=True,phrase=True),
    numero_comensales= NUMERIC(stored=True, numtype=int),
    autor=ID (stored=True),
    fecha= DATETIME (stored=True),
    caracteristica = KEYWORD (stored=True,commas=True,lowercase=True),
    introduccion= TEXT(stored=True,phrase=True),
    )
     
    #eliminamos el directorio del índice, si existe
    if os.path.exists("Index"):
        shutil.rmtree("Index")
    os.mkdir("Index")
    
    #creamos el índice
    ix = create_in("Index", schema=receta_schema)
    #creamos un writer para poder añadir documentos al índice
    writer = ix.writer()
    i=0
    lista=extraer_receta()
    for receta in lista:
        #añade cada elemento de la lista al índice
        writer.add_document(titulo = str(receta[0]), 
                            numero_comensales =(receta[1]), 
                            autor =str(receta[2]),
                            fecha=(receta[3]), 
                            caracteristica=str(receta[4]),
                            introduccion=str(receta[5]) 
                            )    
        i+=1
    writer.commit()
    messagebox.showinfo("Fin de indexado", "Se han indexado "+str(i)+ " elementos")           

def buscar_titulo_introduccion():
    def titulo_introduccion():
        top = Tk()
        scrollbar = Scrollbar(top)
        scrollbar.pack(side=RIGHT, fill=Y)
        Lb = Listbox(top, width=100, yscrollcommand=scrollbar.set)
        
        # meter elementos
        ix = open_dir("Index")
        with ix.searcher() as searcher:
            query = MultifieldParser(["titulo","introduccion"], ix.schema, group=OrGroup).parse(E.get())
            results = searcher.search(query, limit=3) # limit= para coger los X resultados mas relevantes
            for result in results:
                #print(result)
                Lb.insert(END, result['titulo'])
                Lb.insert(END, result['introduccion'])
                Lb.insert(END, '')


        Lb.pack(side=LEFT, fill=BOTH)
        scrollbar.config( command = Lb.yview )
        top.mainloop()

    top = Tk()
    L = Label(top, text="Busqueda:")
    L.pack(side=LEFT)
    E = Entry(top)
    E.pack()
    B = Button(top, text="Buscar", command=titulo_introduccion)
    B.pack()

    top.mainloop()


def buscar_fecha():
    def fecha():
        top = Tk()
        scrollbar = Scrollbar(top)
        scrollbar.pack(side=RIGHT, fill=Y)
        Lb = Listbox(top, width=100, yscrollcommand=scrollbar.set)
        
        # meter elementos
        ix = open_dir("Index")
        with ix.searcher() as searcher:
            aux = E.get().split()
            rango_fecha = '['+ aux[0] + ' TO ' + aux[1] +']'
            query = QueryParser("fecha", ix.schema).parse(rango_fecha)
            results = searcher.search(query, limit=None) # limit= para coger los X resultados mas relevantes
            for result in results:
                Lb.insert(END, result['titulo'])
                Lb.insert(END, result['numero_comensales'])
                Lb.insert(END, result['autor'])
                Lb.insert(END, result['fecha'])
                Lb.insert(END, result['caracteristica'])
                Lb.insert(END, '')


        Lb.pack(side=LEFT, fill=BOTH)
        scrollbar.config( command = Lb.yview )
        top.mainloop()

    top = Tk()
    L = Label(top, text="Busqueda:")
    L.pack(side=LEFT)
    E = Entry(top)
    E.pack()
    B = Button(top, text="Buscar", command=fecha)
    B.pack()

    top.mainloop()

# permite buscar palabras en el "valor1" o en el "valor2" del elemento

#En el ejercicio 6 hay también de buscar fecha y modificarla, buscar género, etc.

def ventana_principal():
        
    root = Tk()
    menubar = Menu(root)
    
    datosmenu = Menu(menubar, tearoff=0)
    datosmenu.add_command(label="Cargar", command=cargar)
    datosmenu.add_separator()   
    datosmenu.add_command(label="Salir", command=root.quit)
    
    menubar.add_cascade(label="Datos", menu=datosmenu)
    
    buscarmenu = Menu(menubar, tearoff=0)
    buscarmenu.add_command(label="Título o Introducción", command=buscar_titulo_introduccion)
    buscarmenu.add_command(label="Fecha", command=buscar_fecha)
    buscarmenu.add_command(label="Características y Título")
    buscarmenu.add_command(label="Eliminar por título")
    
    menubar.add_cascade(label="Buscar", menu=buscarmenu)
        
    root.config(menu=menubar)
    root.mainloop()


    

if __name__ == "__main__":
    ventana_principal()