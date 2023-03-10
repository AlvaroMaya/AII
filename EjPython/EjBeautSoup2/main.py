from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime

#lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHHTPSVERIFY','') and 
    getattr(ssl, '_create_unverified_context',None)):
    ssl._create_default_https_context = ssl._create_unverified_context

#vamos a extraer cosas del html y lo obtenemos como una lista de objetos de BEATSOUP
    
def extraer_elementos():
    conn = sqlite3.connect('peliculas.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS PELICULAS")  
    conn.execute('''CREATE TABLE PELICULAS
       (TITULO           TEXT  NOT NULL,
        TITULO_ORIGINAL           TEXT  NOT NULL,
        PAISES           TEXT    NOT NULL,
        FECHA_EST_ES     DATE  NOT NULL ,
        DIRECTOR           TEXT   NOT NULL,
        GENEROS         TEXT   NOT NULL);''')
    
    print("Creada base de datos")
    
    print("Intentando acceder a la pagina")
    url = "https://www.elseptimoarte.net/estrenos/"
    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    print("Conseguida BS")
    link_peliculas = s.find("ul", class_="elements").find_all("li")
    #print(link_peliculas)
    for pelicula in link_peliculas:
       #print(pelicula)
       ref = pelicula.find("a").get("href")
       #print(ref)
       f = urllib.request.urlopen("https://www.elseptimoarte.net/"+ref)
       s = BeautifulSoup(f, "lxml")
       #comenzamos el almacenamiento de datos
       datos = s.find("main",class_=["informativo"])
       titulo = datos.find("dt",string="Título").find_next_sibling("dd").string.strip()
       titulo_or = datos.find("dt",string="Título original").find_next_sibling("dd").string.strip()
       paises= "".join(datos.find("dt",string="País").find_next_sibling("dd").stripped_strings)
       fecha_estreno = datetime.strptime(datos.find("dt",string="Estreno en España").find_next_sibling("dd").string.strip(), '%d/%m/%Y')
       director = s.find("p",class_=["director"]).span.a.span.string.strip()
       generos = "".join(s.find("p",class_=["categorias"]).stripped_strings)
       #print(director)
       conn.execute("""INSERT INTO PELICULAS 
       (TITULO, TITULO_ORIGINAL, PAISES, FECHA_EST_ES,DIRECTOR,GENEROS) VALUES (?,?,?,?,?,?) """,
       (titulo,titulo_or,paises,fecha_estreno, director,generos))
       #print("Comiteando cambio")
       conn.commit()
    print("Se termino la descarga")
   
    cursor = conn.execute("SELECT COUNT(*) FROM PELICULA")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def buscar_por_titulo():  
    def listar(event):
            conn = sqlite3.connect('peliculas.db')
            conn.text_factory = str
            cursor = conn.execute("SELECT TITULO, PAIS, DIRECTOR FROM PELICULA WHERE TITULO LIKE '%" + str(entry.get()) + "%'")
            conn.close
            listar_peliculas(cursor)
    ventana = Toplevel()
    label = Label(ventana, text="Introduzca cadena a buscar ")
    label.pack(side=LEFT)
    entry = Entry(ventana)
    entry.bind("<Return>", listar)
    entry.pack(side=LEFT)

def listar_peliculas(cursor):      
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'TÍTULO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     PAÍS: " + str(row[1]) + ' | DIRECTOR: ' + row[2]
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)


def listar_peliculas_1(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    for row in cursor:
        s = 'TÍTULO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "-----------------------------------------------------")
        fecha = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")  #sqlite almacena las fechas como str
        s = "     FECHA DE ESTRENO: " + datetime.strftime(fecha,"%d/%m/%Y")
        lb.insert(END, s)
        lb.insert(END, "\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def ventana_principal():
    top = Tk()
    top.title("Cartelera")
    #Con geometry vamos a tocar el tamaño de la ventana al abrirse
    #top.geometry("720x480")

    menubar = Menu(top)
    filemenu = Menu(menubar, tearoff = 0)
    filemenu.add_command(label="Cargar", command=extraer_elementos)#command = almacenar_bd
    filemenu.add_command(label = "Listar")#command = listar_bd

    filemenu.add_separator()

    filemenu.add_command(label = "Salir", command = top.quit)
    menubar.add_cascade(label = "Datos", menu = filemenu)
    
    buscarmenu = Menu(menubar, tearoff = 0)
    buscarmenu.add_command(label="Título")#command = almacenar_bd
    buscarmenu.add_command(label = "Fecha")#command = listar_bd
    buscarmenu.add_command(label = "Géneros")

    menubar.add_cascade(label = "Buscar", menu = buscarmenu)

    top.config(menu = menubar)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()