import os
from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
#importar antes el tkinter que el whoosh
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID, STORED
from whoosh.qparser import QueryParser
from whoosh import query
from tkinter import *
from tkinter import messagebox

juegos={}
#ahora usamos una url como metodo de consulta
url="https://zacatrus.es/juegos-de-mesa.html"
dirindex="Index"


def crea_index():
    def carga():
        sch = Schema(titulo=TEXT(stored=True,phrase=False), precio=NUMERIC(stored=True,numtype=float),
                      tematica=KEYWORD(stored=True,commas=True,lowercase=True),
                      complejidad=ID(stored=True), num_jug=KEYWORD(stored=True,commas=True),
                      detalles=TEXT(stored=True,phrase=False))
        ix = create_in(dirindex, schema=sch)
        lista_juegos=extraer_juegos()
        writer = ix.writer()
        for docname in os.listdir(dirdocs):
            if not os.path.isdir(dirdocs+docname):
                add_doc(writer, dirdocs, docname)                  
        writer.commit()
        messagebox.showinfo("INDICE CREADO", "Se han cargado " + str(ix.reader().doc_count()) + " documentos")
     
    if not os.path.exists(dirdocs):
        messagebox.showerror("ERROR", "No existe el directorio de documentos " + dirdocs)
    else:
        if not os.path.exists(dirindex):
            os.mkdir(dirindex)
    if not len(os.listdir(dirindex))==0:
        respuesta = messagebox.askyesno("Confirmar","Indice no vacío. Desea reindexar?") 
        if respuesta:
            carga()           
    else:
        carga()


def extraer_juegos():
    lista=[]
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    print("Conseguida BS")
    lista = s.find("ol",class_=["products","list","items", "product-items"])
    lista_productos = lista.find_all("li")
    for producto in lista_productos:
        link = producto.find("a").get("href")
        f = urllib.request.urlopen(link)
        s = BeautifulSoup(f, "lxml")
        titulo = s.find("span",class_="base").string.strip()
        info = s.find("div",class_="product-info-price")
        precio = info.find("meta", itemprop="price").get("content")
        tematica = s.find("div",attrs={"data-th":"Temática"})
        if tematica:
            tematica ="".join(s.find("div",attrs={"data-th":"Temática"}).stripped_strings)
        else:
            tematica = "Ninguna"
        complejidad = s.find("div",attrs={"data-th":"Complejidad"})
        if complejidad:
            complejidad = complejidad.string.strip()
        else:
            complejidad = "Variable"
        num_jug=s.find("div",attrs={"data-th":"Núm. jugadores"})
        if num_jug:
            num_jug=list(num_jug.stripped_strings)
        else:
            num_jug="No especificado"
        details = s.find("div",class_="product attribute description")
        if details:
            detalles=details.find("div",class_="value").get_text() #equivale a hacer stripped_strings y unirlo con un join
        else:
            detalles="No hay detalles en la pagina"
        
        print(num_jug,detalles)
        #insertar en la lista
        #lista.append(titulo,precio,tematica,complejidad,num_jug,detalles)
        # título, porcentaje de votos positivos, precio, temática/s y complejidad 
    #devolvemos la lista
    return lista


def ventana_principal():
    def listar_todo():
        ix=open_dir(dirindex)
        with ix.searcher() as searcher:
            results = searcher.search(query.Every())
            listar(results) 
    
    raiz = Tk()

    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=extraer_juegos)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Detalles", command="")
    menubuscar.add_command(label="Temáticas", command="")
    menubuscar.add_command(label="Precio", command="")
    menubuscar.add_command(label="Jugadores", command="")

    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()


if __name__ == "__main__":
    ventana_principal()