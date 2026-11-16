# Kernels SPICE

Esta carpeta contiene los kernels de SPICE a utilizar

En el archivo `calculations/astronomical.py` se espera:
- `naif0012.tls` — leap seconds kernel (LSK).
- `de440s.bsp` — efemérides planetarias (SPK).
- `pck00011.tpc` — constantes y orientación planetaria (PCK).

La elección de los kernels está basada en la documentación de NAIF
https://naif.jpl.nasa.gov/naif/kernel_selection.html