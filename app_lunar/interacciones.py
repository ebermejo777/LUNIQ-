#se importa la librería para hacer una interfaz gráfica de usuario
from tkinter import *
from weakref import ref

#se importa la clase "graficar" del código "mapa_2D", solo funciona si el current directory es "codigo_principal"
from mapa_2D import graficar

#se importan desde matplotlib las clases que permiten insertar un gráfico en Tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)

class mapas_y_puntos:
    def __init__(self, contador_, lista_punt_, ventana_, listado_, hist_mapas_):
        self._contador = contador_
        self._lista_punt = lista_punt_
        self._mapa = None
        self._toolbar = None
        self._marco = None
        self._listado = listado_
        self._ventana = ventana_
        self._hist_mapas = hist_mapas_
        self.escala_calor = 1
        
    def imagen(self, ref, dim):

        #se instancia el mapa con la diercción del archivo de imagen y la tabla de puntos de interés
        #la tabla debería ser siempre la misma
        grafico = graficar(ref, dim, 'searchresults3.csv')
        grafico.escala_calor = self.escala_calor

        #se genera internamente el mapa como parte de la ventana
        self._marco = FigureCanvasTkAgg(grafico.calibrar(), master = self._ventana)

        #se ubica la barra de acciones de matplotlib como barra de acciones de la ventana
        self._toolbar = NavigationToolbar2Tk(self._marco, self._ventana)
        self._toolbar.update()

        self._mapa = grafico
        
        #se retorna la instancia del mapa
        return grafico
    
    #procedimiento para imprimir la lista de puntos siempre que se actualice
    def listar_puntos(self, evento, _mapa):
        
        #se vacía la lista de puntos mostrada en la UI
        self._listado.delete(0, END)

        #la variable de lista_punt se declara global, para poder usarse en varios procedimientos y no perderse al cambiar de mapa
        self._lista_punt = _mapa._puntos

        #se muestra la lista de puntos en la UI actualizada
        for i in self._lista_punt:
            self._listado.insert(END, str(i[1])+"°N, "+str(i[0])+"°E")

    #se define un procedimiento para cambiar el mapa que se muestra en la ventana
    def cambiar_mapa(self, mapa = None):
        #estas acciones se realizan en cada cambio de mapa
        

        #si no se ha hecho ningún cambio antes, se genera el  mapa visual de la luna
        if self._contador == 2:
            self._marco.get_tk_widget().pack_forget()
            #se oculta la barra de acciones
            self._toolbar.pack_forget()
            mapa =  self.generar_mapas("Sun irradiance over moon heatmap", '\nirradiance [W/m^2]', 1368)
        elif self._contador == 1:
            self._marco.get_tk_widget().pack_forget()
            #se oculta la barra de acciones
            self._toolbar.pack_forget()
            mapa =  self.generar_mapas("Earth's angle over moon horizon heatmap", '\nAngle [degree]', 90)

        #se muestran en la ventana el gráfico y la barra de acciones del mapa de pendiente, la última debe estar en la parte inferior de la ventana
        self._marco.get_tk_widget().pack(side  = TOP)
        self._toolbar.config(background="#0042A6")
        self._toolbar._message_label.config(foreground="white", background="#0042A6")
        self._toolbar.pack(side  = BOTTOM)

        #se actualiza la posición de los puntos en el mapa, para que se muestren los puntos añadidos en el mapa anterior
        mapa._editor_puntos.set_positions({mapa._editor_puntos._classes[0]:self._lista_punt})
        #se actualiza la lista interna de puntos del mapa, para que se puedan añadir o quitar puntos en el mapa actual
        mapa._puntos = self._lista_punt

        #se conecta el procedimiento para imprimir la lista de puntos al evento "button_press_event" para que se ejecute tras cada clic de mouse
        #esta acción está asociada unicamente al mapa, por lo que debe actualizarse cada vez que se cambie el mapa. Hay que añadir un nuevo punto si se quiere ver los anteriores
        mapa.fig.canvas.mpl_connect("button_press_event", lambda event: self.listar_puntos(event, mapa))

    def generar_mapas(self, titulo, unidad, max):
        #el contador se reduce 1, pues solo debe generarse este mapa una vez, así se garantiza que el contador no regrese a 2
        self._contador -= 1
        
        #esta función actualiza las variables globales de arriba, dandoles un valor asociado al nuevo mapa
        self.escala_calor = max
        mapa = self.imagen("Unified_Global_Geologic_Map_of_the_Moon_Geologic_Contacts//Unified_Global_Geologic_Map_of_the_Moon_Geologic_Contacts.shp", [2048,1024])
        
        #se guardan los nuevos datos del mapa en el diccionario hist_mapas, para poder mostrarlo otra vez
        self._hist_mapas[titulo] = [mapa, self._toolbar, self._marco]
        mapa.ax1.set_title(titulo, color = "white")
        mapa.cbar.ax.set_xlabel(unidad, color = 'w')
        return mapa
    
    def recuperar_mapas(self, indice):
        #se oculta la barra de acciones
        self._toolbar.pack_forget()
        #se oculta el gráfico
        self._marco.get_tk_widget().pack_forget()
        #se obtienen los datos del mapa a mostrar
        map_act = list(self._hist_mapas.values())[indice]
        #las variables globales se actualizan, adquiriendo los datos guardados del mapa de pendiente en el diccionario hist_mapas
        self._marco = map_act[2]
        self._toolbar = map_act[1]
        self.cambiar_mapa(map_act[0])

        
        