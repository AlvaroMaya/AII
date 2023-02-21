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
        conn.close

def ventana_principal():
    top = Tk()
    top.title("Jornada futbol")
    #Con geometry vamos a tocar el tamaño de la ventana al abrirse
    #top.geometry("720x480")

    resultados = Button(top, text="Almacenar resultados", command=almacenar_bd)
    resultados.pack(side=TOP)
    #resultados.place(x=0,y=100)
    jornadas=Button(top,text="Listar jornadas")
    jornadas.pack(side=TOP)
    buscar_jornada=Button(top,text="Buscar jornada")
    buscar_jornada.pack(side=TOP)
    estadisticas=Button(top,text="Estadisticas jornada")
    estadisticas.pack(side=TOP)
    top.mainloop()
    

if __name__ == "__main__":
    ventana_principal()