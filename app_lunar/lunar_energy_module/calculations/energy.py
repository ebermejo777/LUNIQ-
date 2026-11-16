#Irradiancia mediciones energéticas
import numpy as np


def _integrate(y, x):
    
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y, x))
    return float(np.trapz(y, x))


def integrate_energy(elapsed_hours, irradiance_W_m2):
    x = np.asarray(elapsed_hours, dtype=float)
    y = np.asarray(irradiance_W_m2, dtype=float)
    return _integrate(y, x) if len(x) >= 2 else 0.0


def summarize_energy(dataframe):
    hours = dataframe["elapsed_hours"].to_numpy(dtype=float)
    irradiance = dataframe["irradiance_W_m2"].to_numpy(dtype=float)
    illuminated = dataframe["illumination"].to_numpy(dtype=float)
    period_hours = float(hours[-1] - hours[0]) if len(hours) > 1 else 0.0
    energy_Wh_m2 = integrate_energy(hours, irradiance)
    energy_kWh_m2 = energy_Wh_m2 / 1000.0
    sunlight = _integrate(illuminated, hours) if len(hours) > 1 else 0.0
    darkness = max(0.0, period_hours - sunlight)
    return {
        "sunlight_hours": sunlight,
        "darkness_hours": darkness,
        "availability_percent": sunlight / period_hours * 100.0 if period_hours else 0.0,
        "energy_kWh_m2": energy_kWh_m2,
        "maximum_irradiance_W_m2": float(np.max(irradiance)),
        "mean_irradiance_W_m2": float(np.mean(irradiance)),
    }
