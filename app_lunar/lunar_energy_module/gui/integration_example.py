#Ejemplo para integrar con GUI
from calculations.energy_availability import calculate_energy_availability
from visualization.plots import create_comparison_plots


def run_calculation(selected_locations, start_date, end_date):
    return calculate_energy_availability(
        locations=selected_locations,
        start_date=start_date,
        end_date=end_date,
    )


def show_comparison(results):
    return create_comparison_plots(results, show=True)
