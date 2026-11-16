# Lunar Energy Availability

## Instalación
```powershell
python -m pip install -r requirements.txt
```
## Ejecución
Configure fechas y coordenadas en `main.py` y ejecute:
```powershell
python main.py
```

## Integración GUI
```python
from gui.integration_example import run_calculation, show_comparison

results = run_calculation(
    selected_locations=[
        {"id": "Punto_01", "latitude": -89.5, "longitude": 120.0},
        {"id": "Punto_02", "latitude": -88.8, "longitude": 45.0},
    ],
    start_date="2026-11-14",
    end_date="2026-11-20",
)
show_comparison(results)
```

La fecha final incluye el día completo; la última muestra es 23:59:59 UTC.
La duración de iluminación se estima integrando el indicador en las muestras.
Supuestos: Luna esférica, normal radial, horizonte plano de 0°, sin sombras
topográficas, sin atmósfera y sin eficiencia fotovoltaica.


# Lunar Earth Communication

## Módulo de comunicación con la Tierra
- Evalúa la posición topocéntrica de la Tierra desde cada ubicación lunar.
- Calcula elevación, azimut y distancia Tierra-Luna.
- Determina visibilidad geométrica con una máscara mínima de elevación configurable (0° por defecto).
- Calcula disponibilidad porcentual, horas disponibles/no disponibles y ventanas de comunicación.
- Ajusta automáticamente el número de muestras a la duración del intervalo: mantiene una densidad de referencia de las muestras por cada 24 horas.
- Permite fijar manualmente `number_of_samples` cuando se necesita controlar la resolución; el modo automático tiene un límite de seguridad de 100.000 muestras.
- Genera gráficas comparativas de elevación, distancia y visibilidad.

### Ejecución
Desde la carpeta del proyecto:
```powershell
python main_communication.py
```

### Integración en otra interfaz
```python
from calculations import load_kernels, calculate_earth_communication
from visualization.communication_plots import create_communication_plots

load_kernels("data/ephemeris")
results = calculate_earth_communication(
    locations=[{"id": "Base_A", "latitude": -89.5, "longitude": 120.0}],
    start_date="2026-11-15",
    end_date="2026-11-20",
    minimum_elevation_deg=5.0,
)
create_communication_plots(results)
```

### Supuestos y alcance
La disponibilidad calculada es geométrica: el centro de la Tierra debe superar la elevación mínima configurada. No modela potencia transmitida, antenas, frecuencia, pérdidas, ruido, modulación, capacidad de datos ni estaciones repetidoras. La superficie lunar se representa mediante el elipsoide de referencia del kernel PCK. Las coordenadas de entrada son planetocéntricas; la dirección local Arriba se obtiene a partir de la normal al elipsoide. No se incluyen obstrucciones topográficas locales. La disponibilidad y los extremos de las ventanas se calculan con interpolación lineal de los cruces de la elevación respecto a la máscara configurada. En modo automático se utilizan 512 muestras por día de intervalo (con un máximo de 100.000); para fijar una cantidad concreta, indique `number_of_samples` en `calculate_earth_communication`. La precisión temporal depende de la resolución y debe comprobarse mediante un análisis de convergencia antes de utilizar los resultados en una planificación operativa.
