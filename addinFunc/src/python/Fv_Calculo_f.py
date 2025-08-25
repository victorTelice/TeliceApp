import numpy as np
from utils.logger import Logger 
def Fv_Calculo_f(datos_tabla_vanos, Coord_descentramientos, p_tabla_tipo, n_hhcc, 
                tipo_pendolado, ro_hc, t_hc, t_hs, rel_comp, Ancho_via, Carril):
    """
    Calcula las fuerzas verticales (Fv) en los postes de la catenaria en función de varios parámetros.

    Parameters:
    - datos_tabla_vanos: Tabla con datos de los vanos
    - Coord_descentramientos: Coordenadas con los descentramientos (esta no la usa, no sé por qué la pasa)(la puse pq en matlab la pasaban)
    - p_tabla_tipo: Tabla con información del tipo de tramo
    - n_hhcc: Número de hilos de contacto
    - tipo_pendolado: Tipo de sistema de catenaria ('CA-220', 'CA-160', 'Monforte', 'Libre')
    - ro_hc: Densidad del hilo conductor
    - t_hc: Tensión del hilo conductor
    - t_hs: Tensión del hilo sustentador
    - rel_comp: Relación de compensación (se coge en la gui de seccionamientos)
    - Ancho_via: Ancho de vía
    - Carril: Ancho del carril

    Returns:
    - Fv_Calculo: Array de fuerzas verticales
    """
    Logger.add_to_log("llamada", "Llamada a la función Fv_Calculo_f")

    # Coge los tipos de mensula y los vanos
    tipo_mensula = datos_tabla_vanos[0::2, 1]
    datos_vanos = datos_tabla_vanos[:, 3]

    # esto no sé para que lo hace si no se usa, pero bueno en matlab estaba
    d_par = 0.5 if n_hhcc == 2 else 0
    
    # Inicializar numero de péndolas y distancia a la primera péndola
    num_pendolas = np.zeros(len(datos_vanos), dtype=np.int32)
    dist_1pend = np.zeros(len(datos_vanos), dtype=np.float32)

    ##estuve mirando a ver si encontraba algun patron de los intervalos de un tipo a otro o algo pero es que no parece tener ningun tipo de similitud
  
    ##refactor
    # --------------------------- CA-220 Pendola --------------------------- #
    if tipo_pendolado == 'CA-220':
        for i in range(1,len(datos_tabla_vanos), 2):
            vano = datos_vanos[i]
            
            # Number of pendulums
            if 54.5 <= vano <= 62:
                num_pendolas[i] = 16
            elif 47.5 <= vano < 54.5:
                num_pendolas[i] = 14
            elif 40 <= vano < 47.5:
                num_pendolas[i] = 12
            elif 33 <= vano < 40:
                num_pendolas[i] = 10
            elif 25.5 <= vano < 33:
                num_pendolas[i] = 8
            elif 0 <= vano < 25.5:
                num_pendolas[i] = 6

            
            # Distancia a la primera péndola
            if (62 >= vano > 61.5) or (58.5 >= vano > 58) or (55 >= vano > 54.5) or \
               (50.5 >= vano > 50) or (49 >= vano > 48.5) or (47.5 >= vano > 47) or \
               (38.5 >= vano > 38) or (36.5 >= vano > 36) or (34.5 >= vano > 34) or \
               (32.5 >= vano > 32) or (31 >= vano > 30.5) or (29.5 >= vano > 29) or \
               (28 >= vano > 27.5) or (24.5 >= vano > 24) or (23.5 >= vano > 23) or \
               (22.5 >= vano > 22) or (53.5 >= vano > 53):
                dist_1pend[i] = 5.2
            elif (61.5 >= vano > 61) or (58 >= vano > 57.5) or (54.5 >= vano > 54) or \
                 (52.5 >= vano > 52) or (49.5 >= vano > 49) or (39.5 >= vano > 39):
                dist_1pend[i] = 5.3
            elif (61 >= vano > 60.5) or (57.5 >= vano > 57):
                dist_1pend[i] = 5.4
                
            elif (60.5 >= vano > 60) or (57 >= vano > 56.5) or (54 >= vano > 53.5) or \
                 (51 >= vano > 50.5) or (48 >= vano > 47.5) or (38 >= vano > 37.5) or \
                 (36 >= vano > 35.5) or (34 >= vano > 33.5) or (31.5 >= vano > 31) or \
                 (30 >= vano > 29.5) or (28.5 >= vano > 28) or (25.5 >= vano > 25) or \
                 (23 >= vano > 22.5):
                dist_1pend[i] = 5.15
                
            elif (60 >= vano > 59.5) or (56.5 >= vano > 56) or (53 >= vano > 52.5) or \
                 (51.5 >= vano > 51) or (50 >= vano > 49.5) or (48.5 >= vano > 48) or \
                 (47 >= vano > 39.5) or (39 >= vano > 38.5) or (37 >= vano > 36.5) or \
                 (35 >= vano > 34.5) or (32 >= vano > 31.5) or (30.5 >= vano > 30) or \
                 (27.5 >= vano > 27) or (25 >= vano > 24.5) or (24 >= vano > 23.5) or \
                 (22 >= vano > 21.5) or (33 >= vano > 29.5):
                dist_1pend[i] = 5.25
            
            elif (59.5 >= vano > 59) or (52 >= vano > 51.5):
                dist_1pend[i] = 5.35
            elif (59 >= vano > 58.5) or (55.5 >= vano > 55) or (37.5 >= vano > 37) or \
                 (35.5 >= vano > 35) or (33.5 >= vano > 33) or (29 >= vano > 28.5) or \
                 (26 >= vano > 25.5) or (21.5 >= vano > 21):
                dist_1pend[i] = 5.1
            elif (56 >= vano > 55.5) or (27 >= vano > 26.5):
                dist_1pend[i] = 5
            elif (26.5 >= vano > 26) or (57.5 >= vano > 57):
                dist_1pend[i] = 5.05
            elif (21 >= vano > 20.5):
                dist_1pend[i] = 4.85
            elif (20.5 >= vano > 20):
                dist_1pend[i] = 4.8
            elif (20 >= vano >= 0):
                dist_1pend[i] = 4.75
    # --------------------------- CA-160 Péndola --------------------------- #
    if tipo_pendolado == 'CA-160':
    # Número de péndolas
        for i in range(1,len(datos_tabla_vanos),2):
            vano = datos_vanos[i]
            
            if 54.5 <= vano <= 62:
                num_pendolas[i] = 18
            elif 48.5 <= vano < 54.5:
                num_pendolas[i] = 16
            elif 42 <= vano < 48.5:
                num_pendolas[i] = 14
            elif 36 <= vano < 42:
                num_pendolas[i] = 12
            elif 29.5 <= vano < 36:
                num_pendolas[i] = 10
            elif 23.5 <= vano < 29.5:
                num_pendolas[i] = 8
            elif 0 <= vano < 23.5:
                num_pendolas[i] = 6
           
            # Distancia primera péndola al apoyo
            if (61.5 < vano <= 62 or 59.5 < vano <= 60 or 57.5 < vano <= 58 or
                55.5 < vano <= 56 or 51.5 < vano <= 52 or 48 <= vano < 48.5 or
                47.5 < vano <= 47.5 or 45.5 < vano <= 46 or 42.5 < vano <= 43 or
                35.5 < vano <= 41.5 or 33.5 < vano <= 34 or 32.5 < vano <= 33 or
                31.5 < vano <= 32 or 30.5 < vano <= 31 or 29.5 < vano <= 30 or
                28 < vano <= 29.5 or 26 < vano <= 27.5 or 24.5 < vano <= 25 or
                22 < vano <= 19 or 19 <= vano <= 0 or 43 < vano <= 43.5):
                dist_1pend[i] = 4.75
            elif (58 < vano <= 60.5 or 56 < vano <= 58.5 or 53 < vano <= 53.5 or
                49.5 <= vano < 50 or 45 <= vano < 45.5 or 42 <= vano < 42.5 or
                29 <= vano < 29.5 or 27 <= vano < 27.5 or 22 <= vano < 22.5):
                dist_1pend[i] = 4.8
            elif (50.5 <= vano < 51.5 or 45 <= vano < 45.5 or 22.5 <= vano < 23 or
                44 <= vano < 44.5 or 45.5 <= vano < 46):
                dist_1pend[i] = 4.85
            elif (59 <= vano < 59.5 or 57 <= vano < 57.5 or 55 <= vano < 55.5 or
                50 <= vano < 50.5 or 48.5 <= vano < 49 or 47 <= vano < 47.5 or
                46 <= vano < 46.5 or 43 <= vano < 43.5 or 35 <= vano < 35.5 or
                34 <= vano < 34.5 or 32 <= vano < 32.5 or 33 <= vano < 33.5 or
                31 <= vano < 31.5 or 30 <= vano < 30.5 or 28 <= vano < 28.5 or
                26.5 <= vano < 27 or 25 <= vano < 25.5 or 24 <= vano < 24.5 or
                42 <= vano < 42.5 or 53.5 <= vano < 54 or 30 <= vano < 30.5):
                dist_1pend[i] = 4.7
            elif (58.5 < vano <= 59 or 54.5 < vano <= 55 or 52 <= vano < 52.5 or
                48.5 <= vano < 49 or 46.5 <= vano < 47 or 43.5 <= vano < 44 or
                35 < vano <= 35.5 or 26 <= vano < 26.5 or 24 < vano <= 24.5 or
                56.5 <= vano < 57):
                dist_1pend[i] = 4.65
            elif 49 <= vano < 49.5 or 52.5 <= vano < 53:
                dist_1pend[i] = 4.9
            elif 44 <= vano < 44.5 or 23 <= vano < 23.5 or 54 < vano <= 54.5:
                dist_1pend[i] = 4.6
            elif 50.5 <= vano < 51:
                dist_1pend[i] = 4.95


    # --------------------------- Monforte péndola y Libre --------------------------- #
    if tipo_pendolado == 'Monforte' or tipo_pendolado == 'Libre':
    # Número de péndolas
        for i in range(1,len(datos_tabla_vanos),2):
            vano = datos_vanos[i]
            
            if 59.4 <= vano <= 62:
                num_pendolas[i] = 7
            elif 50.0 <= vano < 59.4:
                num_pendolas[i] = 6
            elif 42.5 <= vano < 50.0:
                num_pendolas[i] = 5
            elif 31.0 <= vano < 42.5:
                num_pendolas[i] = 4
            elif 21.5 <= vano < 31.0:
                num_pendolas[i] = 3
            elif 0 <= vano < 21.5:
                num_pendolas[i] = 2
            
            # Distancia primera péndola al apoyo
            if 50 <= vano < 62 or 0 <= vano < 35:
                dist_1pend[i] = 6.00
            elif 35 <= vano < 50:
                dist_1pend[i] = 7.00

    # Convert péndula data to arrays
    Pendolado_Calculo = np.column_stack((
        num_pendolas, dist_1pend
    ))
    
    #Cogemos los datos que nos interesan

    dist_1pend = Pendolado_Calculo[1::2, 1] 
    peraltes = p_tabla_tipo[:, 5]
    hhc = p_tabla_tipo[:, 11]  
    desc = -p_tabla_tipo[:, 10]
    datos_vanos=datos_tabla_vanos[1:-1:2,3]
    
    valor = peraltes/ (Ancho_via + Carril)
    beta = np.arcsin(valor.astype(complex))

    htt = np.where(p_tabla_tipo[:, 4] == 1, 
                   np.abs(hhc * np.cos(beta) + desc * np.sin(np.abs(beta))) + np.abs(peraltes) / 2000, 
                   np.abs(hhc * np.cos(beta) - desc * np.sin(np.abs(beta))) + np.abs(peraltes) / 2000)
    #htt= htt[0]
    # Calcular coeficientes de tensiones verticales
    Coeficientes_tensiones_verticales = np.zeros((len(tipo_mensula), 2))
    aux1= (htt[1:] - htt[:-1])
    
        # Coeficiente izquierdo
    for i in range(1, len(tipo_mensula)):  # en Python empieza en 1 (MATLAB = 2)
        Coeficientes_tensiones_verticales[i, 0] = (
            (htt[i] - htt[i-1]) / datos_vanos[i-1]
        )

    # Coeficiente derecho
    for i in range(0, len(tipo_mensula)-1):  # MATLAB = 1:size-1
        Coeficientes_tensiones_verticales[i, 1] = (
            (htt[i] - htt[i+1]) / datos_vanos[i]
        )



    Coeficientes = np.sum(Coeficientes_tensiones_verticales, axis=1)
    
    # Calculamos las fuerzas verticales
    Fv_hc = np.zeros(len(tipo_mensula)-2, dtype=np.float32)
    

    for i in range(len(tipo_mensula) - 2):
        Fv_hc[i] = (ro_hc * (dist_1pend[i]/2 + dist_1pend[i+1]/2)) + t_hc * Coeficientes[i+1]
    
    Fv_hc = np.concatenate(([0], Fv_hc, [0]))
    # Ajustar fuerzas según tipo de mensula
    for i in range(len(tipo_mensula)):
        if tipo_mensula[i] == 'Anclaje': 
            Fv_hc[i] = (t_hc + t_hs) / rel_comp
        elif tipo_mensula[i] == 'Elevación':  
            Fv_hc[i+1] = ro_hc * (dist_1pend[i-1]/2 + dist_1pend[i]/2)
            Fv_hc[i-1] = ro_hc * (dist_1pend[i-1]/2 + dist_1pend[i]/2)

    # Devolver el resultado
    return Fv_hc.reshape(-1, 1)  # Devolvemos como un array columna