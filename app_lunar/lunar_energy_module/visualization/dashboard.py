# Dashboard para comparación
from .plots import create_comparison_plots


def create_dashboard(results, show=True):
    return create_comparison_plots(results, show=show)
