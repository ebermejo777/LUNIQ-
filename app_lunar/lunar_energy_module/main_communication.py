#Prueba en consola del módulo de comunicación con la Tierra.
from pathlib import Path
from calculations import load_kernels
from calculations.earth_communication import calculate_earth_communication
from visualization.communication_plots import create_communication_plots

BASE_DIR = Path(__file__).resolve().parent
KERNEL_DIR = BASE_DIR / "data" / "ephemeris"

if __name__ == "__main__":
    load_kernels(KERNEL_DIR)
    locations = [
        {"id": "Punto_01", "latitude": -89.5, "longitude": 120.0},
        {"id": "Punto_02", "latitude": -88.8, "longitude": 45.0},
        {"id": "Punto_03", "latitude": 4.8, "longitude": 90.0},
    ]
    results = calculate_earth_communication(
        locations=locations,
        start_date="2026-11-15",
        end_date="2026-12-31",
        minimum_elevation_deg=0.0,
        # number_of_samples=None activa el muestreo automático según el periodo.
    )
    print("\nRESUMEN DE COMUNICACIÓN CON LA TIERRA")
    for location_id, result in results.items():
        print(f"\n{location_id}")
        for key, value in result["summary"].items():
            print(f"  {key}: {value}")
        print("  ventanas:")
        for window in result["windows"]:
            print(f"    {window['start_utc']} -- {window['end_utc']} "
                  f"({window['duration_hours']:.2f} h)")
    create_communication_plots(results, show=True)
