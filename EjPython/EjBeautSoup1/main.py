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

#vamos a extraer cosas del html y lo obtenemos como una lista de objetos de BEATSOUP
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
    conn.execute("DROP TABLE IF EXISTS TIPOS_UVAS") 
    conn.execute('''CREATE TABLE VINOS
       (NOMBRE           TEXT PRIMARY KEY  NOT NULL,
       PRECIO           INT    NOT NULL,
       DENOMINACION     TEXT   NOT NULL,
       BODEGA           TEXT   NOT NULL,
       TIPO_UVA         TEXT   NOT NULL);''')
    
    conn.execute(''' CREATE TABLE TIPOS_UVAS
       (NOMBRE           TEXT   NOT NULL);''')
    
    #toca ahora meter los vinos dentro de la base de datos
    #consigamos primero los vinos de la pagina
    #recordemos que lista_vinos es ahora una lista de obj de beatsoup
    lista_vinos=extraer_elementos()
    #un set para los tipos de uva que usaremos mas tarde
    tipos_uva=set()
    for vino in lista_vinos:
        datos = vino.find("div",class_=["details"])
        nombre = datos.a.h2.string.strip()
        bodega = datos.find("div",class_=["cellar-name"]).string.strip()
        denominacion  = datos.find("div",class_=["region"]).string.strip()
        uvas = "".join(datos.find("div",class_=["tags"]).stripped_strings)
        for uva in uvas.split("/"):
            tipos_uva.add(uva.strip())
        
        #Los precios estan compuestos por dos elementos, el numerito y el simbolo del euro
        #por tanto, lo metemos todo en la lista siendo [numero, simbolo]
        #y nos quedamos con el numero aka elemento 0
        precio = list(vino.find("p",class_=["price"]).stripped_strings)[0]
        dto = vino.find("p",class_=["price"]).find_next_sibling("p",class_="dto")
        if dto:
            precio = list(dto.stripped_strings)[0]
        
        #enviamos el objeto a la base de datos
        conn.execute("""INSERT INTO VINOS (NOMBRE,PRECIO, DENOMINACION, BODEGA,TIPO_UVA) 
        VALUES (?,?,?,?,?) """,
        (nombre,float(precio.replace(',' , '.')), denominacion,bodega,uvas))
    #guardamos todos los cambios realizados
    conn.commit()
    
    for u in list(tipos_uva):
        #print(type(u))
        conn.execute("""INSERT INTO TIPOS_UVAS (NOMBRE) VALUES (?)""",                   (u,))
    
    conn.commit()
    #procedemos ahora a realizar la ventana emergente que se debe mostrar
    cursor = conn.execute("SELECT COUNT(*) FROM VINOS")
    cursor1 = conn.execute("SELECT COUNT(*) FROM TIPOS_UVAS")
    respuesta=messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " vinos y "
                        + str(cursor1.fetchone()) + " tipos de uvas")

    conn.close()

#extraemos los datos de la bd 
def listar_bd():
    conn = sqlite3.connect('vinos.db')
    conn.text_factory = str
    cursor = conn.execute("SELECT NOMBRE,PRECIO,BODEGA,DENOMINACION FROM VINOS")
    #no se porque no añade aqui el parentesis
    conn.close
    #en listar vinos creamos la ventana y todo lo relacionado con tkinter
    listar_vinos(cursor)

def listar_vinos(cursor):
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT,fill=Y)
    lb = Listbox(v,width=150,yscrollcommand=sc.set)
    for row in cursor:
        s = 'VINO: ' + row[0]
        lb.insert(END, s)
        lb.insert(END, "------------------------------------------------------------------------")
        s = "     PRECIO: " + str(row[1]) + ' | BODEGA: ' + row[2]+ ' | DENOMINACION: ' + row[3]
        lb.insert(END, s)
        lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)



def denominacion_bd():

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
    filemenu.add_command(label = "Listar", command=listar_bd)#command = listar_bd

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