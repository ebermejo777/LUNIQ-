#Malla de tiempo común para los calculos lunares.
from datetime import timedelta
import math
import numpy as np

SAMPLE_INTERVAL_SECONDS = 600
MAX_AUTOMATIC_SAMPLES = 100_000


def build_sampling_grid(start_datetime, end_datetime):
    
    #Genera puntos UTC desde inicio hasta fin, separados exactamente 600 s.
    #El instante final se incluye. Para conservar el intervalo fijo, la duracion debe ser un multiplo exacto de 600 segundos.
    
    total_seconds = (end_datetime - start_datetime).total_seconds()
    if not math.isfinite(total_seconds) or total_seconds <= 0:
        raise ValueError("El intervalo temporal debe tener duracion positiva.")

    interval_float = total_seconds / SAMPLE_INTERVAL_SECONDS
    interval_count = round(interval_float)
    if not math.isclose(interval_float, interval_count, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(
            f"La duracion debe ser multiplo de {SAMPLE_INTERVAL_SECONDS} segundos."
        )

    sample_count = interval_count + 1
    if sample_count > MAX_AUTOMATIC_SAMPLES:
        raise ValueError(
            f"La simulacion requiere {sample_count:,} puntos y supera el limite "
            f"de {MAX_AUTOMATIC_SAMPLES:,}. Reduzca el periodo."
        )

    offsets_seconds = np.arange(sample_count, dtype=np.int64) * SAMPLE_INTERVAL_SECONDS
    timestamps = [start_datetime + timedelta(seconds=int(offset))
                  for offset in offsets_seconds]
    return offsets_seconds, timestamps, interval_count
