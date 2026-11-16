#Gráfico comparativo Irración solar y disponiblidad energética entre puntos seleccionados por latitud y longitud
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def _cumulative_energy(dataframe):
    x = dataframe["elapsed_hours"].to_numpy(dtype=float)
    y = dataframe["irradiance_W_m2"].to_numpy(dtype=float)
    cumulative = np.zeros(len(y), dtype=float)
    if len(y) > 1:
        cumulative[1:] = np.cumsum((y[1:] + y[:-1]) * 0.5 * np.diff(x))
    return cumulative / 1000.0


def create_comparison_plots(results, show=True):
    #Elevación, irradiancia y energía acumulada para todas los puntos seleccionados
    if not results:
        raise ValueError("No hay resultados para graficar.")

    fig, axes = plt.subplots(3, 1, figsize=(13, 10), sharex=True)
    fig.canvas.manager.set_window_title("Energía Solar")
    palette = plt.get_cmap("tab20")
    location_ids = list(results)

    for index, location_id in enumerate(location_ids):
        color = palette(index % 20)
        df = results[location_id]["data"]
        dates = df["datetime_utc"]
        axes[0].plot(dates, df["solar_elevation_deg"], color=color, label=location_id)
        axes[1].plot(dates, df["irradiance_W_m2"], color=color, label=location_id)
        axes[2].plot(dates, _cumulative_energy(df), color=color, label=location_id)

    axes[0].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes[0].set_ylabel("Elevación solar (°)")
    axes[1].set_ylabel("Irradiancia (W/m²)")
    axes[2].set_ylabel("Energía acumulada (kWh/m²)")
    axes[2].set_xlabel("Fecha y hora (UTC)")

    for ax in axes:
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize="small", ncol=2)

    locator = mdates.AutoDateLocator()
    axes[2].xaxis.set_major_locator(locator)
    axes[2].xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    first = results[location_ids[0]]["summary"]
    fig.suptitle(
        f"Comparación de ubicaciones lunares | {first['start_date_utc']} a "
        f"{first['end_date_utc']} UTC",
        fontsize=13
    )
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    if show:
        plt.show()
    return fig, axes


def create_comparison_plot(results, metric="energy_kWh_m2", show=True):
    labels = list(results)
    values = [results[key]["summary"][metric] for key in labels]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(labels, values)
    ax.set_ylabel(metric)
    ax.set_title(f"Comparación entre ubicaciones: {metric}")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    if show:
        plt.show()
    return fig, ax
