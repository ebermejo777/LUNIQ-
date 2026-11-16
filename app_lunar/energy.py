"""Ejecución de prueba desde consola."""
from pathlib import Path
from lunar_energy_module.calculations import load_kernels, calculate_energy_availability
from lunar_energy_module.visualization.plots import create_comparison_plots

BASE_DIR = Path(__file__).resolve().parent
KERNEL_DIR = BASE_DIR/"lunar_energy_module" / "data" / "ephemeris"

load_kernels(KERNEL_DIR)

class energia():
	def __init__(self, punto_1, punto_2, punto_3, fecha_inicio, fecha_final):
		locations = [
			{"id": "Punto_01", "latitude": punto_1[1], "longitude": punto_1[0]},
			{"id": "Punto_02", "latitude": punto_2[1], "longitude": punto_2[0]},
			{"id": "Punto_03", "latitude": punto_3[1], "longitude": punto_3[0]},
		]
		self.results = calculate_energy_availability(
			locations=locations,
			start_date=fecha_inicio,
			end_date=fecha_final,
		)
	def datos(self):
		print("\\nRESUMEN DEL PERIODO")
		for location_id, result in self.results.items():
			print(f"\\n{location_id}")
			for key, value in result["summary"].items():
				print(f"  {key}: {value}")
	def grafica(self):
		create_comparison_plots(self.results, show=True)