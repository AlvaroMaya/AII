from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml

#lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHHTPSVERIFY','') and 
    getattr(ssl, '_create_unverified_context',None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#funcion de confirmacion para almacenar
def cargar(): 
    respuesta=messagebox.askyesno(title = "Confirmar", message="Está seguro de querer cargar los datos")
    if respuesta:
        almacenar_bd()

def extraer_elementos():
    lista=[]
    
    for num_paginas in range(0,3):
        url = "https://www.vinissimus.com/es/vinos/tinto/index.html?cursor="+str(num_paginas*36)
        f = urllib.request.urlopen(url)
        s = BeautifulSoup(f, "lxml")
        lista_una_pagina = s.find_all("div", class_="product-list-item")
        lista.extend(lista_una_pagina)
   
    return lista

def almacenar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS VINOS")   
    conn.execute('''CREATE TABLE VINOS
       (NOMBRE           TEXT PRIMARY KEY  NOT NULL,
       PRECIO           INT    NOT NULL,
       DENOMINACION     TEXT   NOT NULL,
       BODEGA           TEXT   NOT NULL,
       TIPO_UVA         TEXT   NOT NULL);''')
    respuesta=messagebox.showinfo(title = "INFO", message="Se cargaron los datos")
    print("Base de datos creada")

def listar_bd():
    lista=[]
#def salir():

#def buscar_bd():

#def denominacion_bd():

#def precio_bd():

#dev uvas_bd():
        


#fundamento del tkinter e inicio de todo
def ventana_principal():
    top = Tk()
    top.title("Carta de vinos")
    #Con geometry vamos a tocar el tamaño de la ventana al abrirse
    #top.geometry("720x480")

    menubar = Menu(top)
    filemenu = Menu(menubar, tearoff = 0)
    filemenu.add_command(label="Cargar", command=almacenar_bd)#command = almacenar_bd
    filemenu.add_command(label = "Listar")#command = listar_bd

    filemenu.add_separator()

    filemenu.add_command(label = "Salir", command = top.quit)
    menubar.add_cascade(label = "Datos", menu = filemenu)
    
    buscarmenu = Menu(menubar, tearoff = 0)
    buscarmenu.add_command(label="Denominacion")#command = almacenar_bd
    buscarmenu.add_command(label = "Precio")#command = listar_bd
    buscarmenu.add_command(label = "Uvas")

    menubar.add_cascade(label = "Buscar", menu = buscarmenu)

    top.config(menu = menubar)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()