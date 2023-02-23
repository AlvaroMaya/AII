from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
import re

import os, ssl
if (not os.environ.get('PYTHONHHTPSVERIFY','') and 
    getattr(ssl, '_create_unverified_context',None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def almacenar_bd():
    conn = sqlite3.connect('juegos.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS JUEGOS") 
    # título, porcentaje de votos positivos, precio, temática/s y complejidad 
    conn.execute('''CREATE TABLE JUEGOS
       (TITULO           TEXT  NOT NULL,
        PORCT_VOTOS      INTEGER  NOT NULL,
        PRECIO  FLOAT  NOT NULL,
        TEMATICAS     TEXT NOT NULL,
        COMPLEJIDAD TEXT NOT NULL);''')
    
    print("Creada base de datos")
    url="https://zacatrus.es/juegos-de-mesa.html"
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
        votos = info.find("span",itemprop="ratingValue")
        if votos:
            votos = int (votos.string.strip())
        else:
            votos = 0
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
        # título, porcentaje de votos positivos, precio, temática/s y complejidad 
        conn.execute('''INSERT INTO JUEGOS (TITULO,PORCT_VOTOS,PRECIO,TEMATICAS, COMPLEJIDAD)
          VALUES(?,?,?,?,?)  ''',(titulo,votos,precio,tematica,complejidad))
        print(titulo,votos,precio,tematica,complejidad)
    conn.commit()
    conn.close
    print("fin")

def listar_juegos():
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    conn = sqlite3.connect('juegos.db')
    #conn.text_factory = str
    datos = conn.execute("SELECT * FROM JUEGOS ")
    for dato in datos:
        titulo = dato[0]
        votos = "Votos: "+str(dato[1])+" "
        lb.insert(END, titulo)
        lb.insert(END, "-----------------------------------------------------")
        precio = "Precio: "+str(dato[2])+" "
        tematica ="Tematica: "+ dato[3]+" "
        complejidad ="Complejidad: "+ dato[4]+" "
        texto = votos +precio +tematica +complejidad +"\n\n"
        lb.insert(END,texto)
        lb.pack(side=LEFT)


#"SELECT * FROM JUEGOS WERE VOTOS > 90 ORDER BY VOTOS DESC"
def listar_MejJuegos():
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    conn = sqlite3.connect('juegos.db')
    #conn.text_factory = str
    datos = conn.execute("SELECT * FROM JUEGOS WHERE PORCT_VOTOS > 90 ORDER BY PORCT_VOTOS DESC")
    for dato in datos:
        titulo = dato[0]
        votos = "Votos: "+str(dato[1])+" "
        lb.insert(END, titulo)
        lb.insert(END, "-----------------------------------------------------")
        precio = "Precio: "+str(dato[2])+" "
        tematica ="Tematica: "+ dato[3]+" "
        complejidad ="Complejidad: "+ dato[4]+" "
        texto = votos +precio +tematica +complejidad
        lb.insert(END,texto)
    lb.pack(side=LEFT)

def buscar_tematica():
    def juegos_por_tematica(event):
        w = Toplevel()
        pantalla = Text(w)
        tema = temitas.get()
        juegos = conn.execute('''SELECT TITULO, TEMATICAS, COMPLEJIDAD FROM JUEGOS WHERE TEMATICAS LIKE ?'''
                              ,(tema,)).fetchall()
        #print(juegos)
        for juego in juegos:
            texto = "Título: "+juego[0]+", Temáticas: "+juego[1]+", Complejidad: "+juego[2] +"\n\n"
            pantalla.insert(END,texto)
        pantalla.pack(side=LEFT)
        
    #creacion del spinbox
    conn=sqlite3.connect('juegos.db')
    tematicas = conn.execute("SELECT DISTINCT TEMATICAS FROM JUEGOS").fetchall()
    #lista_temas sera el value del spinbox
    lista_temas = list()
    for tema in tematicas:
        for tem in tema:
            tem= tem.split(",")
            for t in tem:
                if t not in lista_temas:
                    lista_temas.append(t)
                else:
                    pass
    #print(lista_temas)
    v = Toplevel()
    label = Label(v,text="Selecccione temática: ")
    label.pack(side=LEFT)
    temitas = Spinbox(v, value=lista_temas,wrap=True)
    temitas.bind("<Return>", juegos_por_tematica)
    temitas.pack(side=LEFT)
    
    

    

def buscar_complejidad():
    pass
    



def ventana_principal():
    raiz = Tk()
    raiz.title("Juegos de Mesa Zacatrus")
    menu = Menu(raiz)

    #DATOS
    menudatos = Menu(menu, tearoff=0)
    menudatos.add_command(label="Cargar", command=almacenar_bd)
    menudatos.add_command(label="Salir", command=raiz.quit)
    menu.add_cascade(label="Datos", menu=menudatos)

    #LISTAR
    menulistar = Menu(menu, tearoff=0)
    menulistar.add_command(label="Juegos", command=listar_juegos)
    menulistar.add_command(label="Mejores Juegos", command=listar_MejJuegos)
    menu.add_cascade(label="Listar", menu=menulistar)

    #BUSCAR
    menubuscar = Menu(menu, tearoff=0)
    menubuscar.add_command(label="Juegos por temática", command=buscar_tematica)
    menubuscar.add_command(label="Juegos por complejidad", command=buscar_complejidad)
    menu.add_cascade(label="Buscar", menu=menubuscar)

    raiz.config(menu=menu)

    raiz.mainloop()

if __name__ == "__main__":
    ventana_principal()