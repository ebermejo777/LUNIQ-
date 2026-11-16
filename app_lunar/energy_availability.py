"""Cálculo temporal de disponibilidad solar para múltiples ubicaciones lunares."""
from datetime import date, datetime, time, timedelta, timezone
import numpy as np
import pandas as pd
import spiceypy as spice

from .astronomical import solar_position
from .horizon import visible_above_horizon
from .energy import summarize_energy

NUMBER_OF_SAMPLES = 512


def _as_date(value, parameter_name):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{parameter_name} debe tener formato YYYY-MM-DD.") from exc
    raise TypeError(f"{parameter_name} debe ser date, datetime o YYYY-MM-DD.")


def calculate_energy_availability(locations, start_date, end_date, horizon_model=None):
    """
    Evalúa exactamente 512 instantes uniformes entre dos fechas UTC inclusivas.
    La fecha final incluye el día completo y termina a las 23:59:59 UTC.
    Todas las ubicaciones comparten los mismos instantes.
    """
    if not locations:
        raise ValueError("Debe seleccionarse al menos una ubicación.")

    first_day = _as_date(start_date, "start_date")
    last_day = _as_date(end_date, "end_date")
    if last_day < first_day:
        raise ValueError("end_date no puede ser anterior a start_date.")

    start_dt = datetime.combine(first_day, time.min, tzinfo=timezone.utc)
    end_dt = datetime.combine(last_day, time(23, 59, 59), tzinfo=timezone.utc)
    total_seconds = (end_dt - start_dt).total_seconds()
    if total_seconds <= 0:
        raise ValueError("El rango de fechas debe tener duración positiva.")

    sample_seconds = np.linspace(0.0, total_seconds, NUMBER_OF_SAMPLES)
    timestamps = [start_dt + timedelta(seconds=float(s)) for s in sample_seconds]
    elapsed_hours = sample_seconds / 3600.0
    total_hours = total_seconds / 3600.0

    # Conversión UTC->ET una sola vez por muestra, compartida por las ubicaciones.
    ephemeris_times = [
        spice.str2et(dt.strftime("%Y-%m-%dT%H:%M:%S.%f")) for dt in timestamps
    ]

    results = {}
    for location in locations:
        required = {"id", "latitude", "longitude"}
        missing = required.difference(location)
        if missing:
            raise ValueError(f"Faltan campos en ubicación: {', '.join(sorted(missing))}")

        location_id = str(location["id"])
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        if not -90 <= latitude <= 90:
            raise ValueError(f"Latitud fuera de rango para {location_id}.")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Longitud fuera de rango para {location_id}.")

        rows = []
        for current_time, elapsed, et in zip(timestamps, elapsed_hours, ephemeris_times):
            solar = solar_position(latitude, longitude, et)
            illuminated = visible_above_horizon(
                solar["solar_elevation_deg"], solar["solar_azimuth_deg"], horizon_model
            )
            irradiance = (
                solar["normal_irradiance_W_m2"]
                * max(0.0, np.sin(np.radians(solar["solar_elevation_deg"])))
                if illuminated else 0.0
            )
            rows.append({
                "datetime_utc": current_time,
                "elapsed_hours": float(elapsed),
                "solar_elevation_deg": solar["solar_elevation_deg"],
                "solar_azimuth_deg": solar["solar_azimuth_deg"],
                "sun_moon_distance_km": solar["sun_moon_distance_km"],
                "irradiance_W_m2": float(irradiance),
                "illumination": int(illuminated),
            })

        dataframe = pd.DataFrame(rows)
        summary = summarize_energy(dataframe)
        summary.update({
            "location_id": location_id,
            "latitude": latitude,
            "longitude": longitude,
            "start_date_utc": first_day.isoformat(),
            "end_date_utc": last_day.isoformat(),
            "number_of_samples": NUMBER_OF_SAMPLES,
            "period_hours": total_hours,
            "sample_spacing_minutes": total_seconds / (NUMBER_OF_SAMPLES - 1) / 60.0,
        })
        results[location_id] = {"data": dataframe, "summary": summary}

    return results
