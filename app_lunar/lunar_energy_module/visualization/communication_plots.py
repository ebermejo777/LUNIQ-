#Gráfico comparativo posición de la tierra y disponibilidad de comunicación con la tierra para puntos seleccionados por latitud y longitud
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def create_communication_plots(results, show=True):
    if not results:
        raise ValueError("No hay resultados para graficar.")
    fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    fig.canvas.manager.set_window_title("Posición geométrica de la tierra")
    palette = plt.get_cmap("tab20")
    for index, (location_id, result) in enumerate(results.items()):
        color = palette(index % 20)
        df = result["data"]
        dates = df["datetime_utc"]
        axes[0].plot(dates, df["earth_elevation_deg"], color=color, label=location_id)
        axes[1].plot(dates, df["earth_moon_distance_km"], color=color, label=location_id)
        # Escalón binario para identificar los intervalos de visibilidad.
        axes[2].step(dates, df["communication_visible"], where="post", color=color, label=location_id)
    axes[0].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes[0].set_ylabel("Elevación de la Tierra (°)")
    axes[1].set_ylabel("Distancia Tierra-Luna (km)")
    axes[2].set_ylabel("Visibilidad (0/1)")
    axes[2].set_yticks([0, 1], ["No disponible", "Disponible"])
    axes[2].set_xlabel("Fecha y hora (UTC)")
    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize="small", ncol=2)
    locator = mdates.AutoDateLocator()
    axes[2].xaxis.set_major_locator(locator)
    axes[2].xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    first = next(iter(results.values()))["summary"]
    fig.suptitle(
        f"Comunicación geométrica con la Tierra | {first['start_date_utc']} a "
        f"{first['end_date_utc']} UTC",
        fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    if show:
        plt.show()
    return fig, axes
