#Prueba en consola disponibilidad energética.
from pathlib import Path
from calculations import load_kernels, calculate_energy_availability
from visualization.plots import create_comparison_plots

BASE_DIR = Path(__file__).resolve().parent
KERNEL_DIR = BASE_DIR / "data" / "ephemeris"

if __name__ == "__main__":
    load_kernels(KERNEL_DIR)
    locations = [
        {"id": "Punto_01", "latitude": -89.5, "longitude": 120.0},
        {"id": "Punto_02", "latitude": -88.8, "longitude": 45.0},
        {"id": "Punto_03", "latitude": 4.8, "longitude": 90.0},
    ]
    results = calculate_energy_availability(
        locations=locations,
        start_date="2026-11-15",
        end_date="2026-12-31",
    )
    print("\\nRESUMEN DEL PERIODO")
    for location_id, result in results.items():
        print(f"\\n{location_id}")
        for key, value in result["summary"].items():
            print(f"  {key}: {value}")
    create_comparison_plots(results, show=True)
