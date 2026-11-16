#Interfaz para modelos de horizonte y sombras topográficas.
def visible_above_horizon(solar_elevation_deg, solar_azimuth_deg,
                          horizon_model=None):
    
    #Indica si el Sol está por encima del horizonte lunar.

    #horizon_model puede ser una función(azimuth_deg) -> elevación_horizonte_deg.
    #Si no se suministra, se usa horizonte plano de 0 grados.
    
    horizon_elevation = (
        float(horizon_model(float(solar_azimuth_deg)))
        if horizon_model is not None else 0.0
    )
    return float(solar_elevation_deg) > horizon_elevation
