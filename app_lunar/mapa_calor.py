import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
from matplotlib.ticker import MaxNLocator

#clase para generar un mapa de calor que describa la irradianza solar sobre la superficie lunar
class grafico_calor():
    def __init__(self, ax, archivo, figura):
        #en esta variable se va a referenciar el gráfico usado
        self._ax = ax
        #self.arch va a contener la ruta relativa de un mapa geológico de la Luna, en formato shp
        self.arch = archivo
        #esta variable va a contener el fig que acompaña a self._ax
        self.fig = figura
        self.cbar = None
        self.escala_calor = 1
        self.luz = 0
        self.luz2 = 0
        self.im = None

    def valores_z(self):
        #los valores de x van de -180 a 180, con 1000 subdivisiones
        #los de y abarcan aproximadamente la mitad de valores con la mitad de subdivisiones
        xvals = np.linspace(-180, 180, 1000)
        yvals = np.linspace(-90, 90, 500)
        
        #se genera un meshgrid, un plano, que abarque los valores dados de x y y para graficar
        xvals, yvals = np.meshgrid(xvals, yvals)

        if self.luz2 > 0 and self.luz > 0:
            pos = 180 - self.luz1
        elif self.luz2 <= 0 and self.luz > 0:
            pos = self.luz
        elif 
        
        #z es el producto punto entre un vector de magnitud 1368 normal a la superficie y un vector que indica en qué coordenadas está el sol en su cénit
        zvals = (-1/2) * self.escala_calor * np.cos(np.deg2rad(yvals)) * np.sin(np.deg2rad(xvals - self.luz - 90))/np.sqrt(1 - ((np.sin(np.deg2rad(yvals)))**2) * ((np.cos(np.deg2rad(xvals - self.luz - 90)))**2))
        #z no puede tener valores negativos, pues en esas posiciones no pega el Sol, así que se convierten en 0 al sumarlos con su valor absoluto
        zvals = np.abs(zvals) + zvals
        return zvals

    #un procedimiento para generar el gráfico del mapa de calor
    def generar(self):

        zvals = self.valores_z()

        #se genera un mapa de calor de los valores de z, que equivale a la irradianza solar en cada punto
        self.im = self._ax.imshow(zvals,cmap='hot',extent=[-180,180,-90,90],interpolation='nearest',origin='lower',aspect='auto', zorder = 0)

        #Se usa geopandas para leer el archivo shp como polígonos
        mapa = gpd.read_file(self.arch)

        #se superpone el mapa geológico al mapa de calor, así va a servir de referencia para el usuario
        mapa.plot(
            ax=self._ax,
            color="gray",
            linewidth=0.3,
            zorder = 1
        )

        self._ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
        self._ax.tick_params(axis='x', colors='white')
        self._ax.tick_params(axis='y', colors='white')

        #se especifican los nombres de los ejes
        self._ax.set_xlabel('Geodetic longitude [degree]', color = 'w')
        self._ax.set_ylabel('Geodetic latitude[degree]', color = 'w')

        #se muestra una convención de colores para comprender el mapa de calor
        self.cbar = self.fig.colorbar(self.im, location = 'left')
        self.cbar.ax.tick_params(axis='y', colors='white')

    def act_mapa(self):
        zvals = self.valores_z()

        #actualizar los datos de la imagen
        self.im.set_data(zvals)

        #actualizar la escala de colores
        self.im.set_clim(vmin=zvals.min(), vmax=zvals.max())

        #actualizar la barra de colores
        self.cbar.update_normal(self.im)

        #redibujar el gráfico
        self.fig.canvas.draw_idle()