import tkinter as tk
from tkinter import messagebox




def ventana_principal():
    root = tk.Tk()

    root.title("My first GUI")
    #Con geometry vamos a tocar el tamaño de la ventana al abrirse
    root.geometry("720x480")
    label = tk.Label(root,text="Recuerda que necesitas hacer pack para cada elemento nuevo", font=('ComicSans',12))
    label.pack(padx=25, pady=10)
    #Para insertar texto
    textbox = tk.Text(root, height=3)
    #Dentro de nuestro textbox podremos hacer scroll si superamos el marco de alto
    textbox.pack()
    #Empecemos con los botones
    button = tk.Button(root,text="SOY UN BOTON",font=('Arial',10), command=mostrar_mensaje())
    button.pack(pady=20)

    root.mainloop()

def mostrar_mensaje():
    #print("Si añades un command al boton, este hara algo")
    mensaje = "Si añades un command al boton, este hara algo"
    messagebox.showinfo(title="boton", message= mensaje)

if __name__ == "__main__":
    ventana_principal()