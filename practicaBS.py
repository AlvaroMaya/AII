'''
Created on 2 mar 2023

@author: javia
'''

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime


import os, ssl
if(not os.environ.get('PYTHONHTTPSVERIFY', '') and 
   getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    respuesta = messagebox.askyesno(title="Confirmar",message="¿Está seguro que quiere recargar los datos? Esta operación puede ser lenta")
    if respuesta:
        almacenar_bd()
 

def almacenar_bd():
    conn = sqlite3.connect('recetas.db')
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS RECETAS")
    conn.execute(''' CREATE TABLE RECETAS
        (TITULO     TEXT     NOT NULL,
         DIFICULTAD TEXT,
         COMENSALES INTEGER,
         TIEMPO_PRE    TEXT,
         AUTOR    TEXT,
         FECHA    TEXT);''')

    
    
    url = "https://www.recetasgratis.net/Recetas-de-Aperitivos-tapas-listado_receta-1_1.html"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    lista_link_recetas = s.find_all("div", class_="resultado link")
    for link in lista_link_recetas:
        texto =  link.a["href"]
        #print(texto)
        p = urllib.request.urlopen(texto)
        sp = BeautifulSoup(p, "lxml")  
        datos = sp.find("div",class_="nombre_autor")
        autor = datos.find("a",class_="ga").string.strip()
        fecha = datos.find("span",class_="date_publish").string.strip()
        if "Actualizado" in fecha:
            fecha = fecha.replace("Actualizado: ", "")
        titulo = sp.find("h1", class_ ="titulo titulo--articulo").string.strip()
       
        if "Receta" in titulo:
            receta_contenido = sp.find("div", class_ = "recipe-info")
         
            if receta_contenido.find("span", class_ = "property comensales"):
                comensales =  (receta_contenido.find("span", class_ = "property comensales").string.strip())
                comensales =  int(comensales[0])
                
            else:
                comensales = -1 
            
            if receta_contenido.find("span", class_ = "property duracion"):
                tiempo_pre = receta_contenido.find("span", class_ = "property duracion").string.strip()
            else:
                tiempo_pre = "0" 
        
            if receta_contenido.find("span", class_ = "property dificultad"):
                dificultad = receta_contenido.find("span", class_ = "property dificultad").string.strip()
            else:
                dificultad = "Sin dificultad"
        
        else:
            comensales = -1 
            tiempo_pre = "0"
            dificultad = "Sin dificultad"
        
        print(titulo, dificultad ,comensales, tiempo_pre, autor, fecha)
        
        conn.execute("""INSERT INTO RECETAS (TITULO, DIFICULTAD, COMENSALES, TIEMPO_PRE, AUTOR, FECHA) VALUES (?,?,?,?,?,?)""",
            (titulo, dificultad, comensales, tiempo_pre, autor, fecha))
        conn.commit()
    conn.close()
        

    
    
def listar_recetas():

    conn = sqlite3.connect('recetas.db')
    print ("Abrir base de datos")

    cursor = conn.execute("SELECT TITULO, DIFICULTAD, COMENSALES, TIEMPO_PRE FROM RECETAS")
    print(cursor)

#MOSTRAR LA VENTANA  CON UNA LISTBOX Y CON SCROLLBAR 

    top = Toplevel()

    scrollbar = Scrollbar(top)
    scrollbar.pack( side = RIGHT, fill = Y )

    mylist = Listbox(top, yscrollcommand = scrollbar.set, width = 100 )
    for fila in cursor:
        mylist.insert(END, str(fila))

    mylist.pack( side = LEFT, fill = BOTH )
    scrollbar.config( command = mylist.yview )

    mainloop()
    conn.close()

def buscar_autor():
    def recetas_por_autor(event):
        w = Toplevel()
        sc = Scrollbar(w)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width=150, yscrollcommand=sc.set)
        pantalla = Text(w)
        autor = compl.get()
        autor = autor[1:-1]
        print(autor)
        
        recetas = conn.execute('''SELECT TITULO, DIFICULTAD, COMENSALES,TIEMPO_PRE,AUTOR FROM RECETAS 
        WHERE AUTOR LIKE ?'''
                              ,(autor,)).fetchall()
        #print(juegos)
        for receta in recetas:
            pantalla.insert(END, "Título: "+receta[0])
            pantalla.insert(END, "\n------------------------------------------------------------------------\n")
            texto =  "Dificultad: "+receta[1]+", COMENSALES: "+str(receta[2]) +" Tiempo preparacion: "+receta[3]+" Autor: "+receta[4] +"\n\n"
            pantalla.insert(END,texto)
            
        pantalla.pack(side=LEFT)
        
    #creacion del spinbox
    conn=sqlite3.connect('recetas.db')
    autores = conn.execute("SELECT DISTINCT AUTOR FROM RECETAS").fetchall()
    #lista_temas sera el value del spinbox
    
    lista_autores = list()
    for autor in autores:
        if autor not in lista_autores:
            lista_autores.append(autor)
        else:
            pass
    
    #print(lista_temas)
    v = Toplevel()
    
    label = Label(v,text="Selecccione autor: ")
    label.pack(side=LEFT)
    compl = Spinbox(v, value=lista_autores,wrap=True)
    compl.bind("<Return>", recetas_por_autor)
    compl.pack(side=LEFT)

def buscar_fecha():
    def recetas_por_fecha(event):
        
        
        w = Toplevel()
        sc = Scrollbar(w)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width=150, yscrollcommand=sc.set)
        pantalla = Text(w)
        fecha = E1.get()
        print(fecha)
        meses={'enero':'01','febrero':'02','marzo':'03','abril':'04','mayo':'05','junio':'06','julio':'07','agosto':'08','septiembre':'09',
           'octubre':'10','noviembre':'11','diciembre':'12'}
        #fecha = re.match(r'.*(\d\d)\s*(.{3})\s*(\d{4}).*', s)
        mes = fecha[3:5]
        traduccion = meses.values(mes)
        dia= fecha[0:2]
        year = fecha[7:]
        fecha1 = dia + traduccion + year
        print(fecha1)
        print(mes)
        #l = list(fecha.groups())
        #l[1] = meses[l[1]]
        pantalla.insert(END,fecha)
        
            
        pantalla.pack(side=LEFT)

    v = Toplevel()

    L1 = Label(v, text = "Introducir fecha en formato dd/mm/yyyy")
    L1.pack( side = LEFT)
    E1 = Entry(v, bd = 5)
    E1.bind("<Return>", recetas_por_fecha)
    E1.pack(side = RIGHT)
    


#VENTANA PRINCIPAL CON 3 BOTONES
def ventana_principal():

    root = Tk()
    menubar = Menu(root)

    # BOTON DATOS
    datamenu = Menu(menubar, tearoff = 0)
    datamenu.add_command(label="Cargar",command=cargar)
    datamenu.add_command(label = "Salir", command = root.quit)
    menubar.add_cascade(label = "Datos", menu = datamenu)

    #BOTON LISTAR
    listarmenu = Menu(menubar, tearoff = 0)
    listarmenu.add_command(label = "Recetas",command=listar_recetas)
    menubar.add_cascade(label = "Listar", menu = listarmenu)

    #BOTON BUSCAR
    buscarmenu = Menu(menubar, tearoff = 0)
    buscarmenu.add_command(label = "Recetas por autor", command=buscar_autor)
    buscarmenu.add_command(label = "Recetas por fecha", command=buscar_fecha)
    menubar.add_cascade(label = "Buscar", menu = buscarmenu)


    root.config(menu = menubar)
    root.mainloop()

if __name__ == "__main__":
    ventana_principal()