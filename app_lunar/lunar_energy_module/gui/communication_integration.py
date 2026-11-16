#Funciones para la integración de cálculo en GUI
from calculations.earth_communication import calculate_earth_communication
from visualization.communication_plots import create_communication_plots


def run_communication_calculation(selected_locations, start_date, end_date,
                                  minimum_elevation_deg=0.0):
    return calculate_earth_communication(
        locations=selected_locations,
        start_date=start_date,
        end_date=end_date,
        minimum_elevation_deg=minimum_elevation_deg,
    )


def show_communication_comparison(results):
    return create_communication_plots(results, show=True)
