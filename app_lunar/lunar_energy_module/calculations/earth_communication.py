#Visibilidad de la Tierra desde ubicaciones en la luna
#latitud y longitud se expresan en grados, con longitud este positiva. La orientación lunar y las posiciones aparentes se obtienen de los kernels SPICE.

from datetime import date, datetime, time, timedelta, timezone
import math

import numpy as np
import pandas as pd
import spiceypy as spice

from .time_grid import SAMPLE_INTERVAL_SECONDS, build_sampling_grid


def _as_date(value, parameter_name):
    #Convierte una fecha o datetime a fecha UTC sin aceptar formatos ambiguos."""
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).date()
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                f"{parameter_name} debe tener formato YYYY-MM-DD."
            ) from exc
    raise TypeError(f"{parameter_name} debe ser date, datetime o texto YYYY-MM-DD.")


def _validate_location(latitude_deg, longitude_deg):
    #Valida y convierte coordenadas lunares."""
    latitude = float(latitude_deg)
    longitude = float(longitude_deg)
    if not math.isfinite(latitude) or not -90.0 <= latitude <= 90.0:
        raise ValueError("La latitud debe ser un valor finito entre -90 y 90 grados.")
    if not math.isfinite(longitude) or not -180.0 <= longitude <= 180.0:
        raise ValueError("La longitud debe ser un valor finito entre -180 y 180 grados.")
    return latitude, longitude


def _surface_point_and_local_frame(latitude_deg, longitude_deg, radii_km):
    #Devuelve punto superficial y base local Este-Norte-Arriba.
    #La latitud de entrada es planetocéntrica. El punto se obtiene como la intersección del radio que parte del centro lunar con el elipsoide.
    #La dirección Arriba es la normal al elipsoide en ese punto, no el radio geocéntrico; esta diferencia importa fuera del ecuador y los polos.
    
    a, b, c = np.asarray(radii_km, dtype=float)
    if not np.all(np.isfinite([a, b, c])) or np.any(np.array([a, b, c]) <= 0.0):
        raise RuntimeError("El kernel PCK no proporciona radios lunares válidos.")

    latitude = math.radians(latitude_deg)
    longitude = math.radians(longitude_deg)
    radial_direction = np.array([
        math.cos(latitude) * math.cos(longitude),
        math.cos(latitude) * math.sin(longitude),
        math.sin(latitude),
    ])

    inverse_radius_squared = np.array([1.0 / a**2, 1.0 / b**2, 1.0 / c**2])
    denominator = float(np.dot(radial_direction**2, inverse_radius_squared))
    surface_radius = 1.0 / math.sqrt(denominator)
    surface_point = surface_radius * radial_direction

    # La normal de un elipsoide es proporcional a (x/a², y/b², z/c²).
    up = surface_point * inverse_radius_squared
    up /= np.linalg.norm(up)

    east = np.array([-math.sin(longitude), math.cos(longitude), 0.0])
    north = np.cross(up, east)
    north /= np.linalg.norm(north)
    return surface_point, east, north, up


def earth_position(latitude_deg, longitude_deg, et, minimum_elevation_deg=0.0):
    
    #Calcula elevación, azimut y distancia de la Tierra desde un punto lunar.
    #``et`` es el tiempo de efemérides SPICE (TDB). La posición aparente del centro terrestre se calcula en ``IAU_MOON`` con corrección ``LT+S``.
    #La visibilidad es geométrica y se determina comparando la elevación del centro terrestre con la máscara mínima indicada.
    
    latitude, longitude = _validate_location(latitude_deg, longitude_deg)
    threshold = float(minimum_elevation_deg)
    if not math.isfinite(threshold) or not -90.0 <= threshold <= 90.0:
        raise ValueError("minimum_elevation_deg debe estar entre -90 y 90 grados.")
    ephemeris_time = float(et)
    if not math.isfinite(ephemeris_time):
        raise ValueError("El tiempo ET debe ser un número finito.")

    state, _ = spice.spkezr("EARTH", ephemeris_time, "IAU_MOON", "LT+S", "MOON")
    earth_from_moon = np.asarray(state[:3], dtype=float)
    if earth_from_moon.shape != (3,) or not np.all(np.isfinite(earth_from_moon)):
        raise RuntimeError("SPICE devolvió una posición de la Tierra no válida.")

    radii = spice.bodvrd("MOON", "RADII", 3)[1]
    surface_point, east, north, up = _surface_point_and_local_frame(
        latitude, longitude, radii
    )
    earth_from_site = earth_from_moon - surface_point
    distance_km = float(np.linalg.norm(earth_from_site))
    if not math.isfinite(distance_km) or distance_km <= 0.0:
        raise RuntimeError("La distancia entre la ubicación lunar y la Tierra no es válida.")

    direction = earth_from_site / distance_km
    east_component = float(np.dot(direction, east))
    north_component = float(np.dot(direction, north))
    up_component = float(np.clip(np.dot(direction, up), -1.0, 1.0))

    elevation_deg = math.degrees(math.asin(up_component))
    azimuth_deg = math.degrees(math.atan2(east_component, north_component)) % 360.0

    return {
        "earth_elevation_deg": elevation_deg,
        "earth_azimuth_deg": azimuth_deg,
        "earth_moon_distance_km": distance_km,
        "communication_visible": int(elevation_deg > threshold),
    }


def _crossing_time(time_0, time_1, elevation_0, elevation_1, threshold):
    #Interpola linealmente el instante en que se cruza la máscara angular
    change = elevation_1 - elevation_0
    if change == 0.0:
        return time_1
    fraction = (threshold - elevation_0) / change
    fraction = min(1.0, max(0.0, fraction))
    return time_0 + (time_1 - time_0) * fraction


def _communication_windows(dataframe, threshold):
    #Construye ventanas continuas a partir de cruces interpolados.
    if dataframe.empty:
        return []

    timestamps = dataframe["datetime_utc"].tolist()
    elevations = dataframe["earth_elevation_deg"].to_numpy(dtype=float)
    visible = elevations > threshold
    windows = []
    window_start = timestamps[0] if visible[0] else None

    for index in range(1, len(timestamps)):
        if visible[index] == visible[index - 1]:
            continue

        crossing = _crossing_time(
            timestamps[index - 1], timestamps[index],
            elevations[index - 1], elevations[index], threshold,
        )
        if visible[index]:
            window_start = crossing
        elif window_start is not None:
            duration = (crossing - window_start).total_seconds() / 3600.0
            windows.append({
                "start_utc": window_start,
                "end_utc": crossing,
                "duration_hours": duration,
            })
            window_start = None

    if window_start is not None:
        duration = (timestamps[-1] - window_start).total_seconds() / 3600.0
        windows.append({
            "start_utc": window_start,
            "end_utc": timestamps[-1],
            "duration_hours": duration,
        })
    return windows


def _available_time_hours(timestamps, elevations, threshold):
    #Integra el tiempo visible usando los mismos cruces lineales de las ventanas.
    available_seconds = 0.0
    for index in range(1, len(timestamps)):
        interval_seconds = (timestamps[index] - timestamps[index - 1]).total_seconds()
        first_visible = elevations[index - 1] > threshold
        second_visible = elevations[index] > threshold

        if first_visible and second_visible:
            visible_fraction = 1.0
        elif not first_visible and not second_visible:
            visible_fraction = 0.0
        else:
            elevation_change = elevations[index] - elevations[index - 1]
            if elevation_change == 0.0:
                visible_fraction = 0.0
            else:
                crossing_fraction = (threshold - elevations[index - 1]) / elevation_change
                crossing_fraction = min(1.0, max(0.0, crossing_fraction))
                visible_fraction = (1.0 - crossing_fraction
                                    if second_visible else crossing_fraction)
        available_seconds += interval_seconds * visible_fraction
    return available_seconds / 3600.0


def _validate_sample_count(number_of_samples):
    #Evita truncar silenciosamente valores no enteros.
    if isinstance(number_of_samples, bool):
        raise TypeError("number_of_samples debe ser un entero mayor o igual que 2.")
    try:
        count = int(number_of_samples)
    except (TypeError, ValueError, OverflowError) as exc:
        raise TypeError("number_of_samples debe ser un entero mayor o igual que 2.") from exc
    if count != number_of_samples or count < 2:
        raise ValueError("number_of_samples debe ser un entero mayor o igual que 2.")
    return count


def calculate_earth_communication(
    locations,
    start_date,
    end_date,
    minimum_elevation_deg=0.0,
    number_of_samples=None,
):
    #Evalúa la visibilidad Tierra-Luna en una malla temporal UTC inclusiva.
    #Devuelve, por ubicación, un DataFrame de resultados, un resumen estadístico y una lista de ventanas. Se conserva la estructura de salida de la versión anterior para facilitar la integración con la interfaz y las gráficas.
    
    if not locations:
        raise ValueError("Debe seleccionarse al menos una ubicación.")

    first_day = _as_date(start_date, "start_date")
    last_day = _as_date(end_date, "end_date")
    if last_day < first_day:
        raise ValueError("end_date no puede ser anterior a start_date.")

    threshold = float(minimum_elevation_deg)
    if not math.isfinite(threshold) or not -90.0 <= threshold <= 90.0:
        raise ValueError("minimum_elevation_deg debe estar entre -90 y 90 grados.")

    start_datetime = datetime.combine(first_day, time.min, tzinfo=timezone.utc)
    # end_date es inclusiva: el límite final es la medianoche del día siguiente.
    # Así se modelan días completos y se conserva una malla exacta de 600 s.
    end_datetime = datetime.combine(
        last_day + timedelta(days=1), time.min, tzinfo=timezone.utc
    )
    total_seconds = (end_datetime - start_datetime).total_seconds()
    offsets_seconds, timestamps, interval_count = build_sampling_grid(
        start_datetime, end_datetime
    )
    sample_count = len(offsets_seconds)

    if number_of_samples is not None:
        requested_count = _validate_sample_count(number_of_samples)
        if requested_count != sample_count:
            raise ValueError(
                f"Con intervalos fijos de {SAMPLE_INTERVAL_SECONDS} s, "
                f"este periodo requiere {sample_count} puntos "
                f"({interval_count} intervalos). No se puede cambiar "
                "number_of_samples sin perder la resolución exacta."
            )
    elapsed_hours = offsets_seconds / 3600.0
    ephemeris_times = [
        spice.str2et(timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"))
        for timestamp in timestamps
    ]
    total_period_hours = total_seconds / 3600.0

    results = {}
    for location in locations:
        missing_fields = {"id", "latitude", "longitude"}.difference(location)
        if missing_fields:
            missing_text = ", ".join(sorted(missing_fields))
            raise ValueError(f"Faltan campos en ubicación: {missing_text}.")

        location_id = str(location["id"]).strip()
        if not location_id:
            raise ValueError("El identificador de cada ubicación no puede estar vacío.")
        if location_id in results:
            raise ValueError(f"El identificador de ubicación '{location_id}' está repetido.")
        latitude, longitude = _validate_location(
            location["latitude"], location["longitude"]
        )

        records = []
        for timestamp, elapsed, ephemeris_time in zip(
            timestamps, elapsed_hours, ephemeris_times
        ):
            position = earth_position(
                latitude, longitude, ephemeris_time, threshold
            )
            records.append({
                "datetime_utc": timestamp,
                "elapsed_hours": float(elapsed),
                **position,
            })

        dataframe = pd.DataFrame.from_records(records)
        elevations = dataframe["earth_elevation_deg"].to_numpy(dtype=float)
        windows = _communication_windows(dataframe, threshold)
        available_hours = _available_time_hours(timestamps, elevations, threshold)
        available_hours = min(total_period_hours, max(0.0, available_hours))
        unavailable_hours = total_period_hours - available_hours
        durations = [window["duration_hours"] for window in windows]

        summary = {
            "location_id": location_id,
            "latitude": latitude,
            "longitude": longitude,
            "start_date_utc": first_day.isoformat(),
            "end_date_utc": last_day.isoformat(),
            "number_of_samples": sample_count,
            "number_of_intervals": interval_count,
            "sampling_mode": "fixed_interval",
            "sample_interval_seconds": SAMPLE_INTERVAL_SECONDS,
            "sample_spacing_minutes": SAMPLE_INTERVAL_SECONDS / 60.0,
            "period_hours": total_period_hours,
            "minimum_elevation_deg": threshold,
            "communication_available_hours": available_hours,
            "communication_unavailable_hours": unavailable_hours,
            "communication_availability_pct": 100.0 * available_hours / total_period_hours,
            "number_of_windows": len(windows),
            "longest_window_hours": max(durations, default=0.0),
            "average_window_hours": float(np.mean(durations)) if durations else 0.0,
            "earth_elevation_max_deg": float(dataframe["earth_elevation_deg"].max()),
            "earth_elevation_mean_deg": float(dataframe["earth_elevation_deg"].mean()),
            "earth_moon_distance_mean_km": float(dataframe["earth_moon_distance_km"].mean()),
        }
        results[location_id] = {
            "data": dataframe,
            "summary": summary,
            "windows": windows,
        }

    return results
