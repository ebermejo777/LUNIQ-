# Funciones basadas en SPICE
from pathlib import Path
import numpy as np
import spiceypy as spice

au = 149_597_870.7 # Unidad astrónomica a utilizar
sc = 1361.0 #Constante de irradiación solar W/m^2


def load_kernels(kernel_directory, kernel_files=None):
    
    #Carga de kernels SPICE
    directory = Path(kernel_directory)
    if kernel_files is None:
        kernel_files = [
            "naif0012.tls",
            "de440s.bsp",
            "pck00011.tpc",
        ]

    spice.kclear()
    loaded = []
    for filename in kernel_files:
        path = directory / filename
        if not path.is_file():
            spice.kclear()
            raise FileNotFoundError(f"No se encontró el kernel: {path}")
        spice.furnsh(str(path))
        loaded.append(str(path))
    return loaded


def unload_kernels():
    #Descarga los kernels SPICE
    spice.kclear()


def solar_position(latitude_deg, longitude_deg, et):
    
    #Calcula la posición solar local para coordenadas lunares planetocéntricas.

    #Convenciones:
    #latitud: grados, -90 a +90;
    #longitud: grados, -180 a +180, positiva hacia el este;
    #frame: IAU_MOON;
    #origen: centro de la Luna.

    #Devuelve elevación, azimut y distancia Sol-Luna. La elevación se calcula respecto a la normal radial de una Luna esférica; no incluye relieve.
    
    if not -90 <= float(latitude_deg) <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90 grados.")
    if not -180 <= float(longitude_deg) <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180 grados.")

    # Posición aparente del Sol, con corrección de tiempo de luz y aberración.
    state, _ = spice.spkezr("SUN", et, "IAU_MOON", "LT+S", "MOON")
    vector = np.asarray(state[:3], dtype=float)
    distance_km = float(np.linalg.norm(vector))
    if distance_km <= 0:
        raise RuntimeError("Distancia Sol-Luna no válida.")

    sun_unit = vector / distance_km
    lat = np.radians(float(latitude_deg))
    lon = np.radians(float(longitude_deg))

    up = np.array([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])
    east = np.array([-np.sin(lon), np.cos(lon), 0.0])
    north = np.cross(up, east)

    east_component = float(np.dot(sun_unit, east))
    north_component = float(np.dot(sun_unit, north))
    up_component = float(np.clip(np.dot(sun_unit, up), -1.0, 1.0))

    elevation_deg = float(np.degrees(np.arcsin(up_component)))
    azimuth_deg = float(np.degrees(np.arctan2(
        east_component, north_component
    )) % 360.0)

    normal_irradiance = (
        sc * (au / distance_km) ** 2
    )
    horizontal_irradiance = normal_irradiance * max(0.0, up_component)

    return {
        "solar_elevation_deg": elevation_deg,
        "solar_azimuth_deg": azimuth_deg,
        "sun_moon_distance_km": distance_km,
        "normal_irradiance_W_m2": normal_irradiance,
        "irradiance_W_m2": horizontal_irradiance,
        "sun_above_geometric_horizon": elevation_deg > 0.0,
    }
