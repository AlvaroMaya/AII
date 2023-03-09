# -*- coding: utf-8 -*-
from tkinter import *
import os
import re
from tkinter import messagebox

from whoosh.fields import *
from whoosh.index import create_in

import whoosh.index as index


class FicherosSchema(SchemaClass):
    path = ID(stored=True)
    asunto = TEXT(stored=True)
    contenido = TEXT(stored = True)
    remitente = TEXT(stored=True)
    destinatarios = TEXT(stored=True)
    
class Aplicacion(object):
    
    def __init__(self):
        self.indice = None
        self.emaildirectory = "Correos"
        self.ventana = Tk()
        self.framebusqueda = Frame()
        self.framebremitente = Frame()
        self.framebcontenido = Frame()
        Button(self.framebusqueda,text="Buscar por remitente",command= self.buscar_por_remitente).pack(fill=BOTH)
        Button(self.framebusqueda,text="Buscar por contenido",command= self.buscar_por_contenido).pack(fill=BOTH)
        self.framebusqueda.pack()
        
    def create_index(self):
        # Creamos un indice en la dirección correos
        if not os.path.exists("Indices"): os.mkdir("Indices")
        self.indice = create_in("Indices", FicherosSchema, "IndiceCorreos")
    
    def indexing_emails(self):
        # Abrimos el indice
        ix = index.open_dir("Indices", "IndiceCorreos")
        writer = ix.writer()
        # Recorremos los ficheros
        for root, dirs, files in os.walk(self.emaildirectory):
            for name in files:
                # Si el nombre del fichero esta compuesto solo por números significa que es un fichero de email
                if(re.match('\d+\.txt', name)):

                    # Abrimos el archivo de email y obtenemos la información
                    filepath = os.path.join(root,name)
                    f = open(filepath,'r')
                    temp = f.read().splitlines()
                    remitente = temp[0]
                    destinatarios = temp[1]
                    asunto = temp[2]
                    cuerpo = '\n'.join(temp[3:])
                    
                    # Añadimos el documento al indice
                    writer.add_document(path = str(filepath),asunto = str(asunto), contenido = str(cuerpo), remitente = str(remitente), destinatarios = str(destinatarios))
                    f.close()
        writer.commit()     
               
    def search(self,content):
        # Buscamos en el contenido lo especificado por la variable content
        from whoosh.qparser import QueryParser
        with self.indice.searcher() as searcher:
            query = QueryParser("contenido", self.indice.schema).parse(content)
            results = searcher.search(query)
            resultado = []
            for r in results:
                    resultado.append({'path':r['path'],'remitente': r['remitente'], 'destinatarios':r['destinatarios'],'contenido':r['contenido'],'asunto':r['asunto']})
            return resultado  
    def search_by_sender(self,sender):
        # Buscamos el email del sender en el archivo de agenda
        agenda = open("Agenda/agenda.txt", 'r')
        textagenda = agenda.read()
        email = re.findall('(.*)\s'+sender, textagenda)
        agenda.close()
        if(email):
            resultado = []
            # Buscamos en el remitente lo especificado por la variable sender
            from whoosh.qparser import QueryParser
            with self.indice.searcher() as searcher:
                query = QueryParser("remitente", self.indice.schema).parse(email[0])
                results = searcher.search(query)
                for r in results:
                    resultado.append({'path':r['path'],'remitente': r['remitente'], 'destinatarios':r['destinatarios'],'contenido':r['contenido'],'asunto':r['asunto']})
                return resultado
        else:
            messagebox.showerror("Error", "Esta persona no consta en la agenda", parent = self.ventana)
            return None
        
    def inicio(self):
        # Carga la vista de inicio    
        self.framebremitente.pack_forget()
        self.framebcontenido.pack_forget()
        self.framebcontenido = Frame()
        self.framebremitente = Frame()
        self.framebusqueda.pack()
        
    def buscar_por_remitente(self):
        # Carga la vista de buscar por remitente:
        self.framebusqueda.pack_forget()
        remitentevar = StringVar()
        Label(self.framebremitente, text = 'Introduzca un remitente:').pack(padx = 5, pady = 5, fill = X, side = LEFT, expand = True)
        control_remitente = Entry(self.framebremitente, textvariable = remitentevar)
        control_remitente.pack(padx = 5, pady = 5, side= LEFT, fill = X, expand = True)
        self.framebremitente.pack()
        control_remitente.insert(0,"Antonio Garcia")
        def resultados_remitente():
            # Muestra los resultados de la busqueda por remitente:
            introducido = control_remitente.get()
            if introducido != "":
                # Buscamos los emails del remitente introducido:
                emails = self.search_by_sender(introducido)
                # Creo la nueva ventana para mostrar los resultados:
                rv = Tk()
                rv.title('Emails')
                scrollbary = Scrollbar(rv)
                scrollbarx = Scrollbar(rv,orient=HORIZONTAL)
                scrollbarx.pack(side = BOTTOM, fill= X)
                scrollbary.pack(side = RIGHT, fill= Y)
                text = Text(rv, wrap=NONE, yscrollcommand = scrollbary.set, xscrollcommand = scrollbarx.set)
                text.pack(side = LEFT, fill = BOTH, expand = True)
                scrollbary.config(command = text.yview)
                scrollbarx.config(command = text.xview)
                for email in emails:
                    stremail = 'Email '+email['path']+'\n'
                    stremail += 'Remitente: '+email['remitente']+'\n'
                    stremail += 'Destinatarios: '+email['destinatarios']+'\n'
                    stremail += 'Asunto: '+email['asunto']+'\n'
                    stremail += '\n'+email['contenido']+'\n'
                    stremail += '-------------------------------------------------------------\n'
                    text.insert(INSERT, stremail)
            else:
                messagebox.showerror("Error", "Debe introducir un remitente válido", parent = self.ventana)  
            
        Button(self.framebremitente, text="Atras", command= self.inicio).pack(fill=BOTH, side=TOP)
        Button(self.framebremitente,text="Buscar",command= resultados_remitente).pack(fill=BOTH, side= BOTTOM)
        
    def buscar_por_contenido(self):
        # Carga la vista de buscar por remitente
        self.framebusqueda.pack_forget()
        contenidovar = StringVar()
        Label(self.framebcontenido, text = 'Introduzca un contenido:').pack(padx = 5, pady = 5, fill = X, side = LEFT, expand = True)
        control_remitente = Entry(self.framebcontenido, textvariable = contenidovar)
        control_remitente.pack(padx = 5, pady = 5, side= LEFT, fill = X, expand = True)
        self.framebcontenido.pack()
        
        def resultados_contenido():
            # Muestra los resultados de la busqueda por contenido:
            introducido = control_remitente.get()
            if introducido != "":
                # Buscamos los emails del contenido introducido:
                emails = self.search(introducido)
                # Creo la nueva ventana para mostrar los resultados:
                rv = Tk()
                rv.title('Emails')
                scrollbary = Scrollbar(rv)
                scrollbarx = Scrollbar(rv,orient=HORIZONTAL)
                scrollbarx.pack( side = BOTTOM, fill= X)
                scrollbary.pack( side = RIGHT, fill= Y)
                text = Text(rv,wrap=NONE, yscrollcommand = scrollbary.set, xscrollcommand = scrollbarx.set)
                text.pack(side = LEFT, fill = BOTH, expand = True)
                scrollbary.config(command = text.yview)
                scrollbarx.config(command = text.xview)
                for email in emails:
                    stremail = 'Email: '+email['path']+'\n'
                    stremail += 'Remitente: '+email['remitente']+'\n'
                    stremail += 'Destinatarios: '+email['destinatarios']+'\n'
                    stremail += 'Asunto: '+email['asunto']+'\n'
                    stremail += '\n'+email['contenido']+'\n'
                    stremail += '-------------------------------------------------------------\n'
                    text.insert(INSERT, stremail)
            else:
                messagebox.showerror("Error", "Debe introducir un contenido válido", parent = self.ventana)    
        Button(self.framebcontenido, text="Atras", command= self.inicio).pack(fill=BOTH, side=TOP)
        Button(self.framebcontenido,text="Buscar",command= resultados_contenido).pack(fill=BOTH, side= BOTTOM)
        
    def run(self):
        self.create_index()
        self.indexing_emails()
        
        self.ventana.mainloop()
# Ejecución principal        
if __name__ == '__main__':
    app = Aplicacion()
    app.run()
