import numpy as np

def Fv_Calculo_f(datos_tabla_vanos, Coord_descentramientos, p_tabla_tipo, n_hhcc, 
                tipo_pendolado, ro_hc, t_hc, t_hs, rel_comp, Ancho_via, Carril):
    """
    Calcula las fuerzas verticales (Fv) en los postes de la catenaria en función de varios parámetros.
    """
    
    datos_vanos = np.array(datos_tabla_vanos[:, 3], dtype=float)
    tipo_mensula = datos_tabla_vanos[:, 1]
    
    # Inicializamos péndolas y distancia a primera péndola
    num_pendolas = np.zeros(len(datos_vanos), dtype=int)
    dist_1pend = np.zeros(len(datos_vanos), dtype=float)
    
    # Función para asignar número de péndolas y distancia según tipo de pendolado
    def asignar_pendolas(vano, tipo):
        if tipo == 'CA-220':
            # Número de péndolas
            if vano >= 54.5: n = 16
            elif vano >= 47.5: n = 14
            elif vano >= 40: n = 12
            elif vano >= 33: n = 10
            elif vano >= 25.5: n = 8
            else: n = 6
            # Distancia primera péndola (simplificado rango principal)
            d = 5.2 if 50 <= vano <= 62 else 5.0
        elif tipo == 'CA-160':
            if vano >= 54.5: n = 18
            elif vano >= 48.5: n = 16
            elif vano >= 42: n = 14
            elif vano >= 36: n = 12
            elif vano >= 29.5: n = 10
            elif vano >= 19: n = 6
            else: n = 6
            d = 4.75
        else:  # 'Monforte' o 'Libre'
            if vano >= 59.4: n = 7
            elif vano >= 50: n = 6
            elif vano >= 42.5: n = 5
            elif vano >= 31: n = 4
            elif vano >= 21.5: n = 3
            else: n = 2
            d = 6.0 if vano >= 50 else 7.0 if vano >= 35 else 6.0
        return n, d

    # Vectorizamos la asignación de péndolas y distancia
    for i, vano in enumerate(datos_vanos):
        num_pendolas[i], dist_1pend[i] = asignar_pendolas(vano, tipo_pendolado)

    peraltes = p_tabla_tipo[:, 5]
    hhc = p_tabla_tipo[:, 11]  
    desc = -p_tabla_tipo[:, 10] 

    # Calcular beta y htt vectorizado
    beta = np.arcsin(peraltes / (Ancho_via + Carril).astype(float).view(np.float64).astype(complex))
    htt = np.where(p_tabla_tipo[:, 4] == 1, 
                   np.abs(hhc * np.cos(beta) + desc * np.sin(np.abs(beta))) + np.abs(peraltes)/2000,
                   np.abs(hhc * np.cos(beta) - desc * np.sin(np.abs(beta))) + np.abs(peraltes)/2000)

    # Coeficientes de tensiones verticales
    coef_izq = np.zeros(len(tipo_mensula))
    coef_der = np.zeros(len(tipo_mensula))
    coef_izq[1:] = (htt[1:] - htt[:-1]) / datos_vanos[:-1]
    coef_der[:-1] = (htt[:-1] - htt[1:]) / datos_vanos[:-1]
    Coeficientes = coef_izq + coef_der

    # Calculamos fuerzas verticales
    Fv_hc = np.zeros(len(tipo_mensula))
    Fv_hc[1:-1] = ro_hc * (dist_1pend[:-1]/2 + dist_1pend[1:]/2) + t_hc * Coeficientes[1:]

    return Fv_hc
