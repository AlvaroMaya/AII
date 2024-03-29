from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
import re


#lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHHTPSVERIFY','') and 
    getattr(ssl, '_create_unverified_context',None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def almacenar_bd():
    conn = sqlite3.connect('futbol.db')
    conn.text_factory = str  # para evitar problemas con el conjunto de caracteres que maneja la BD
    conn.execute("DROP TABLE IF EXISTS FUTBOL")  
    conn.execute('''CREATE TABLE FUTBOL
       (JORNADA           TEXT  NOT NULL,
        EQUIPO_LOCAL      TEXT  NOT NULL,
        EQUIPO_VISITANTE  TEXT  NOT NULL,
        RESULTADO_LOCAL     INTEGER NOT NULL,
        RESULTADO_VISITANTE INTEGER NOT NULL,
        LINK_DIRECTO      TEXT NOT NULL);''')
    
    print("Creada base de datos")
    
    print("Intentando acceder a la pagina")
    url = "http://resultados.as.com/resultados/futbol/primera/2021_2022/calendario/"

    f = urllib.request.urlopen(url)
    s = BeautifulSoup(f, "lxml")
    print("Conseguida BS")
    lista_jornadas=s.find_all("div",class_=["cont-modulo","resultados"])
    for j in lista_jornadas:
        #print(j)
        jornada = j.find("a").get("title")
        #print(jornada)
        #buscamos dentro de cada elemento de la tabla, por tanto necesitamos otro bucle for
        lista_partidos = j.find("tbody").find_all("tr")
        for i in lista_partidos:
            equipo_local = i.find("td",class_="col-equipo-local").find("span").string.strip()
            equipo_visitante = i.find("td",class_="col-equipo-visitante").find("span",class_="nombre-equipo").string.strip()
            resultado = i.find("td",class_="col-resultado").find("a").string.strip()
            res_global = re.compile('(\d+).*(\d+)').search(resultado)
            res_local = res_global.group(1)
            res_visitante = int (resultado.split("-")[1]) 
            link = i.find("td",class_="col-resultado").find("a").get("href")
            #print(equipo_local,resultado,equipo_visitante)
            #print(res_local,res_visitante)
            #print(link)
            conn.execute("""INSERT INTO FUTBOL 
            (JORNADA, EQUIPO_LOCAL, EQUIPO_VISITANTE, RESULTADO_LOCAL,RESULTADO_VISITANTE,LINK_DIRECTO) VALUES (?,?,?,?,?,?) """,
            (jornada,equipo_local,equipo_visitante,res_local, res_visitante,link))
            print("Comiteando cambio")
            conn.commit()
        cursor = conn.execute("SELECT COUNT(*) FROM FUTBOL")
        messagebox.showinfo("Base Datos",
                            "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
        conn.close()

#“Listar Jornadas”, que muestre en otra ventana (en una listbox con scrollbar) los
#resultados de los partidos de todas las jornadas, extrayéndolos de la BD.
def listar_jornadas():
    #creacion de la ventana
    v = Toplevel()
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    #parte de la base de datos
    conn=sqlite3.connect('futbol.db')
    conn.text_factory = str
    jornadas = conn.execute("SELECT DISTINCT JORNADA FROM FUTBOL")
    for row in jornadas: #en row[0] tenemos el nombre de nuestras jornadas
        #print(row[0])
        jornada = row[0]
        #agregamos la jornada a nuestro texto
        lb.insert(END, jornada)
        lb.insert(END, "-----------------------------------------------------")
        #sacamos el numerito del texto para llamar a la funcion
        s = jornada[8:]
        lista_res=extraer_jornada(s)
        for res in lista_res:
            lb.insert(END,res)
        #insertamos un salto de linea al final del ultimo resultado, para una mejor lectura
        lb.insert(END, "\n\n")
       # lista_de_jornadas(cursor,jornada)
    conn.close
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

def buscar_jornada():
    def imprimir_jornada():
        s = numeritos.get()
        #me voy a extraer jornada porque alli hago toda la extraccion de datos
        lista_res=extraer_jornada(s)
        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width=150, yscrollcommand=sc.set)
        lb.insert(END, "Jornada "+s)
        lb.insert(END, "-----------------------------------------------------")
        for res in lista_res:
            lb.insert(END,res)
        lb.pack(side=LEFT,fill=BOTH)
        sc.config(command=lb.yview)
    conn=sqlite3.connect('futbol.db')
    conn.text_factory = str
    partidos = conn.execute("SELECT DISTINCT JORNADA FROM FUTBOL")
    jornadas = partidos.fetchall()
    conn.close
    #hay que hacer 2 ventanas nuevas, para el entry y otra para el texto de resultado
    v = Toplevel()
    label = Label(v,text="Introduzca numero de la jornada: ")
    label.pack(side=LEFT)
    x = str
    var=StringVar()
    numeritos = Spinbox(v,textvariable=var, from_= 1 , to =len(jornadas), command=imprimir_jornada,wrap=True)
    var.set(0)
    numeritos.pack(side=LEFT)


def estadistica_jornada():
    def imprimir_jornada():
        s = numeritos.get()
        #me voy a extraer jornada porque alli hago toda la extraccion de datos
        stats=estadisticas(s)
        #print(stats)
        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Text(v, width=150, yscrollcommand=sc.set)
        lb.insert(END, "Jornada "+s)
        lb.insert(END, "\n-----------------------------------------------------")
        lb.insert(END,stats)
        lb.pack(side=LEFT,fill=BOTH)
        sc.config(command=lb.yview)
    conn=sqlite3.connect('futbol.db')
    conn.text_factory = str
    partidos = conn.execute("SELECT DISTINCT JORNADA FROM FUTBOL")
    jornadas = partidos.fetchall()
    conn.close
    #hay que hacer 2 ventanas nuevas, para el entry y otra para el texto de resultado
    v = Toplevel()
    label = Label(v,text="Introduzca numero de la jornada: ")
    label.pack(side=LEFT)
    x = str
    var=StringVar()
    numeritos = Spinbox(v,textvariable=var, from_= 1 , to =len(jornadas),wrap=True)
    numeritos.bind("<Return>", imprimir_jornada)
    var.set(0)
    numeritos.pack(side=LEFT)

#buscamos los links con cada url necesaria para sacar los datos
def buscar_goles():
    def sacar_equipos():
        num_jornada=jornada.get()
        str_jornada = "Jornada "+num_jornada
        #print(str_jornada)
        local = conn.execute("SELECT EQUIPO_LOCAL FROM FUTBOL WHERE JORNADA LIKE ?",(str_jornada,))
        loc=local.fetchall()
        #print(loc)
        visitante = conn.execute("SELECT EQUIPO_VISITANTE FROM FUTBOL WHERE JORNADA LIKE ?",(str_jornada,))
        vis=visitante.fetchall()
        equipo_loc.config(value=loc)
        equipo_vis.config(value=vis)
    def imprime_goles():
        num_jornada=jornada.get()
        str_jornada = "Jornada "+num_jornada
        equipo_local = equipo_loc.get()
        equipo_visitante = equipo_vis.get()
        #extraemos el link
        link =  conn.execute('''SELECT LINK_DIRECTO FROM FUTBOL WHERE JORNADA LIKE ? 
        AND EQUIPO_LOCAL LIKE ? AND EQUIPO_VISITANTE LIKE ?''',(str_jornada,equipo_local,equipo_visitante))
        url = link.fetchone()
        
        if url:
            #print(url[0])
            detalles_goles(url)
        else:
            print("Te equivocaste wey")
            messagebox.showwarning("Warning","Estos dos equipos no se enfrentaron en la jornada seleccionada")

    conn=sqlite3.connect('futbol.db')
    conn.text_factory = str
    partidos = conn.execute("SELECT DISTINCT JORNADA FROM FUTBOL")
    jornadas = partidos.fetchall()
    
    v = Toplevel()
    label = Label(v,text="Selecccione jornada: ")
    label.pack(side=LEFT)
    x = str
    var=StringVar()
    jornada= Spinbox(v,textvariable=var, from_= 1 , to =len(jornadas),command=sacar_equipos, wrap=True)
    var.set(0)
    jornada.pack(side=LEFT)
    equipo_loc = Spinbox(v, value=[],wrap=True)
    label1 = Label(v,text="Selecccione equipo local: ")
    label1.pack(side=LEFT)
    equipo_loc.pack(side=LEFT)
    equipo_vis = Spinbox(v,value=[],wrap=True)
    label2 = Label(v,text="Selecccione equipo visitante: ")
    label2.pack(side=LEFT)
    equipo_vis.pack(side=LEFT)
    button = Button(v,text="Buscar goles",command=imprime_goles)
    button.pack(side=LEFT, padx= 10)

def detalles_goles(url):
    v = Toplevel()
    msg = Text(v)
    #print(url[0])
    f = urllib.request.urlopen(url[0])
    s = BeautifulSoup(f, "lxml")
    #lista_jornadas=s.find_all("div",class_=["cont-modulo","resultados"])
    #buscar en section->class=is-postgame
    #para los locales:
    seccion=s.find("section",class_=["is-postgame"])
    #print(seccion)
    datos_local = seccion.find("div",class_=["is-local"])
    datos_visit = seccion.find("div",class_=["is-visitor"])
    nombre_local=datos_local.find("span",class_=["name-large"]).string.strip()
    nombre_visit=datos_visit.find("span",class_=["name-large"]).string.strip()
    scorers_local = datos_local.find("div",class_=["scr-hdr__scorers"])
    spans_loc= scorers_local.find_all("span")
    texto=str 
    for span in spans_loc:
        if span.get("class"):
            pass
        else:
            x = span.string.strip()
            texto=nombre_local+": " +x+"\n"
            msg.insert(END, texto)

            print(x)
    scorers_vis = datos_visit.find("div",class_=["scr-hdr__scorers"])
    spans_vis= scorers_vis.find_all("span")
    texto=str 
    for span in spans_vis:
        if span.get("class"):
            pass
        else:
            x = span.string.strip()
            texto=nombre_visit+": " +x+"\n"
            msg.insert(END, texto)
            print(x)
    msg.pack()
    #print(spans)

def extraer_jornada(jornada):
    jornada_ext = "Jornada "+jornada
    print(jornada_ext)
    conn = sqlite3.connect('futbol.db')
    cursor = conn.execute('''SELECT EQUIPO_LOCAL,EQUIPO_VISITANTE,RESULTADO_LOCAL, RESULTADO_VISITANTE
                               FROM FUTBOL WHERE JORNADA LIKE ?''', (jornada_ext,))
    lista_res = list()
    for fila in cursor:
        equipo_local = fila[0]
        equipo_vis   = fila[1]
        res_local    = fila[2]
        res_vis      = fila[3] 
            #el cast de str es necesario para pasar los numeros a string y meterlo en el texto
        texto = str(equipo_local + " " +str(res_local) +"-"+str(res_vis) +" " +equipo_vis)
        lista_res.append(texto)
    conn.close
    #devuelvo la lista con el texto
    return lista_res

def estadisticas(jornada):
    jornada_ext = "Jornada "+jornada
    print(jornada_ext)
    conn = sqlite3.connect('futbol.db')
    cursor = conn.execute('''SELECT RESULTADO_LOCAL, RESULTADO_VISITANTE
                               FROM FUTBOL WHERE JORNADA LIKE ?''', (jornada_ext,))
    tot_goles=0
    empate=0
    vic_local=0
    vic_vis=0
    for fila in cursor:
        res_local=int(fila[0])
        res_vis  =int(fila[1])
        tot_goles+=res_local+res_vis
        if res_vis == res_local:
            empate+=1
        elif res_local>res_vis:
            vic_local +=1
        else:
            vic_vis+=1
    texto = "\n\tTOTAL GOLES JORNADA: "+str(tot_goles)+"\n\n\t Empates: "+str(empate)+"\n\t Victoria local: "+str(vic_local)+"\n\t Victoria visitante: "+str(vic_vis)
    return texto


def ventana_principal():
    top = Tk()
    top.title("Jornada futbol")
    #Con geometry vamos a tocar el tamaño de la ventana al abrirse
    #top.geometry("720x480")

    resultados = Button(top, text="Almacenar resultados", command=almacenar_bd)
    resultados.pack(side=TOP)
    #resultados.place(x=0,y=100)
    jornadas=Button(top,text="Listar jornadas",command=listar_jornadas)
    jornadas.pack(side=TOP)
    buscar_jorn=Button(top,text="Buscar jornada",command=buscar_jornada)
    buscar_jorn.pack(side=TOP)
    estadisticas=Button(top,text="Estadisticas jornada",command=estadistica_jornada)
    estadisticas.pack(side=TOP)
    goles=Button(top,text="Buscar goles", command=buscar_goles)
    goles.pack(side=TOP)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()