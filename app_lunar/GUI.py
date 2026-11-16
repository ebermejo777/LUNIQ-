#se importa la librería para hacer una interfaz gráfica de usuario
from tkinter import *
from tkcalendar import Calendar


from interacciones import mapas_y_puntos 
from parte_inferior_GUI import gui_

#se instancia una ventana que usa la interfaz
ventana = Tk()
ventana.title("sunlight over moon")
# Cargar el archivo de imagen desde el disco.
icono = PhotoImage(file="Space Apps Logo Color and Black motif.png")
# Establecerlo como ícono de la ventana.
ventana.iconphoto(True, icono)

ventana.tk_setPalette(background="#0042A6", selectColor="#07173f", foreground="white")

#se crea un frame que contenga el listado de puntos y un calendario
mi_frame = Frame(ventana, bg="#0042A6")


#se genera el título de la lista
lbl = Label(mi_frame, text = "points coordinates")

#se genera en la UI la lista de puntos
listado = Listbox(mi_frame, width=84, height=15, bg="#07173f", fg = "white")


#se instancia un objeto de la clase mapas_y_puntos, que contiene los procedimientos para interactuar con la GUI
interaccion = mapas_y_puntos(contador_ = 2, lista_punt_ = [], ventana_ = ventana, listado_ = listado, hist_mapas_ = {})

#se llama a la función para insertar el gráfico, el gráfico será a base de la imagen del mapa
mapa = interaccion.imagen('mapa_color.tif', [2048,1024])
interaccion._hist_mapas['mapa_color.tif'] = [mapa, interaccion._toolbar, interaccion._marco]

#espacio para opciones de mapa
cambiar = Frame(ventana, bg="#0042A6")
#botones para volver a cambiar el mapa
cambio_1 = Button(cambiar, text = 'standard moon map', command = lambda : interaccion.recuperar_mapas(0), bg="#EAFE07", fg = "#07173f")
cambio_2 = Button(cambiar, text = 'irradiance moon map', command = lambda : interaccion.recuperar_mapas(1), bg="#EAFE07", fg = "#07173f")
cambio_3 = Button(cambiar, text = 'communication moon map', command = lambda : interaccion.recuperar_mapas(2), bg="#EAFE07", fg = "#07173f")

#se ubica el botón de cambio de mapa en la interfaz, está debajo del mapa y encima de la barra de acciones
cambiar.pack(before = interaccion._toolbar, ipady=20, ipadx=40, pady = 15)

#no se pueden añadir puntos hasta que se halla cambiado el mapa, así que se cambia apenas inica el programa
interaccion.cambiar_mapa()
interaccion.cambiar_mapa()

#se ubican los puntos para seleccionar el tipo de mapa
cambio_1.grid(column = 0, row = 0)
cambio_2.grid(column = 1, row = 0)
cambio_3.grid(column = 2, row = 0)

#se ubica mi frame en la interfaz, se ajusta a la ventana en el eje Y, está a la derecha del mapa
mi_frame.pack(side = RIGHT, expand = True, fill = Y, pady = 5, after = interaccion._marco.get_tk_widget(), before = cambiar)

#se ubica el titulo de la lista en el frame
lbl.grid(column = 0, row = 0, columnspan=4)

#se ubica la lista de puntos en el frame
listado.grid(column = 0, row = 1, columnspan=4)

#se crean dos calendarios seleccionables bajo la lista
lbl_inicio = Label(mi_frame, text = "start date")
cal_inicio = Calendar(mi_frame, selectmode = 'day', year = 2027, month = 1, day = 1)
cal_inicio.grid(column = 0, row = 3, columnspan=2)
lbl_inicio.grid(column = 0, row = 2, columnspan = 2)
lbl_final = Label(mi_frame, text = "end date")
cal_final = Calendar(mi_frame, selectmode = 'day', year = 2027, month = 1, day = 1)
cal_final.grid(column = 2, row = 3, columnspan=2)
lbl_final.grid(column = 2, row = 2, columnspan = 2)




#hay otros elementos en la parte inferior de la GUI, pero no aparecerán aquí para no alargar más el codigo
abajo = Frame(ventana, bg="#0042A6")
abajo.pack(after = mi_frame, side=BOTTOM, pady = 15)
contenido = gui_(abajo, [0,0], [0,0], [0,0])
contenido.inst_mapa = interaccion._mapa.ds
contenido.generar()

#se crean dos puntos, uno para mostrar la iluminación por fecha y otro para generar un grafico
actualizar = Button(mi_frame, text = "select time interval", command= lambda : contenido.desarrollo(cal_inicio.selection_get(), cal_final.selection_get(), "solar_elevation_deg"))
actualizar.grid(column = 1, row = 4, columnspan = 2)

def punto_de_lista(evento):
    global contenido
    global interaccion

    seleccion = evento.widget.curselection()
    if seleccion:
        indice = seleccion[0]
    else:
        indice = 0
    contenido.punto_ = interaccion._lista_punt[indice]

listado.bind('<<ListboxSelect>>', punto_de_lista)

graf = Button(mi_frame, text = "plot Sun and Earth positions", command = lambda : contenido.gen_graf(cal_inicio.selection_get(), cal_final.selection_get()), bg="#EAFE07", fg = "#07173f")
graf.grid(column=1, row=5, columnspan = 2)

#se establecen las dimensiones de la ventana, no se pueden cambiar
ventana.geometry("1900x700")
#ventana.resizable(width=0, height=0)

#procedimiento para terminar el programa
def cerrar_ventana():
    #se destruye la ventana y se termina el programa
    ventana.destroy()
    print("program terminated")
    exit()

#se establece que al cliquear la X de la ventana se ejecute el procedimiento cerrar_ventana
ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)


#se puede terminar el programa con Ctrl+C, se muestra un mensaje en la consola para indicarlo
print("type Ctrl+C to stop running the program")
try:
    #se muestra la ventana y se va actualizando a cada frame
    ventana.mainloop()
except KeyboardInterrupt:
    print("program terminated")