#Cálculos de iluminación y duración del día evaluado.
import numpy as np


def add_illumination_columns(dataframe):
    #Agrega estado de iluminación y duración integrada aproximada.
    df = dataframe.copy()
    df["illumination"] = (
        df["solar_elevation_deg"] > 0.0
    ).astype(int)
    return df


def integrate_illumination_hours(elapsed_hours, illumination):
    #Integra el indicador de iluminación mediante regla trapezoidal.
    x = np.asarray(elapsed_hours, dtype=float)
    y = np.asarray(illumination, dtype=float)
    if len(x) < 2:
        return 0.0
    return float(np.trapezoid(y, x))
