#generación de mapa de pendientes lunares

#libreria de mapas
import rasterio
from rasterio.plot import show

import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib.ticker import MaxNLocator
import csv


#libreria para añadir puntos a un mapa
from mpl_point_clicker import clicker
from mapa_calor import grafico_calor

#clase para hacer un mapa 2-D con la opción de añadir puntos
class graficar:
    def __init__(self, mapa, dim_mapa, sitios):
        #el primer parámetro es la ruta al archivo del mapa
        self._mapa = mapa
        #el segundo parámetro es la ruta al archivo csv con lugares de interés
        self._sitios = sitios

        #se crea una figura con un subplot, disponible para todas las funciones con parámetro self
        #la figura debe ser lo suficientemente ancha para incluir el botón que añade puntos
        self.fig, self.ax1 = plt.subplots(figsize = (11,4))
        self.fig.set_facecolor('#0042A6')
        self.fig.canvas.manager.set_window_title("map")

        #aquí se almacenan los puntos añadidos
        self._puntos = []

        #aquí se guarda el clicker como atributo
        self._editor_puntos = None

        #aquí se guarda un atributo que permita desactivar el listado de puntos
        self._escucha = None

        #aquí se guardan las dimensiones del archivo .tif para más adelante convertir la posición de cada pixel en coordenadas
        self._dim_mapa = dim_mapa

        #aquí se guardan los nombre visibles
        self._ubicaciones = []

        #variables que solo aplican para los mapas de calor
        self.cbar = None
        self.escala_calor = None
        self.ds = None


    #función para añadir cada tupla de coordenadas a la lista de puntos
    def nuevo_punto(self, coords, zero):
        item = [coords[0], coords[1]]
        self._puntos.append(item)

    #función para eliminar las tuplas de los puntos borrados de la lista de puntos
    def quitar_punto(self, coords, idx, dict):
        #se guardan las coordenadas del último punto borrado en el formato de la lista de puntos
        punto = [coords[0], coords[1]]
        #si se encuentra una coincidencia en la lista de puntos con el punto borrado, se elimina de la lista
        if punto in self._puntos:
            self._puntos.remove(punto)

    #procedimiento que ubica los nombres de los sitios de interés en el mapa
    def lugares(self, ejes, f):
        #se reinicia el array para las ubicaciones visibles
        if len(self._ubicaciones) != 0:
            for ubicacion in self._ubicaciones:
                ubicacion.remove()
        self._ubicaciones = []
        #self._ubicaciones.clear()
        for row in f:
            #para cada fila del archivo, se agregan los datos de nombre y coordenadas como texto en la posición correspondiente del mapa
            #solo los sitios más grandes se muestran en pantalla, según la escala usada en el eje x
            if ((float(row['Diameter']) > (ejes.get_xlim()[1]- ejes.get_xlim()[0])*2) and (float(row['Center Longitude']) < ejes.get_xlim()[1])
                and (float(row['Center Longitude']) > ejes.get_xlim()[0]) and (float(row['Center Latitude']) < ejes.get_ylim()[1])
                and (float(row['Center Latitude']) > ejes.get_ylim()[0])):
                self._ubicaciones.append(ejes.text(float(row['Center Longitude']), float(row['Center Latitude']), 
                                                   str(row['\ufeffFeature Name']), fontsize= 8, color = '#0960E1', 
                                                   ha = 'center', zorder=1000))
                self._ubicaciones[len(self._ubicaciones) - 1].set_path_effects([PathEffects.withStroke(linewidth=5, foreground='w')])

    #función para generar el gráfico
    def calibrar(self):

        if self._mapa[-4:] == ".tif":
            #estos puntos son de referencia, permiten convertir la posición de los pixeles en coordenadas selenográficas
            punto1 = rasterio.control.GroundControlPoint(row = 0, col = 0, x = -180, y = 90)
            punto2 = rasterio.control.GroundControlPoint(row = self._dim_mapa[1], col = self._dim_mapa[0], x = 180, y = -90)
            punto3 = rasterio.control.GroundControlPoint(row = self._dim_mapa[1] / 2, col = 0, x = -180, y = 0)

            #se guardan los puntos de referencia en un array y se pone en un formato compatible con las propiedades del raster
            puntos = [punto1, punto2, punto3]
            transformacion = rasterio.transform.from_gcps(puntos)

            #se abre el archivo, de 3000 x 6000 pixeles con datos de las pendientes de toda la luna
            ds1 = rasterio.open(self._mapa)

            self.ax1.set_title("Moon surface map", color = "white")
            self.ax1.yaxis.set_major_locator(MaxNLocator(nbins=5))
            self.ax1.tick_params(axis='x', colors='white')
            self.ax1.tick_params(axis='y', colors='white')
            #se especifican los nombres de los ejes
            self.ax1.set_xlabel('Geodetic longitude [degree]', color = 'w')
            self.ax1.set_ylabel('Geodetic latitude[degree]', color = 'w')

            #se grafica internamente la imagen con la transformación de coordenadas
            show(ds1.read(), ax=self.ax1, transform=transformacion, zorder = 0)
            

        elif self._mapa[-4:] == ".shp":

            ds1 = grafico_calor(self.ax1, self._mapa, self.fig)
            ds1.escala_calor = self.escala_calor
            ds1.generar()
            self.cbar = ds1.cbar
            self.ds = ds1
            


        #se abre el archivo con sitios de interés
        with open('searchresults3.csv', mode='r', encoding='utf-8') as archivo:
            arch = list(csv.DictReader(archivo))

        #print(f.fieldnames)

        #se llama al procedimiento que ubica los sitios de interés
        self.lugares(self.ax1, arch)

        #cada que se actualice la escala se deberían actualizar los sitios
        registro = self.ax1.callbacks
        registro.connect('xlim_changed', lambda event: self.lugares(self.ax1, arch))
        registro.connect('ylim_changed', lambda event: self.lugares(self.ax1, arch))

        #se instancia un objeto para generar puntos circulares y rojos, se guarda en el atributi _editor_puntos
        self._editor_puntos = clicker(self.ax1, markers = "o", colors = ['#0960E1'], classes = ["Add to \nrefresh \npoints"])
        #se guarda la id de conexion permite llamar a la función que lista los puntos cuando son añadidos, se retorna para poder bloquearla si es necesario
        self._escucha = self._editor_puntos.on_point_added(self.nuevo_punto)
        #se llama al procedimiento para eliminar puntos de la lista cada que un punto sea borrado
        self._editor_puntos.on_point_removed(self.quitar_punto)

        # Se establece la prioridad visual de los puntos
        for elemento in self.ax1.collections:
            elemento.set_zorder(1000)

        for elemento in self.ax1.lines:
            elemento.set_zorder(1000)

        #se retorna la figura de matplotlib en caso de que se necesite acceder a ella
        return self.fig  

    def __del__(self):
        del self

