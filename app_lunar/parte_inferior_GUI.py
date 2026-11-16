from tkinter import *
from energy import energia
import datetime

class gui_:
    def __init__(self, _canvas, punto1, punto2, punto3):
        self._canvas = _canvas
        self.puntos = [punto1, punto2, punto3]
        self.coords = []
        self.punto_ = [0, 0]
        self.elevacion = None
        self.elevacion2 = None
        self.datos = None
        self.datos2 = None
        self.dif_fechas = 24
        self._scroll = None
        self.inst_mapa = None

    
    def seleccion(self, indice):
        self.coords[indice].config(text= str(self.punto_[1])+"°N, "+str(self.punto_[0])+"°E")
        self.puntos[indice] = self.punto_

    def info_graf(self, punto_1, punto_2, punto_3, inicial, final):
        #las fechas del calendario están en formato date, se necesitan como string
        fecha1 = str(inicial)
        fecha2 = str(final)
        nuevo = energia(punto_1, punto_2, punto_3, fecha1, fecha2)
        return nuevo

    def gen_graf(self, inicio, fin):
        fuente = self.info_graf(self.puntos[0], self.puntos[1], self.puntos[2], inicio, fin)
        fuente.grafica()

    def desarrollo(self, inicio, fin, target):
        fuente = self.info_graf([0,0], [90, 0], [0,0], inicio, fin)
        self.datos = fuente.results["Punto_01"]["data"]
        self.datos2 = fuente.results["Punto_02"]["data"]
        self.elevacion = self.datos[target]
        self.elevacion2 = self.datos2[target]
        self.dif_fechas = int((fin - inicio).total_seconds() // 3600) + 24
        self._scroll.configure(to=self.dif_fechas)
        self.scroller(0, self.dif_fechas)

    def scroller(self, valor, valormax):
        indice = int(float(valor)*len(self.elevacion)/valormax)
        angulo = self.elevacion[indice]
        angulo2 = self.elevacion2[indice]
        self.inst_mapa.luz = angulo
        self.inst_mapa.luz2 = angulo2
        self.inst_mapa.act_mapa()

    def generar(self):
        caja_scroll = Frame(self._canvas)
        self._scroll = Scale(caja_scroll, orient=HORIZONTAL, from_=0, to= self.dif_fechas, command = lambda val: self.scroller(val, self.dif_fechas), label = "hours")
        self.desarrollo(datetime.date(2027, 1, 1), datetime.date(2027, 1, 1), "solar_elevation_deg")
        self._scroll.pack(ipadx = 400, side = LEFT, padx = 50)
        caja_scroll.grid(column=0, row=1)
        pt_1 = Label(self._canvas, text="point 1: ")
        pt_2 = Label(self._canvas, text="point 2: ")
        pt_3 = Label(self._canvas, text="point 3: ")
        coord_1 = Label(self._canvas, text = str(self.puntos[0][1])+"°N, "+str(self.puntos[0][0])+"°E", background = "white", foreground = "#07173f")
        coord_2 = Label(self._canvas, text = str(self.puntos[1][1])+"°N, "+str(self.puntos[1][0])+"°E", background = "white", foreground = "#07173f")
        coord_3 = Label(self._canvas, text = str(self.puntos[2][1])+"°N, "+str(self.puntos[2][0])+"°E", background = "white", foreground = "#07173f")
        self.coords = [coord_1, coord_2, coord_3]
        cambia_1 = Button(self._canvas, command= lambda : self.seleccion(0), text = "choose selected coordinates")
        cambia_2 = Button(self._canvas, command= lambda : self.seleccion(1), text = "choose selected coordinates")
        cambia_3 = Button(self._canvas, command= lambda : self.seleccion(2), text = "choose selected coordinates")
        pt_1.grid(column=1, row=0)
        pt_2.grid(column=1, row=1)
        pt_3.grid(column=1, row=2)
        self.coords[0].grid(column=2, row=0)
        self.coords[1].grid(column=2, row=1)
        self.coords[2].grid(column=2, row=2)
        cambia_1.grid(column=3, row=0)
        cambia_2.grid(column=3, row=1)
        cambia_3.grid(column=3, row=2)

    



