import numpy as np
import math
import scipy.io as sio
from scipy.optimize import fsolve
from scipy.io import loadmat
import warnings
from typing import Tuple, List, Dict, Any
import os
import Calcular_Seccionamiento_f
from utils.logger import Logger 


# Funcion auxiliar que aplana dimensiones para arrays sobredivididos
def aplanar_varias_veces(array, veces):
    resultado = array
    for _ in range(veces):
        resultado = [item for subarray in resultado for item in subarray]
    return resultado


# Función auxiliar para obtener medida o None si no se encuentra
def obtener_medida(medidas_herrajes_mensula, herrajes_mensula, referencia):
    indices = np.where([h == referencia for h in herrajes_mensula])[0]
    if indices.size > 0:  # Si hay coincidencias
        return (medidas_herrajes_mensula[indices[0]][0][0]).astype(np.float64)  # Retorna la primera medida encontrada
    return None  # Si no hay coincidencias

##Funcion principal
def Mensulas_Calculo_f(
    datos_tabla_vanos,
    Fhc_Calculo,
    tabla_datos_topografia,
    t_hs,
    ro_hs,
    t_hc,
    ro_hc,
    Ancho_via,
    Carril,
    biblioteca_escogida_cat,
    datos_tabla_tramos,
    npuntos,
    Coord_trazado,
    n_hhcc,
    tipo_pendolado,
    rel_comp
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Función principal que calcula las ménsulas y sus coordenadas.
    
    Parámetros:
    - datos_tabla_vanos: Tabla de los datos de los vanos. 
    - Fhc_Calculo: Tabla con tres columnsas: nombre del poste, fuerza radial y fuerza vertical.
    - tabla_datos_topografia: Datos topográficos de los postes. 
    - t_hs, ro_hs, t_hc, ro_hc: Parámetros de tensión y densidad de los conductores 
    - Ancho_via, Carril: Dimensiones de la vía. 
    - biblioteca_escogida_cat: Ruta a la biblioteca de herrajes_catenaria. 
    - datos_tabla_tramos: Datos de los tramos. 
    - np: Número de puntos. 
    - Coord_trazado: Coordenadas del trazado. 
    - n_hhcc: Número de hilos de contacto. 
    - tipo_pendolado: Tipo de pendolado. 
    - rel_comp: Relación de compensación. 
    
    Returns
    - Mensulas_Calculo: Matriz con los cálculos de las ménsulas.
    - Coord_Mensulas_Calculo: Coordenadas de las ménsulas.
    """
    
    Logger.add_to_log("llamada", "Llamada a la función Mensulas_Calculo_f")

    # -----------------------Datos que se ven en la tabla del GUI------------------------------------------%
    # Número de poste
    datos_postes = datos_tabla_vanos[::2, 0]  # matriz con los nombres de los postes (solo los impares)
    
    # Datos
    tipo_poste = tabla_datos_topografia[:, 1].flatten()
    tipologia_men = tabla_datos_topografia[:, 2].flatten()
    lado_poste = tabla_datos_topografia[:, 3].flatten()
    giros_men = tabla_datos_topografia[:, 4].flatten()
    datos_desc = tabla_datos_topografia[:, 5].astype(float).flatten() * -10  # en mm (Para que haga el cálculo de las coordenadas de los descentramientos bien)
    datos_alt = tabla_datos_topografia[:, 6].astype(float).flatten()  # en mm
    alt_cat = tabla_datos_topografia[:, 7].astype(float).flatten()
    nombre_men = tabla_datos_topografia[:, 8].flatten() # Nombre de la biblioteca de la ménsula
    galibo = tabla_datos_topografia[:, 9].astype(float).flatten()
    ht = tabla_datos_topografia[:, 10].astype(float).flatten()
    peralte = tabla_datos_topografia[:, 11].astype(float).flatten()
    alt_GM = tabla_datos_topografia[:, 12].astype(float).flatten()
    dist_giros = tabla_datos_topografia[:, 13].astype(float).flatten()
    despl = tabla_datos_topografia[:, 14].astype(float).flatten()
    tipo_brazo = tabla_datos_topografia[:, 15].flatten()
    p_brazo_sup = tabla_datos_topografia[:, 16].astype(float).flatten()
    ang_brazo = tabla_datos_topografia[:, 17].astype(float).flatten()
    
    # Brazos
    l_brazo = np.zeros(len(datos_postes), dtype=float)
    brazo_mensula_biblio = []
    for i in range(len(datos_postes)):
        ruta=os.path.join('Bibliotecas', 'Brazos de atirantado', tipo_brazo[i])
        brazo_data = sio.loadmat(ruta)  # Cargar datos del brazo
        brazo_mensula_biblio.append(brazo_data)
        l_brazo[i] = float(brazo_data['datos'][0, 0])  # El primer número siempre es la longitud
    
    # Se vuelve a calcular las coordenadas por si cambia algún descentramiento o alturas
    datos_vanos = np.concatenate((np.array([0]), datos_tabla_vanos[1:-1:2, 3]))  # lo vuelvo a coger de la tabla de vanos 
    pki = float( datos_tabla_vanos[0, 2] * 1000 ) #  pks de postes en m
    
    # Llamada a la función Seccionamientos_Calculo_f 
    Coord_seccionamientos_eje, vectores_normal, p_tabla_tipo, Coord_descentramientos, Fr_Calculo, Fv_Calculo = Calcular_Seccionamiento_f.Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, Ancho_via, Carril)

    Fr_hc = Fr_Calculo
    Fv_hc = Fv_Calculo
    
    Fhc_Calculo=np.column_stack((
        datos_postes, Fr_hc, Fv_hc
    ))

    # Tipo de ménsula
    tipo_men = np.empty(len(datos_postes), dtype=object)
    for i in range(len(datos_postes)):
        if (tipologia_men[i] == 'Vía General' and Fr_hc[i] > 0 and lado_poste[i] == 'Derecha') or ( tipologia_men[i] == 'Vía General' and Fr_hc[i] < 0 and lado_poste[i] == 'Izquierda'):
            tipo_men[i] = 'B1'
        elif (tipologia_men[i] == 'Vía General' and Fr_hc[i] > 0 and lado_poste[i] == 'Izquierda') or ( tipologia_men[i] == 'Vía General' and Fr_hc[i] < 0 and lado_poste[i] == 'Derecha'):
            tipo_men[i] = 'B2'
        elif tipologia_men[i] == 'Elevación':
            tipo_men[i] = 'Elevación'
        elif tipologia_men[i] == 'Anclaje':
            tipo_men[i] = 'No hay ménsula'
    
    # Sumando el semipeso del brazo a la Fv
    p_brazo = np.zeros(len(datos_postes))
    for i in range(len(datos_postes)):
        t_b = brazo_mensula_biblio[i]['tipo'][0][0]  # 1=Recto 2=Quebrado 3=Curvo
        if tipo_men[i] in ['B1', 'B2']:
            if t_b in [1, 3]:
                p_brazo[i] = float(brazo_mensula_biblio[i]['datos'][6])  # peso brazo
            else:
                p_brazo[i] = float(brazo_mensula_biblio[i]['datos'][9] ) # peso brazo
            Fv_hc[i] += p_brazo[i] / 2
    # Elevación del brazo en mm
    beta_virgen = np.abs(np.arctan(Fv_hc / Fr_hc)) * 360 / (2 * np.pi)  # ángulo brazos en grados sin retocar
    
    # Rendimiento del brazo
    Eta = np.zeros(len(datos_postes))
    ang_brazo_rad = ang_brazo * np.pi / 180
    for i in range(len(datos_postes)):
        ruta=os.path.join('Bibliotecas', 'Tipos de Ménsulas', nombre_men[i])
        herrajes_data = sio.loadmat(ruta)
        if tipo_men[i] == 'B1':
            parametros_b1 = herrajes_data['parametros_b1']
            beta_max = parametros_b1[8]  # angulo máx. del brazo
            if ang_brazo_rad[i] > 0:
                beta_virgen[i] = ang_brazo_rad[i]
            elif beta_virgen[i] > beta_max:
                beta_virgen[i] = beta_max * np.pi / 180
            else:
                beta_virgen[i] = beta_virgen[i] * np.pi / 180
            Eta[i] = np.abs(np.tan(beta_virgen[i]) * Fr_hc[i] / Fv_hc[i]) * 100
        elif tipo_men[i] == 'B2':
            parametros_b2 = herrajes_data['parametros_b2']
            beta_max = parametros_b2[8]  # angulo máx. del brazo
            if ang_brazo_rad[i] > 0:
                beta_virgen[i] = ang_brazo_rad[i]
            elif beta_virgen[i] > beta_max:
                beta_virgen[i] = beta_max * np.pi / 180
            else:
                beta_virgen[i] = beta_virgen[i] * np.pi / 180
            Eta[i] = np.abs(np.tan(beta_virgen[i]) * Fr_hc[i] / Fv_hc[i]) * 100
        elif tipo_men[i] == 'Vertical':
            parametros_vertical = herrajes_data['parametros_vertical']
            beta_max = parametros_vertical[0, 3]  # angulo máx. del brazo
            if beta_virgen[i] > beta_max:
                beta_virgen[i] = beta_max * np.pi / 180
            else:
                beta_virgen[i] = beta_virgen[i] * np.pi / 180
            Eta[i] = np.abs(np.tan(beta_virgen[i]) * Fr_hc[i] / Fv_hc[i]) * 100
        elif tipo_men[i] == 'Elevación':
            Eta[i] = 0
        elif tipo_men[i] == 'No hay ménsula':
            Eta[i] = 0
    
    # Preparar datos de salida
    tipo_men = np.array(tipo_men).reshape(-1, 1)
    Fr_hc = Fr_hc.reshape(-1, 1)
    Fv_hc = Fv_hc.reshape(-1, 1)
    Fr_hs = Fr_hc * (t_hs / t_hc)
    Fv_hs = Fv_hc * (ro_hs / ro_hc)
    beta_virgen = (beta_virgen * 360 / (2 * np.pi)).reshape(-1, 1)
    Eta = Eta.reshape(-1, 1)
    
    Mensulas_Calculo = np.hstack((
        datos_postes.reshape(-1, 1),
        tipo_men,
        Fr_hc,
        Fv_hc,
        beta_virgen,
        Eta,
        Fr_hs,
        Fv_hs
    ))
    
    # ------------------------Cálculo de las Coordenadas de las Ménsulas-----------------------------------------%
    datos_desc = tabla_datos_topografia[:, 5].astype(float) * 10  # lo tengo que volver a hacer aquí porque en la primera cambian el signo para que haga el cálculo de las coordenadas bien
    
    
    
    Fr_hc = Fhc_Calculo[:, 1].astype(float)
    Fv_hc = Fhc_Calculo[:, 2].astype(float)
    
    # -----------------MÉNSULAS TUBULARES TIPO ALTA VELOCIDAD-----------------%
    # herrajes catenaria
    #ruta=os.path.join('Bibliotecas', 'Herrajes de catenaria', biblioteca_escogida_cat)
    biblioteca_cat = sio.loadmat(biblioteca_escogida_cat)
    medidas_herrajes_catenaria = biblioteca_cat['medidas_herrajes_catenaria']
    herrajes_catenaria = biblioteca_cat['herrajes_catenaria']
    
    Coord_Mensulas_Calculo = np.zeros((52, 2 * len(datos_postes)), dtype=complex)  # CAMBIAR SI CAMBIA EL NÚMERO DE PUNTOS
    
    for i in range(len(datos_postes)):
        if lado_poste[i] == 'Izquierda':
            datos_desc[i] = -datos_desc[i]  # para que haga el calculo bien
            peralte[i] = -peralte[i]  # NO LO SE
        
        # ----------------------------------------------------------------------------B1----------------------------------------------------------------------------%
        if tipo_men[i] == 'B1':
            # Cargar las bibliotecas de las menulas individualmente
            ruta=os.path.join('Bibliotecas','Tipos de Ménsulas',nombre_men[i])
            herrajes_data = sio.loadmat(ruta)
            grapas_b1 =herrajes_data['grapas_b1']
            terminales_b1 = herrajes_data['terminales_b1']
            parametros_b1 = aplanar_varias_veces(herrajes_data['parametros_b1'],3)
            otrosherrajes_b1 = herrajes_data['otrosherrajes_b1']
            medidas_herrajes_mensula = herrajes_data['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_data['herrajes_mensula']
            
            # Extraer medidas de herrajes
            brazo_supsa = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b1[4])
            supsa = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b1[3])
            ais_tir = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b1[0])
            ais_men = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b1[1])

            # Obtener parámetros
            cota_fija_4 = parametros_b1[3]
            cota_fija_1 = parametros_b1[0]
            cota_fija_2 = parametros_b1[1]
            cota_fija_3 = parametros_b1[2]
            cota_fija_5 = parametros_b1[4]
            cota_fija_6 = parametros_b1[5]
            cota_fija_7 = parametros_b1[6]
            cota_seguridad_1 = parametros_b1[9]
            cota_seguridad_2 = parametros_b1[10]
            beta_max = parametros_b1[8] * np.pi / 180
            sigma = parametros_b1[7] * np.pi / 180

            # Obtener grapas
            grapa_men_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[1])
            grapa_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[2])
            grapa_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[3])
            grapa_u_tirmen = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[0])
            grapa_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[5])
            grapa_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b1[4])

            # Obtener terminales
            terminal_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[0])
            terminal_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[1])
            terminal_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[2])
            terminal_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[3])
            terminal_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[4])
            terminal_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b1[5])

            # Obtener BS
            BS = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, otrosherrajes_b1[2])

            # Obtener medidas de giros
            giros_simple_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GM')
            giros_simple_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GT')
            giros_doble_GM_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1200')
            giros_doble_GT_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1200')
            giros_doble_GM_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1500')
            giros_doble_GT_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1500')
            rot_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GM')
            rot_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GT')
            
            if giros_men[i] == 'Simple':
                d_giro_men = giros_simple_GM
                d_giro_tir = giros_simple_GT
            elif giros_men[i] == 'Doble 1200':
                d_giro_men = giros_doble_GM_1200
                d_giro_tir = giros_doble_GT_1200
            elif giros_men[i] == 'Doble 1500':
                d_giro_men = giros_doble_GM_1500
                d_giro_tir = giros_doble_GT_1500
            
            d_rot_men = rot_GM
            d_rot_tir = rot_GT
            
            # Cargar datos del poste
            ruta=os.path.join('Bibliotecas','Postes', tipo_poste[i])
            poste_data = sio.loadmat(ruta)
            Lposte = poste_data['h'][0, 0]
            binf = poste_data['h0'][0, 0]
            bsup = poste_data['h1'][0, 0]
            
            # Cargar datos del brazo
            ruta=os.path.join('Bibliotecas','Brazos de atirantado', tipo_brazo[i])
            brazo_data = sio.loadmat(ruta)
            t_b = brazo_data['tipo'][0, 0]  # 1=Recto 2=Quebrado 3=Curvo
            if t_b == 1:
                a = brazo_data['datos'][0][0]  # Lbrazo
                b = brazo_data['datos'][1][0] # cota2
                c = brazo_data['datos'][2][0]  # cota3
                d = brazo_data['datos'][3][0] * np.pi / 180  # angulo4
                e = brazo_data['datos'][4][0] * np.pi / 180  # angulo5
                f = brazo_data['datos'][5][0] * np.pi / 180  # angulo6
            elif t_b == 2:
                a = brazo_data['datos'][0][0]  # Lbrazo
                b = brazo_data['datos'][1][0]  # cota2
                c = brazo_data['datos'][2][0]  # cota3
                d = brazo_data['datos'][5][0] * np.pi / 180  # angulo4
                e = brazo_data['datos'][6][0] * np.pi / 180  # angulo5
                f = brazo_data['datos'][7][0] * np.pi / 180  # angulo6
                g = brazo_data['datos'][3][0] # cota4
                h = brazo_data['datos'][4][0]  # cota5
            elif t_b == 3:
                a = brazo_data['datos'][0][0]  # Lbrazo
                b = brazo_data['datos'][1][0]  # cota2
                c = brazo_data['datos'][2][0]  # cota3
                d = brazo_data['datos'][3][0]  # Radio
                e = brazo_data['datos'][4][0] * np.pi / 180  # angulo5
                f = brazo_data['datos'][5][0] * np.pi / 180  # angulo6
            
            # Ángulos
            alfa = (np.arctan(peralte[i] / (Ancho_via + Carril)))  # ángulo del peralte (p>0 (curva drcha)
            beta = np.abs(np.arctan(Fv_hc[i] / Fr_hc[i])) # ángulo brazos
            beta_max = parametros_b1[8] * np.pi / 180  # angulo máx. del brazo
            
            ang_brazo_rad = ang_brazo[i] * np.pi / 180
            
            if beta > beta_max:
                beta = beta_max
            
            if ang_brazo_rad > 0:
                beta = ang_brazo_rad
            
            elev_brazo = l_brazo[i] * np.sin(beta)
            x_brazo = l_brazo[i] * np.cos(beta)
            ganma = np.arctan((binf/2 - bsup/2)/Lposte)  # angulo conicidad poste
            delta = np.arctan(despl[i]/1000)  # angulo desplome
            sigma = parametros_b1[7] * np.pi / 180  # angulo del estabilizador
            
            # Coordenadas x e y
            x0, y0 = 0, 0
            x1 = datos_alt[i] * np.sin(alfa) + datos_desc[i] * np.cos(alfa)  # posición del hilo de contacto
            if alfa <= 0:
                y1 = datos_alt[i] * np.cos(alfa) + datos_desc[i] * np.sin(np.abs(alfa))  # El que le cambia el signo es el descentramiento
            else:
                y1 = datos_alt[i] * np.cos(alfa) - datos_desc[i] * np.sin(alfa)  # El descentramiento positivo hace bajar el hilo
            
            x2 = x1  # posición del sustentador
            y2 = y1 + alt_cat[i]
            x3 = x1 + l_brazo[i] * np.cos(beta)  # final del brazo de atirantado
            y3 = y1 + elev_brazo
            
            if t_b == 1:
                xba1 = x1 - b * np.abs(np.cos(d + beta))
                yba1 = y1 + b * np.sin(d + beta)
                xba2 = x3 - c * np.abs(np.cos(e - beta))
                yba2 = y3 + c * np.sin(e - beta)
                xba3, yba3 = xba2, yba2
            elif t_b == 2:
                xba1 = x1 - b * np.abs(np.cos(d + beta))
                yba1 = y1 + b * np.sin(d + beta)
                xba2 = x3 - c * np.abs(np.cos(e - beta))
                yba2 = y3 + c * np.sin(e - beta)
                xba3 = xba2 - h * np.cos(np.pi/2 + beta - f)
                yba3 = yba2 - h * np.sin(np.pi/2 + beta - f)
            elif t_b == 3:
                xba1 = x1 + b * np.abs(np.cos(e + beta))
                yba1 = y1 + b * np.sin(e + beta)
                xba2 = x3 - c * np.cos(f - beta)
                yba2 = y3 + c * np.sin(f - beta)
                xba3, yba3 = xba2, yba2
            
            x4 = x3 + brazo_supsa[0] + supsa[1]  # posición en x de la grapa que sostiene el brazo
            y4 = y3
            x5 = x4  # posición de la supsa en el estabilizador
            y5 = y4 + p_brazo_sup[i]
            x6 = x5  # posición final de la supsa (abajo)
            y6 = y5 - supsa[0]
            x7 = x1 + cota_fija_4 * np.cos(sigma)  # posición de la grapa del tubo de péndola en el estabilizador
            y7 = y5 + (x_brazo + brazo_supsa[0] + supsa[1]) * np.sin(sigma)
            x8 = x7 - (grapa_pend_estab[1]/2 + cota_fija_1) * np.cos(sigma)  # posición final del estabilizador
            y8 = y7 - (grapa_pend_estab[1]/2 + cota_fija_1) * np.sin(sigma)
            x12 = x7 - grapa_pend_estab[0] * np.sin(sigma)  # posición final grapa pendola
            y12 = y7 + grapa_pend_estab[0] * np.cos(sigma)
            xgalibo_poste = galibo[i]  # poste a la altura del PMR
            ygalibo_poste = 0
            xbase_poste = xgalibo_poste - ht[i] * np.tan(ganma + delta)  # base poste cara de la via
            ybase_poste = ygalibo_poste - ht[i]
            xaltura_poste = xbase_poste + Lposte * np.tan(ganma + delta)  # altura poste cara de la via
            yaltura_poste = ybase_poste + Lposte
            mposte = np.abs((yaltura_poste - ybase_poste) / (xaltura_poste - xbase_poste))  # pendiente de la recta de la cara del poste
            xbase_poste_atras = xbase_poste + binf * np.cos(delta)  # base poste cara atrás via
            ybase_poste_atras = ybase_poste - binf * np.sin(delta)
            xaltura_poste_atras = xaltura_poste + bsup * np.cos(delta)  # altura cara atrás via
            yaltura_poste_atras = yaltura_poste - bsup * np.sin(delta)
            
            if mposte == np.inf:
                mgiros = 0  # pendiente de la recta perpendiculares a la cara del poste
            else:
                mgiros = -1 / mposte
            
            xGM = xbase_poste + alt_GM[i] * np.tan(ganma + delta)  # posición giros ménsula
            yGM = ybase_poste + alt_GM[i]
            xGT = xGM + dist_giros[i] * np.tan(ganma + delta)  # posición giros tirante
            yGT = yGM + dist_giros[i]
            xGMBis = xGM - d_giro_men[0] * np.cos(ganma + delta)  # posición final giros ménsula
            yGMBis = yGM + d_giro_men[0] * np.sin(ganma + delta)
            xGTBis = xGT - d_giro_tir[0] * np.cos(ganma + delta)  # posición final giros tirante
            yGTBis = yGT + d_giro_tir[0] * np.sin(ganma + delta)
            x25 = xGMBis - d_rot_men[1] * np.cos(ganma + delta)  # posición final rotula mensula
            y25 = yGMBis + d_rot_men[1] * np.sin(ganma + delta) + d_rot_men[2] * np.cos(ganma + delta)
            x26 = xGTBis - d_rot_tir[0] * np.cos(ganma + delta)  # posición final rotula tirante
            y26 = yGTBis + d_rot_tir[0] * np.sin(ganma + delta)
            
            # recta tirante
            x26_aux = x26 - x2
            y26_aux = y26 - y2
            R_aux = np.sqrt((x26_aux**2 + y26_aux**2)+0j) / 2
            x_aux = x26_aux / 2
            y_aux = y26_aux / 2
            D = (BS[0]**2 - R_aux**2 + x_aux**2 + y_aux**2) / (2 * x_aux)
            E = y_aux / x_aux
            a_eq = E**2 + 1
            b_eq = -2 * D * E
            c_eq = D**2 - BS[0]**2
            disc=(b_eq**2 - 4 * a_eq * c_eq) 
            y20_aux = (-b_eq - np.sqrt(disc + 0j)) / (2 * a_eq)  # faltaria sumar + y2
            
            if y2 < y26:  # por las dos soluciones que hay en la ecuación de la circunferencia para una y
                x20_aux = np.sqrt((BS[0]**2 - y20_aux**2)+ 0j)
            else:
                x20_aux = - (np.sqrt((BS[0]**2 - y20_aux**2)+ 0j))
            
            x20 = x20_aux + x2  # posicion borne sustentador en el tubo de tirante
            y20 = y2 - (-y20_aux)
            omega = np.arctan((y26 - y20) / (x26 - x20))  # angulo del tubo de tirante
            x22 = x20 - (BS[1]/2 + cota_fija_2) * np.cos(omega)  # posicion final tirante
            y22 = y20 - (BS[1]/2 + cota_fija_2) * np.sin(omega)
            x19 = x20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.cos(omega)  # posicion de la grapa de union tirante-mensula
            y19 = y20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.sin(omega)
            x27 = x26 - ais_tir[0] * np.cos(omega)  # posicion tubo tirante dentro del aislador
            y27 = y26 - ais_tir[0] * np.sin(omega)
            x28 = x27 - grapa_diag_tir[0] * np.cos(omega)  # posicion final aislador
            y28 = y27 - grapa_diag_tir[0] * np.sin(omega)
            
            # diagonal
            if grapa_diag_tir[0] >= 57:
                x29, y29 = 0, 0
            else:
                x28aux = x27 - grapa_diag_tir[2] * np.cos(omega)
                y28aux = y27 - grapa_diag_tir[2] * np.sin(omega)
                x29 = x28aux + grapa_diag_tir[3] * np.sin(omega)
                y29 = y28aux - grapa_diag_tir[3] * np.cos(omega)
            
            mtirante = np.abs((y26 - y22) / (x26 - x22))  # pendiente de la recta tirante
            
            # recta mensula
            x18 = x19 + grapa_u_tirmen[0] * np.sin(omega)  # posicion del ojo terminal de union tirante-mensula
            y18 = y19 - grapa_u_tirmen[0] * np.cos(omega)
            teta = np.abs(np.arctan((y25 - y18) / (x25 - x18)))  # angulo del tubo de mensula (siempre positivo)
            Lsu = np.sqrt(((x25 - x18)**2 + (y25 - y18)**2) +0j) # SE OBTIENE EL VALOR DE LA DIAGONAL QUE UNE EL GM CON LA SEMIUNIÓN DEL TUBO DE TIRANTE
            xsu1 = np.sqrt((Lsu**2 - terminal_men[0]**2)+0j)  # SE CALCULA EL VALOR DEL CATETO CONTIGUO PARA OBTENER EL POSICIONAMIENTO DE LA SEMINUNIÓN DEL TUBO DE MÉNSULA
            teta_aux = np.arctan(terminal_men[0] / xsu1)  # SE CALCULA EL ÁNGULO DEL TRIÁNGULO ANTERIOR
            teta1 = teta - teta_aux
            xsu = x25 - xsu1 * np.cos(teta1)
            ysu = y25 + xsu1 * np.sin(teta1)
            x17, y17 = xsu, ysu
            x17bis = x17 - (50 + terminal_men[1]/2) * np.cos(teta1)  # posicion final del tubo de puntal de ménsula con crece de 50mm para el tapón
            y17bis = y17 + (50 + terminal_men[1]/2) * np.sin(teta1)
            x16 = x17 + (cota_fija_5 + grapa_pend_men[1]/2 + terminal_men[1]/2) * np.cos(teta1)  # posicion grapa tubo de péndola en el tubo de mensula
            y16 = y17 - (cota_fija_5 + grapa_pend_men[1]/2 + terminal_men[1]/2) * np.sin(teta1)
            x15 = x16 - grapa_pend_men[0] * np.sin(teta1)  # posicion final grapa pendola
            y15 = y16 - grapa_pend_men[0] * np.cos(teta1)
            x24 = x25 - ais_men[0] * np.cos(teta1)  # posicion tubo mensula dentro del aislador
            y24 = y25 + ais_men[0] * np.sin(teta1)
            x23 = x24 - ais_men[1] * np.cos(teta1)  # posicion final aislador
            y23 = y24 + ais_men[1] * np.sin(teta1)
            mmen = np.abs((y25 - y17) / (x25 - x17))  # pendiente de la recta mensula
            xdaux = x23 - grapa_men_estab[0] * np.sin(teta1)
            ydaux = y23 - grapa_men_estab[0] * np.cos(teta1)
            z = ydaux - (-mmen) * xdaux
            mestab = np.abs((y5 - y8) / (x5 - x8))  # pendiente de la recta estabilizador
            x10 = (y5 - z - mestab * x5) / (-mmen - mestab)  # Punto final grapa mensula estab
            y10 = -mmen * x10 + z
            x11 = x10 + grapa_men_estab[0] * np.sin(teta1)  # Posición grapa estab mensula en el tubo de mensula
            y11 = y10 + grapa_men_estab[0] * np.cos(teta1)
            x9 = x10 - terminal_estab[0] * np.cos(sigma)
            y9 = y10 - terminal_estab[0] * np.sin(sigma)
            x9bis = x9 - terminal_estab[1] * np.cos(sigma)
            y9bis = y9 - terminal_estab[1] * np.sin(sigma)
            
            # diagonal
            if grapa_diag_tir[0] >= 57:
                x34, y34 = 0, 0
            else:
                x34 = x11 + (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.cos(teta1)
                y34 = y11 - (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.sin(teta1)
            
            # pendola
            epsilon = np.abs(np.arctan(((y15 - y12) / (x15 - x12) )+0j))  # angulo del tubo de péndola siempre positivo
            if x15 >= x12:
                x14 = x15 - terminal_pend_men[0] * np.cos(epsilon)
                x14bis = x14 - terminal_pend_men[1] * np.cos(epsilon)
            else:
                x14 = x15 + terminal_pend_men[0] * np.cos(epsilon)
                x14bis = x14 + terminal_pend_men[1] * np.cos(epsilon)
            y14 = y15 - terminal_pend_men[0] * np.sin(epsilon)
            y14bis = y14 - terminal_pend_men[1] * np.sin(epsilon)
            
            if x15 >= x12:
                x13 = x12 + terminal_pend_estab[0] * np.cos(epsilon)
                x13bis = x13 + terminal_pend_estab[1] * np.cos(epsilon)
            else:
                x13 = x12 - terminal_pend_estab[0] * np.cos(epsilon)
                x13bis = x13 - terminal_pend_estab[1] * np.cos(epsilon)
            y13 = y12 + terminal_pend_estab[0] * np.sin(epsilon)
            y13bis = y13 + terminal_pend_estab[1] * np.sin(epsilon)
            
            # diagonal
            if grapa_diag_tir[0] >= 57:
                x33, y33 = 0, 0
                x32, y32 = 0, 0
                x32bis, y32bis = 0, 0
                x30, y30 = 0, 0
                x31, y31 = 0, 0
                x31bis, y31bis = 0, 0
            else:
                x33 = x34 + grapa_diag_men[0] * np.sin(teta1)
                y33 = y34 + grapa_diag_men[0] * np.cos(teta1)
                x30, y30 = x29, y29
                kappa = np.abs(np.arctan((y33 - y30) / (x33 - x30)))  # angulo del tubo de péndola siempre positivo
                
                if x30 >= x33:
                    x32 = x33 + terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 + terminal_diag_men[1] * np.cos(kappa)
                else:
                    x32 = x33 - terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 - terminal_diag_men[1] * np.cos(kappa)
                y32 = y33 + terminal_diag_men[0] * np.sin(kappa)
                y32bis = y32 + terminal_diag_men[1] * np.sin(kappa)
                
                if x30 >= x33:
                    x31 = x30 - terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 - terminal_diag_tir[1] * np.cos(kappa)
                else:
                    x31 = x30 + terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 + terminal_diag_tir[1] * np.cos(kappa)
                y31 = y30 - terminal_diag_tir[0] * np.sin(kappa)
                y31bis = y31 - terminal_diag_tir[1] * np.sin(kappa)
            
            # Comprobación de que se puede construir
            dist_compr_1 = np.sqrt(((x11 - x23)**2 + (y11 - y23)**2) +0j) # Distancia de comprobación para que entren los herrajes para la grapa del estabilizador
            if dist_compr_1 < cota_seguridad_1 or x11 > x23:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'No hay solución'
                warnings.warn(f'La ménsula no tiene solución o es vertical. Cambiar parámetros. Poste: {titulo}')
            
            dist_compr_1_diag = np.sqrt(((x34 - x23)**2 + (y34 - y23)**2)+0j)  # Distancia de comprobación para que entren los herrajes para la grapa de la diagonal en caso que haya
            if dist_compr_1_diag < cota_seguridad_1 and x34 != x11:
                titulo = str(datos_postes[i])
                warnings.warn(f'La diagonal no entraría en la ménsula. Cambiar cota o colocar por arriba. Poste: {titulo}')
            
            dist_compr_2 = np.sqrt(((x9bis - x5)**2 + (y9bis - y5)**2)+0j)  # Distancia de comprobación para que entren los herrajes para la grapa del estabilizador
            if dist_compr_2 < (cota_seguridad_2 + 23) or x9bis < x5:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'No hay solución'
                warnings.warn(f'La ménsula no tiene solución o es vertical. Cambiar parámetros. Poste: {titulo}')
            
            if y5 < yba3 or y5 < yba2:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'Supsa más larga'
                warnings.warn(f'La ménsula necesita una supsa más larga. Poste: {titulo}')
            
            # Almacenar coordenadas
            coords =[
                [x0, y0], [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5], [x6, y6], [x7, y7], [x8, y8], [x9, y9],
                [x10, y10], [x11, y11], [x12, y12], [x13, y13], [x14, y14], [x15, y15], [x16, y16], [x17, y17],
                [x18, y18], [x19, y19], [x20, y20], [x22, y22], [x23, y23], [x24, y24], [x25, y25], [x26, y26],
                [x27, y27], [x28, y28], [x29, y29], [x30, y30], [x31, y31], [x32, y32], [x33, y33], [x34, y34],
                [x9bis, y9bis], [x17bis, y17bis], [x13bis, y13bis], [x14bis, y14bis], [x31bis, y31bis], [x32bis, y32bis],
                [xGM, yGM], [xGT, yGT], [xGMBis, yGMBis], [xGTBis, yGTBis], [xgalibo_poste, ygalibo_poste],
                [xbase_poste, ybase_poste], [xaltura_poste, yaltura_poste], [xbase_poste_atras, ybase_poste_atras],
                [xaltura_poste_atras, yaltura_poste_atras], [xba1, yba1], [xba2, yba2], [xba3, yba3]
            ]
            
            if lado_poste[i] == 'Izquierda':
                coords[:, 0] = -coords[:, 0]  # coordenadas x cambiadas de signo
            
            #Coord_Mensulas_Calculo[:, 2*i:2*i+2] = coords
            Coord_Mensulas_Calculo[:, 2*i : 2*i+2]=coords
        
        # ----------------------------------------------------------------------------B2----------------------------------------------------------------------------%
        elif tipo_men[i] == 'B2':
  
   
            # Cargar las bibliotecas de las mensulas individualmente
            # herrajes mensulas
            ruta=os.path.join('Bibliotecas','Tipos de Ménsulas', nombre_men[i])
            herrajes_mensula_data = loadmat(ruta)
            grapas_b2 = herrajes_mensula_data['grapas_b2']
            terminales_b2 = herrajes_mensula_data['terminales_b2']
            parametros_b2 = aplanar_varias_veces(herrajes_mensula_data['parametros_b2'],3)
            otrosherrajes_b2 = herrajes_mensula_data['otrosherrajes_b2']
            medidas_herrajes_mensula = herrajes_mensula_data['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_data['herrajes_mensula']
            
            # Convertir cell arrays a listas de strings
            grapas_b2 = [str(g[0]) for g in grapas_b2 if g.size > 0]
            terminales_b2 = [str(t[0]) for t in terminales_b2 if t.size > 0]
            otrosherrajes_b2 = [str(o[0]) for o in otrosherrajes_b2 if o.size > 0]
            herrajes_mensula = [str(h[0]) for h in herrajes_mensula if h.size > 0]
            
           # Obtener medidas de herrajes
            brazo_supsa = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b2[4])
            supsa = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b2[3])
            ais_tir = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b2[0])
            ais_men = obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_b2[1])
            
            # Obtener parámetros
            cota_fija_4 = parametros_b2[3]
            cota_fija_1 = parametros_b2[0]
            cota_fija_2 = parametros_b2[1]
            cota_fija_3 = parametros_b2[2]
            cota_fija_5 = parametros_b2[4]
            cota_fija_6 = parametros_b2[5]
            cota_fija_7 = parametros_b2[6]
            cota_seguridad_1 = parametros_b2[9]
            beta_max = parametros_b2[8] * np.pi / 180
            sigma = parametros_b2[7] * np.pi / 180

            # Obtener grapas
            grapa_men_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[1])
            grapa_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[2])
            grapa_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[3])
            grapa_u_tirmen = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[0])
            grapa_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[5])
            grapa_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_b2[4])

            # Obtener terminales
            terminal_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[0])
            terminal_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[1])
            terminal_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[2])
            terminal_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[3])
            terminal_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[4])
            terminal_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_b2[5])

            # Obtener BS
            BS = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, otrosherrajes_b2[2])

            # Obtener medidas de giros
            giros_simple_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GM')
            giros_simple_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GT')
            giros_doble_GM_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1200')
            giros_doble_GT_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1200')
            giros_doble_GM_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1500')
            giros_doble_GT_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1500')
            rot_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GM')
            rot_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GT')
            
            # Determinar tipo de giros
            if giros_men[i] == 'Simple':
                d_giro_men = giros_simple_GM
                d_giro_tir = giros_simple_GT
            elif giros_men[i] == 'Doble 1200':
                d_giro_men = giros_doble_GM_1200
                d_giro_tir = giros_doble_GT_1200
            elif giros_men[i] == 'Doble 1500':
                d_giro_men = giros_doble_GM_1500
                d_giro_tir = giros_doble_GT_1500
                
            d_rot_men = rot_GM
            d_rot_tir = rot_GT
            
            # Cargar biblioteca de postes
            ruta=os.path.join('Bibliotecas','Postes', tipo_poste[i])
            poste_mensula_data = loadmat(ruta)
            Lposte = poste_mensula_data['h'][0][0]
            binf = poste_mensula_data['h0'][0][0]
            bsup = poste_mensula_data['h1'][0][0]
            
            # Cargar biblioteca de brazos
            ruta=os.path.join('Bibliotecas','Brazos de atirantado', tipo_brazo[i])
            brazo_mensula_data = loadmat(ruta)
            t_b = brazo_mensula_data['tipo'][0]
            
            if t_b == 1:
                a = brazo_mensula_data['datos'][0][0]  # Lbrazo
                b = brazo_mensula_data['datos'][1][0]  # cota2
                c = brazo_mensula_data['datos'][2][0]  # cota3
                d = brazo_mensula_data['datos'][3][0] * np.pi / 180  # angulo4
                e = brazo_mensula_data['datos'][4][0] * np.pi / 180  # angulo5
                f = brazo_mensula_data['datos'][5][0] * np.pi / 180  # angulo6
            elif t_b == 2:
                a = brazo_mensula_data['datos'][0][0]  # Lbrazo
                b = brazo_mensula_data['datos'][1][0]  # cota2
                c = brazo_mensula_data['datos'][2][0]  # cota3
                d = brazo_mensula_data['datos'][5][0] * np.pi / 180  # angulo4
                e = brazo_mensula_data['datos'][6][0] * np.pi / 180  # angulo5
                f = brazo_mensula_data['datos'][7][0] * np.pi / 180  # angulo6
                g = brazo_mensula_data['datos'][3][0]  # cota4
                h = brazo_mensula_data['datos'][4][0]  # cota5
            elif t_b == 3:
                a = brazo_mensula_data['datos'][0][0]  # Lbrazo
                b = brazo_mensula_data['datos'][1][0]  # cota2
                c = brazo_mensula_data['datos'][2][0]  # cota3
                d = brazo_mensula_data['datos'][3][0]  # Radio
                e = brazo_mensula_data['datos'][4][0] * np.pi / 180  # angulo5
                f = brazo_mensula_data['datos'][5][0] * np.pi / 180  # angulo6
                
            # Ángulos
            alfa = (np.arctan(peralte[i] / (Ancho_via + Carril))) # Ángulo del peralte
            beta = (np.abs(np.arctan(Fv_hc[i] / Fr_hc[i]))) # Ángulo brazos
            elev_brazo = l_brazo[i] * np.sin(beta)
            x_brazo = l_brazo[i] * np.cos(beta)
            
            # Ajustar ángulo del brazo según parámetros
            ang_brazo_rad = ang_brazo[i] * np.pi / 180
            
            if ang_brazo_rad > 0:
                beta = ang_brazo_rad
                
            if beta > beta_max:
                beta = beta_max
                
            elev_brazo = l_brazo[i] * np.sin(beta)
            x_brazo = l_brazo[i] * np.cos(beta)
            
            # Otros ángulos
            ganma = np.arctan((binf/2 - bsup/2) / Lposte)  # ángulo conicidad poste
            delta = np.arctan(despl[i] / 1000)  # ángulo desplome
            
            # Coordenadas
            x0, y0 = 0, 0
            x1 = (datos_alt[i] * np.sin(alfa) + datos_desc[i] * np.cos(alfa)) # posición del hilo de contacto
            
            if alfa <= 0:
                y1 = (datos_alt[i] * np.cos(alfa) + datos_desc[i] * np.sin(np.abs(alfa)))
            else:
                y1 = (datos_alt[i] * np.cos(alfa) - datos_desc[i] * np.sin(alfa))
                
            x2 = x1  # posición del sustentador
            y2 = y1 + alt_cat[i]
            x3 = x1 - l_brazo[i] * np.cos(beta)  # final del brazo de atirantado
            y3 = y1 + elev_brazo
            
            # Coordenadas del brazo según tipo
            if t_b == 1:
                xba1 = x1 + b * np.abs(np.cos(d + beta))
                yba1 = y1 + b * np.sin(d + beta)
                xba2 = x3 + c * np.abs(np.cos(e - beta))
                yba2 = y3 + c * np.sin(e - beta)
                xba3, yba3 = xba2, yba2
            elif t_b == 2:
                xba1 = x1 + b * np.abs(np.cos(d + beta))
                yba1 = y1 + b * np.sin(d + beta)
                xba2 = x3 + c * np.abs(np.cos(e - beta))
                yba2 = y3 + c * np.sin(e - beta)
                xba3 = xba2 + h * np.cos(np.pi/2 + beta - f)
                yba3 = yba2 - h * np.sin(np.pi/2 + beta - f)
            elif t_b == 3:
                xba1 = x1 + b * np.abs(np.cos(e + beta))
                yba1 = y1 + b * np.sin(e + beta)
                xba2 = x3 + c * np.cos(f - beta)
                yba2 = y3 + c * np.sin(f - beta)
                xba3, yba3 = xba2, yba2
                
            # Más coordenadas
            x4 = x3 - brazo_supsa[0] - supsa[1]  # posición en x de la grapa que sostiene el brazo
            y4 = y3
            x5 = x4  # posición de la supsa en el estabilizador
            y5 = y4 + p_brazo_sup[i]
            x6 = x5  # posición final de la supsa (abajo)
            y6 = y5 - supsa[0]
            x7 = x1 - cota_fija_4 * np.cos(sigma)  # posición de la grapa del tubo de péndola en el estabilizador
            y7 = y5 + (x_brazo + brazo_supsa[0] + supsa[1]) * np.sin(sigma)
            x8 = x5 - (supsa[2]/2 + cota_fija_1 - 8) * np.cos(sigma)  # posición final del estabilizador
            y8 = y5 - (supsa[2]/2 + cota_fija_1 - 8) * np.sin(sigma)
            x12 = x7 - grapa_pend_estab[0] * np.sin(sigma)  # posición final grapa pendola
            y12 = y7 + grapa_pend_estab[0] * np.cos(sigma)
            xgalibo_poste = galibo[i]  # poste a la altura del PMR
            ygalibo_poste = 0
            xbase_poste = xgalibo_poste - ht[i] * np.tan(ganma + delta)  # base poste cara de la via
            ybase_poste = ygalibo_poste - ht[i]
            xaltura_poste = xbase_poste + Lposte * np.tan(ganma + delta)  # altura poste cara de la via
            yaltura_poste = ybase_poste + Lposte
            mposte = np.abs((yaltura_poste - ybase_poste) / (xaltura_poste - xbase_poste))  # pendiente de la recta de la cara del poste
            
            xbase_poste_atras = xbase_poste + binf * np.cos(delta)  # base poste cara atrás via
            ybase_poste_atras = ybase_poste - binf * np.sin(delta)
            xaltura_poste_atras = xaltura_poste + bsup * np.cos(delta)  # altura cara atrás via
            yaltura_poste_atras = yaltura_poste - bsup * np.sin(delta)
            
            if np.isinf(mposte):
                mgiros = 0  # pendiente de la recta perpendiculares a la cara del poste
            else:
                mgiros = -1 / mposte
                
            xGM = xbase_poste + alt_GM[i] * np.tan(ganma + delta)  # posición giros mánsula
            yGM = ybase_poste + alt_GM[i]
            xGT = xGM + dist_giros[i] * np.tan(ganma + delta)  # posición giros tirante
            yGT = yGM + dist_giros[i]
            xGMBis = xGM - d_giro_men[0] * np.cos(ganma + delta)  # posición final giros mánsula
            yGMBis = yGM + d_giro_men[0] * np.sin(ganma + delta)
            xGTBis = xGT - d_giro_tir[0] * np.cos(ganma + delta)  # posición final giros tirante
            yGTBis = yGT + d_giro_tir[0] * np.sin(ganma + delta)
            x25 = xGMBis - d_rot_men[1] * np.cos(ganma + delta)  # posición final rotula mensula
            y25 = yGMBis + d_rot_men[1] * np.sin(ganma + delta) + d_rot_men[2] * np.cos(ganma + delta)
            x26 = xGTBis - d_rot_tir[0] * np.cos(ganma + delta)  # posición final rotula tirante
            y26 = yGTBis + d_rot_tir[0] * np.sin(ganma + delta)
            
            # Recta tirante
            x26_aux = x26 - x2
            y26_aux = y26 - y2
            R_aux = np.sqrt((x26_aux**2 + y26_aux**2)+0j) / 2
            x_aux = x26_aux / 2
            y_aux = y26_aux / 2
            D = (BS[0]**2 - R_aux**2 + x_aux**2 + y_aux**2) / (2 * x_aux)
            E = y_aux / x_aux
            a_eq = E**2 + 1
            b_eq = -2 * D * E
            c_eq = D**2 - BS[0]**2
            
            # Resolver ecuación cuadrática
            discriminant = b_eq**2 - 4 * a_eq * c_eq
            
            y20_aux = (-b_eq - np.sqrt(discriminant +0j)) / (2 * a_eq)
                
            if y2 < y26:
                x20_aux = np.sqrt((BS[0]**2 - y20_aux**2) + 0j)
            else:
                x20_aux =  -(np.sqrt(((BS[0]**2 - y20_aux**2)) + 0j))
                
                
            x20 = x20_aux + x2  # posición borne sustentador en el tubo de tirante
            y20 = y2 - (-y20_aux)
            omega = np.arctan((y26 - y20) / (x26 - x20))  # ángulo del tubo de tirante
            
            x22 = x20 - (BS[1]/2 + cota_fija_2) * np.cos(omega)  # posición final tirante
            y22 = y20 - (BS[1]/2 + cota_fija_2) * np.sin(omega)
            x19 = x20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.cos(omega)  # posición de la grapa de union tirante-mensula
            y19 = y20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.sin(omega)
            x27 = x26 - ais_tir[0] * np.cos(omega)  # posición tubo tirante dentro del aislador
            y27 = y26 - ais_tir[0] * np.sin(omega)
            x28 = x27 - grapa_diag_tir[0] * np.cos(omega)  # posición final aislador
            y28 = y27 - grapa_diag_tir[0] * np.sin(omega)
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x29, y29 = 0, 0
            else:
                x28aux = x27 - grapa_diag_tir[2] * np.cos(omega)
                y28aux = y27 - grapa_diag_tir[2] * np.sin(omega)
                x29 = x28aux + grapa_diag_tir[3] * np.sin(omega)
                y29 = y28aux - grapa_diag_tir[3] * np.cos(omega)
                
            mtirante = np.abs((y26 - y22) / (x26 - x22))  # pendiente de la recta tirante
            
            # Recta mensula
            x18 = x19 + grapa_u_tirmen[0] * np.sin(omega)  # posición del ojo terminal de union tirante-mensula
            y18 = y19 - grapa_u_tirmen[0] * np.cos(omega)
            teta = np.abs(np.arctan((y25 - y18) / (x25 - x18)))  # ángulo del tubo de mensula (siempre positivo)
            
            Lsu = np.sqrt(((x25 - x18)**2 + (y25 - y18)**2)+0j)  # SE OBTIENE EL VALOR DE LA DIAGONAL QUE UNE EL GM CON LA SEMIUNIÓN DEL TUBO DE TIRANTE
            xsu1 = np.sqrt((Lsu**2 - terminal_men[0]**2)+0j)  # SE CALCULA EL VALOR DEL CATETO CONTIGUO PARA OBTENER EL POSICIONAMIENTO DE LA SEMINUNIÓN DEL TUBO DE MÁNSULA
            teta_aux = np.arctan(terminal_men[0] / xsu1)  # SE CALCULA EL ÁNGULO DEL TRIÁNGULO ANTERIOR
            teta1 = teta - teta_aux
            xsu = x25 - xsu1 * np.cos(teta1)
            ysu = y25 + xsu1 * np.sin(teta1)
            x17, y17 = xsu, ysu
            x17bis = x17 - (50 + terminal_men[1]/2) * np.cos(teta1)  # posición final del tubo de puntal de mánsula con crece de 50mm para el tapón
            y17bis = y17 + (50 + terminal_men[1]/2) * np.sin(teta1)
            
            x16, y16 = x20, y20  # posición grapa tubo de péndola en el tubo de tirante
            x15 = x16 + BS[3] * np.sin(omega)  # POSICIÓN GANCHO SUSPENSIÓN DE BORNE SUSTENTADOR
            y15 = y16 - BS[3] * np.cos(omega)
            x24 = x25 - ais_men[0] * np.cos(teta1)  # posición tubo mensula dentro del aislador
            y24 = y25 + ais_men[0] * np.sin(teta1)
            x23 = x24 - ais_men[1] * np.cos(teta1)  # posición final aislador
            y23 = y24 + ais_men[1] * np.sin(teta1)
            mmen = np.abs((y25 - y17) / (x25 - x17))  # pendiente de la recta mensula
            
            xdaux = x23 - grapa_men_estab[0] * np.sin(teta1)
            ydaux = y23 - grapa_men_estab[0] * np.cos(teta1)
            z = ydaux - (-mmen) * xdaux
            mestab = np.abs((y5 - y8) / (x5 - x8))  # pendiente de la recta estabilizador
            
            x10 = (y5 - z - mestab * x5) / (-mmen - mestab)  # Punto final grapa mensula estab
            y10 = -mmen * x10 + z
            x11 = x10 + grapa_men_estab[0] * np.sin(teta1)  # Posición grapa estab mensula en el tubo de mensula
            y11 = y10 + grapa_men_estab[0] * np.cos(teta1)
            x9 = x10 - terminal_estab[0] * np.cos(sigma)
            y9 = y10 - terminal_estab[0] * np.sin(sigma)
            x9bis = x9 - terminal_estab[1] * np.cos(sigma)
            y9bis = y9 - terminal_estab[1] * np.sin(sigma)
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x34, y34 = 0, 0
            else:
                x34 = x11 + (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.cos(teta1)
                y34 = y11 - (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.sin(teta1)
                
            # Péndola PA-FLEX
            epsilon = np.abs(np.arctan((y15 - y12) / (x15 - x12)))  # ángulo del tubo de péndola siempre positivo
            x14, x14bis, x13, x13bis = x15, x15, x12, x12
            y14, y14bis, y13, y13bis = y15, y15, y12, y12
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x33, y33 = 0, 0
                x32, y32 = 0, 0
                x32bis, y32bis = 0, 0
                x30, y30 = 0, 0
                x31, y31 = 0, 0
                x31bis, y31bis = 0, 0
            else:
                x33 = x34 + grapa_diag_men[0] * np.sin(teta1)
                y33 = y34 + grapa_diag_men[0] * np.cos(teta1)
                x30, y30 = x29, y29
                kappa = np.abs(np.arctan((y33 - y30) / (x33 - x30)))  # ángulo del tubo de péndola siempre positivo
                
                if x30 >= x33:
                    x32 = x33 + terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 + terminal_diag_men[1] * np.cos(kappa)
                else:
                    x32 = x33 - terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 - terminal_diag_men[1] * np.cos(kappa)
                y32 = y33 + terminal_diag_men[0] * np.sin(kappa)
                y32bis = y32 + terminal_diag_men[1] * np.sin(kappa)
                
                if x30 >= x33:
                    x31 = x30 - terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 - terminal_diag_tir[1] * np.cos(kappa)
                else:
                    x31 = x30 + terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 + terminal_diag_tir[1] * np.cos(kappa)
                y31 = y30 - terminal_diag_tir[0] * np.sin(kappa)
                y31bis = y31 - terminal_diag_tir[1] * np.sin(kappa)
                
            # Comprobación de que se puede construir
            dist_compr_1 = np.sqrt(((x11 - x23)**2 + (y11 - y23)**2)+0j)  # Distancia de comprobación para que entren los herrajes
            
            if dist_compr_1 < cota_seguridad_1 or x11 > x23:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'No hay solución'
                warnings.warn(f'La mánsula no tiene solución. Cambiar parámetros - {titulo}')
                
            dist_compr_1_diag = np.sqrt(((x34 - x23)**2 + (y34 - y23)**2)+0j)  # Distancia de comprobación para la diagonal
            
            if dist_compr_1_diag < cota_seguridad_1 and x34 != x11:
                titulo = str(datos_postes[i])
                warnings.warn(f'La diagonal no entraría en la mánsula. Cambiar cota o colocar por arriba - {titulo}')
                
            if y5 < yba3 or y5 < yba2:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'Supsa más larga'
                warnings.warn(f'La mánsula necesita una supsa más larga. - {titulo}')
                
            coords = [
            (x0, y0), (x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6), (x7, y7),
            (x8, y8), (x9, y9), (x10, y10), (x11, y11), (x12, y12), (x13, y13), (x14, y14),
            (x15, y15), (x16, y16), (x17, y17), (x18, y18), (x19, y19), (x20, y20), (x22, y22),
            (x23, y23), (x24, y24), (x25, y25), (x26, y26), (x27, y27), (x28, y28), (x29, y29),
            (x30, y30), (x31, y31), (x32, y32), (x33, y33), (x34, y34), (x9bis, y9bis), (x17bis, y17bis),
            (x13bis, y13bis), (x14bis, y14bis), (x31bis, y31bis), (x32bis, y32bis), (xGM, yGM),
            (xGT, yGT), (xGMBis, yGMBis), (xGTBis, yGTBis), (xgalibo_poste, ygalibo_poste),
            (xbase_poste, ybase_poste), (xaltura_poste, yaltura_poste), (xbase_poste_atras, ybase_poste_atras),
            (xaltura_poste_atras, yaltura_poste_atras), (xba1, yba1), (xba2, yba2), (xba3, yba3)
            ]

            # Crear un array de numpy con el tamaño adecuado (52 filas y 2 columnas por i)
           # Coord_Mensulas_Calculo_aux= np.array(coords).flatten() # Inicializar el array con ceros
            
            # Ajustar para lado izquierdo
            if lado_poste[i] == 'Izquierda':
                coords[:, 0] = -coords[:, 0]
                
            # Almacenar en la matriz de resultados
            #Coord_Mensulas_Calculo[:, 2*i-1:2*i] = coords
            Coord_Mensulas_Calculo[:, 2*i : 2*i+2]=coords
        
        # ----------------------------------------------------------------------------Elevación----------------------------------------------------------------------------%
        elif tipo_men[i] == 'Elevación':
            
            # Cargar las bibliotecas de las mensulas individualmente
            ruta=os.path.join('Bibliotecas', 'Tipos de Ménsulas', nombre_men[i])
            herrajes_mensula_data = loadmat(ruta)
            
            # Extraer componentes
            grapas_cola = herrajes_mensula_data['grapas_cola']
            terminales_cola = herrajes_mensula_data['terminales_cola']
            parametros_cola = aplanar_varias_veces( herrajes_mensula_data['parametros_cola'],3)
            otrosherrajes_cola = herrajes_mensula_data['otrosherrajes_cola']
            medidas_herrajes_mensula = herrajes_mensula_data['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_data['herrajes_mensula']
            
            # Convertir cell arrays a listas de strings
            grapas_cola = [str(g[0]) for g in grapas_cola if g.size > 0]
            terminales_cola = [str(t[0]) for t in terminales_cola if t.size > 0]
            otrosherrajes_cola = [str(o[0]) for o in otrosherrajes_cola if o.size > 0]
            herrajes_mensula = [str(h[0]) for h in herrajes_mensula if h.size > 0]
            
            # Verificar herrajes definidos
            if not otrosherrajes_cola[0] or not otrosherrajes_cola[1]:
                raise ValueError('No se han definido los herrajes de las mánsulas')
            
            # Obtener medidas de herrajes
            anclaje_hc=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_cola[3])
            ais_tir=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_cola[0])
            ais_men=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_cola[1])
            
            # Obtener parámetros
            cota_fija_4 = parametros_cola[3]
            cota_fija_1 = parametros_cola[0]
            cota_fija_2 = parametros_cola[1]
            cota_fija_3 = parametros_cola[2]
            cota_fija_5 = parametros_cola[4]
            cota_fija_6 = parametros_cola[5]
            cota_fija_7 = parametros_cola[6]
            cota_seguridad_1 = parametros_cola[8]
            sigma = parametros_cola[7] * np.pi / 180
            
            # Obtener grapas
            grapa_men_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[1])
            grapa_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[2])
            grapa_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[3])
            grapa_u_tirmen = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[0])
            grapa_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[5])
            grapa_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, grapas_cola[4])

            # Obtener terminales
            terminal_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[0])
            terminal_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[1])
            terminal_pend_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[2])
            terminal_pend_estab = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[3])
            terminal_diag_men = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[4])
            terminal_diag_tir = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, terminales_cola[5])

            # Obtener BS
            BS = obtener_medida(medidas_herrajes_mensula,herrajes_mensula, otrosherrajes_cola[2])
            
            # Obtener medidas de giros
            giros_simple_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GM')
            giros_simple_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Simple_GT')
            giros_doble_GM_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1200')
            giros_doble_GT_1200 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1200')
            giros_doble_GM_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GM_1500')
            giros_doble_GT_1500 = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Giro_Doble_GT_1500')
            rot_GM = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GM')
            rot_GT = obtener_medida(medidas_herrajes_catenaria,herrajes_catenaria, 'Rótula_GT')
            
            # Determinar tipo de giros
            if giros_men[i] == 'Simple':
                d_giro_men = giros_simple_GM
                d_giro_tir = giros_simple_GT
            elif giros_men[i] == 'Doble 1200':
                d_giro_men = giros_doble_GM_1200
                d_giro_tir = giros_doble_GT_1200
            elif giros_men[i] == 'Doble 1500':
                d_giro_men = giros_doble_GM_1500
                d_giro_tir = giros_doble_GT_1500
                
            d_rot_men = rot_GM
            d_rot_tir = rot_GT
            
            # Cargar biblioteca de postes
            ruta=os.path.join('Bibliotecas','Postes', tipo_poste[i])
            poste_mensula_data = loadmat(ruta)
            Lposte = poste_mensula_data['h'][0,0]
            binf = poste_mensula_data['h0'][0,0]
            bsup = poste_mensula_data['h1'][0,0]
            
            # Ángulos
            alfa = (np.arctan(peralte[i] / (Ancho_via + Carril)))
            ganma = np.arctan((binf/2 - bsup/2) / Lposte)  # ángulo conicidad poste
            delta = np.arctan(despl[i] / 1000)  # ángulo desplome
            
            # Coordenadas
            x0, y0 = 0, 0
            x1 = datos_alt[i] * np.sin(alfa) + datos_desc[i] * np.cos(alfa)  # posición del hilo de contacto
            
            if alfa <= 0:
                y1 = datos_alt[i] * np.cos(alfa) + datos_desc[i] * np.sin(np.abs(alfa))
            else:
                y1 = datos_alt[i] * np.cos(alfa) - datos_desc[i] * np.sin(alfa)
                
            x5 = x1 - anclaje_hc[0] * np.sin(sigma)  # posición de la anclaje_hc en el estabilizador
            y5 = y1 + anclaje_hc[0] * np.cos(sigma)
            x2 = x1  # posición del sustentador
            y2 = y1 + alt_cat[i]
            x3, y3 = x5, y5
            xba1, yba1 = x1, y1
            xba2, yba2 = x1, y1
            xba3, yba3 = x1, y1
            x4, y4 = x5, y5
            x6, y6 = x5, y5  # posición final de la anclaje_hc (abajo)
            x7 = x5 + cota_fija_4 * np.cos(sigma)  # posición de la grapa del tubo de péndola en el estabilizador
            y7 = y5 + cota_fija_4 * np.sin(sigma)
            x8 = x5 - (anclaje_hc[2] + cota_fija_1) * np.cos(sigma)  # posición final del estabilizador
            y8 = y5 - (anclaje_hc[2] + cota_fija_1) * np.sin(sigma)
            x12 = x7 - grapa_pend_estab[0] * np.sin(sigma)  # posición final grapa pendola
            y12 = y7 + grapa_pend_estab[0] * np.cos(sigma)
            xgalibo_poste = galibo[i]  # poste a la altura del PMR
            ygalibo_poste = 0
            xbase_poste = xgalibo_poste - ht[i] * np.tan(ganma + delta)  # base poste cara de la via
            ybase_poste = ygalibo_poste - ht[i]
            xaltura_poste = xbase_poste + Lposte * np.tan(ganma + delta)  # altura poste cara de la via
            yaltura_poste = ybase_poste + Lposte
            xbase_poste_atras = xbase_poste + binf * np.cos(delta)  # base poste cara atrás via
            ybase_poste_atras = ybase_poste - binf * np.sin(delta)
            xaltura_poste_atras = xaltura_poste + bsup * np.cos(delta)  # altura cara atrás via
            yaltura_poste_atras = yaltura_poste - bsup * np.sin(delta)
            mposte = np.abs((yaltura_poste - ybase_poste) / (xaltura_poste - xbase_poste))  # pendiente de la recta de la cara del poste
            
            if np.isinf(mposte):
                mgiros = 0  # pendiente de la recta perpendiculares a la cara del poste
            else:
                mgiros = -1 / mposte
                
            xGM = xbase_poste + alt_GM[i] * np.tan(ganma + delta)  # posición giros mánsula
            yGM = ybase_poste + alt_GM[i]
            xGT = xGM + dist_giros[i] * np.tan(ganma + delta)  # posición giros tirante
            yGT = yGM + dist_giros[i]
            xGMBis = xGM - d_giro_men[0] * np.cos(ganma + delta)  # posición final giros mánsula
            yGMBis = yGM + d_giro_men[0] * np.sin(ganma + delta)
            xGTBis = xGT - d_giro_tir[0] * np.cos(ganma + delta)  # posición final giros tirante
            yGTBis = yGT + d_giro_tir[0] * np.sin(ganma + delta)
            x25 = xGMBis - d_rot_men[1] * np.cos(ganma + delta)  # posición final rotula mensula
            y25 = yGMBis + d_rot_men[1] * np.sin(ganma + delta) + d_rot_men[2] * np.cos(ganma + delta)
            x26 = xGTBis - d_rot_tir[0] * np.cos(ganma + delta)  # posición final rotula tirante
            y26 = yGTBis + d_rot_tir[0] * np.sin(ganma + delta)
            
            # Recta tirante
            x26_aux = x26 - x2
            y26_aux = y26 - y2
            R_aux = np.sqrt((x26_aux**2 + y26_aux**2)+0j) / 2
            x_aux = x26_aux / 2
            y_aux = y26_aux / 2
            ASAA=(BS[0])**2
            D = ((BS[0])**2 - R_aux**2 + x_aux**2 + y_aux**2) / (2 * x_aux)
            E = y_aux / x_aux
            a_eq = E**2 + 1
            b_eq = -2 * D * E
            c_eq = D**2 - BS[0]**2
            
            # Resolver ecuación cuadrática
            discriminant = b_eq**2 - 4 * a_eq * c_eq
            y20_aux = (-b_eq - np.sqrt(discriminant + 0j)) / (2 * a_eq)
                
            if y2 < y26:
                x20_aux = np.sqrt((BS[0]**2 - y20_aux**2)+0j)
            else:
                x20_aux = -np.sqrt((BS[0]**2 - y20_aux**2)+0j)
                
            x20 = x20_aux + x2  # posición borne sustentador en el tubo de tirante
            y20 = y2 - (-y20_aux)
            omega = np.arctan((y26 - y20) / (x26 - x20))  # ángulo del tubo de tirante
            
            x22 = x20 - (BS[1]/2 + cota_fija_2) * np.cos(omega)  # posición final tirante
            y22 = y20 - (BS[1]/2 + cota_fija_2) * np.sin(omega)
            x19 = x20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.cos(omega)  # posición de la grapa de union tirante-mensula
            y19 = y20 + (BS[1]/2 + cota_fija_3 + grapa_u_tirmen[1]/2) * np.sin(omega)
            x27 = x26 - ais_tir[0] * np.cos(omega)  # posición tubo tirante dentro del aislador
            y27 = y26 - ais_tir[0] * np.sin(omega)
            x28 = x27 - grapa_diag_tir[0] * np.cos(omega)  # posición final aislador
            y28 = y27 - grapa_diag_tir[0] * np.sin(omega)
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x29, y29 = 0, 0
            else:
                x28aux = x27 - grapa_diag_tir[2] * np.cos(omega)
                y28aux = y27 - grapa_diag_tir[2] * np.sin(omega)
                x29 = x28aux + grapa_diag_tir[3] * np.sin(omega)
                y29 = y28aux - grapa_diag_tir[3] * np.cos(omega)
                
            mtirante = np.abs((y26 - y22) / (x26 - x22))  # pendiente de la recta tirante
            
            # Recta mensula
            x18 = x19 + grapa_u_tirmen[0] * np.sin(omega)  # posición del ojo terminal de union tirante-mensula
            y18 = y19 - grapa_u_tirmen[0] * np.cos(omega)
            teta = np.abs(np.arctan((y25 - y18) / (x25 - x18)))  # ángulo del tubo de mensula (siempre positivo)
            
            Lsu = np.sqrt(((x25 - x18)**2 + (y25 - y18)**2)+0j)  # Diagonal que une el GM con la semiunión
            xsu1 = np.sqrt((Lsu**2 - terminal_men[0]**2) +0j) # Cateto contiguo
            teta_aux = np.arctan(terminal_men[0] / xsu1)  # Ángulo del triángulo
            teta1 = teta - teta_aux
            xsu = x25 - xsu1 * np.cos(teta1)
            ysu = y25 + xsu1 * np.sin(teta1)
            x17, y17 = xsu, ysu
            x17bis = x17 - (50 + terminal_men[1]/2) * np.cos(teta1)  # posición inicial del terminal
            y17bis = y17 + (50 + terminal_men[1]/2) * np.sin(teta1)
            
            x16, y16 = x20, y20  # posición grapa tubo de péndola en el tubo de tirante
            x15 = x16 + BS[3] * np.sin(omega)  # POSICIÓN GANCHO SUSPENSIÓN DE BORNE SUSTENTADOR
            y15 = y16 - BS[3] * np.cos(omega)
            
            x24 = x25 - ais_men[0] * np.cos(teta1)  # posición tubo mensula dentro del aislador
            y24 = y25 + ais_men[0] * np.sin(teta1)
            x23 = x24 - ais_men[1] * np.cos(teta1)  # posición final aislador
            y23 = y24 + ais_men[1] * np.sin(teta1)
            mmen = np.abs((y25 - y17) / (x25 - x17))  # pendiente de la recta mensula
            
            xdaux = x23 - grapa_men_estab[0] * np.sin(teta1)
            ydaux = y23 - grapa_men_estab[0] * np.cos(teta1)
            z = ydaux - (-mmen) * xdaux
            mestab = np.abs((y5 - y8) / (x5 - x8))  # pendiente de la recta estabilizador
            
            x10 = (y5 - z - mestab * x5) / (-mmen - mestab)  # Punto final grapa mensula estab
            y10 = -mmen * x10 + z
            x11 = x10 + grapa_men_estab[0] * np.sin(teta1)  # Posición grapa estab mensula en el tubo de mensula
            y11 = y10 + grapa_men_estab[0] * np.cos(teta1)
            x9 = x10 - terminal_estab[0] * np.cos(sigma)
            y9 = y10 - terminal_estab[0] * np.sin(sigma)
            x9bis = x9 - terminal_estab[1] * np.cos(sigma)
            y9bis = y9 - terminal_estab[1] * np.sin(sigma)
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x34, y34 = 0, 0
            else:
                x34 = x11 + (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.cos(teta1)
                y34 = y11 - (cota_fija_6 + grapa_men_estab[1]/2 + grapa_diag_men[1]/2) * np.sin(teta1)
                
            # Péndola
            epsilon = np.abs(np.arctan((y15 - y12) / (x15 - x12)))  # ángulo del tubo de péndola siempre positivo
            x14, x14bis, x13, x13bis = x15, x15, x12, x12
            y14, y14bis, y13, y13bis = y15, y15, y12, y12
            
            # Diagonal
            if grapa_diag_tir[0] >= 57:
                x33, y33 = 0, 0
                x32, y32 = 0, 0
                x32bis, y32bis = 0, 0
                x30, y30 = 0, 0
                x31, y31 = 0, 0
                x31bis, y31bis = 0, 0
            else:
                x33 = x34 + grapa_diag_men[0] * np.sin(teta1)
                y33 = y34 + grapa_diag_men[0] * np.cos(teta1)
                x30, y30 = x29, y29
                kappa = np.abs(np.arctan((y33 - y30) / (x33 - x30)))  # ángulo del tubo de péndola siempre positivo
                
                if x30 >= x33:
                    x32 = x33 + terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 + terminal_diag_men[1] * np.cos(kappa)
                else:
                    x32 = x33 - terminal_diag_men[0] * np.cos(kappa)
                    x32bis = x32 - terminal_diag_men[1] * np.cos(kappa)
                y32 = y33 + terminal_diag_men[0] * np.sin(kappa)
                y32bis = y32 + terminal_diag_men[1] * np.sin(kappa)
                
                if x30 >= x33:
                    x31 = x30 - terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 - terminal_diag_tir[1] * np.cos(kappa)
                else:
                    x31 = x30 + terminal_diag_tir[0] * np.cos(kappa)
                    x31bis = x31 + terminal_diag_tir[1] * np.cos(kappa)
                y31 = y30 - terminal_diag_tir[0] * np.sin(kappa)
                y31bis = y31 - terminal_diag_tir[1] * np.sin(kappa)
                
            # Comprobación de que se puede construir
            dist_compr_1 = np.sqrt(((x11 - x23)**2 + (y11 - y23)**2)+0j)  # Distancia para herrajes del estabilizador
            if dist_compr_1 < cota_seguridad_1 or x11 > x23:
                titulo = str(datos_postes[i])
                Mensulas_Calculo[i, 1] = 'No hay solución'
                warnings.warn(f'La mánsula no tiene solución. Cambiar parámetros - {titulo}')
                
            dist_compr_1_diag = np.sqrt(((x34 - x23)**2 + (y34 - y23)**2)+0j)  # Distancia para diagonal
            if dist_compr_1_diag < cota_seguridad_1 and x34 != x11:
                titulo = str(datos_postes[i])
                warnings.warn(f'La diagonal no entraría en la mánsula. Cambiar cota o colocar por arriba - {titulo}')
                
            # Almacenar todas las coordenadas
            coords = [
                [x0, y0], [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5], [x6, y6], [x7, y7], [x8, y8],
                [x9, y9], [x10, y10], [x11, y11], [x12, y12], [x13, y13], [x14, y14], [x15, y15], [x16, y16],
                [x17, y17], [x18, y18], [x19, y19], [x20, y20], [x22, y22], [x23, y23], [x24, y24], [x25, y25],
                [x26, y26], [x27, y27], [x28, y28], [x29, y29], [x30, y30], [x31, y31], [x32, y32], [x33, y33],
                [x34, y34], [x9bis, y9bis], [x17bis, y17bis], [x13bis, y13bis], [x14bis, y14bis], [x31bis, y31bis],
                [x32bis, y32bis], [xGM, yGM], [xGT, yGT], [xGMBis, yGMBis], [xGTBis, yGTBis], [xgalibo_poste, ygalibo_poste],
                [xbase_poste, ybase_poste], [xaltura_poste, yaltura_poste], [xbase_poste_atras, ybase_poste_atras],
                [xaltura_poste_atras, yaltura_poste_atras], [xba1, yba1], [xba2, yba2], [xba3, yba3]
            ]
            
            # Ajustar para lado izquierdo
            if lado_poste[i] == 'Izquierda':
                coords[:, 0] = -coords[:, 0]
                
            # Almacenar en la matriz de resultados
            #Coord_Mensulas_Calculo[:, 2*i-1:2*i] = coords
            #Coord_Mensulas_Calculo[:, 2*i : 2*i+1]=coords
            Coord_Mensulas_Calculo[:, 2*i : 2*i+2]=coords
        
        # ----------------------------------------------------------------------------Vertical----------------------------------------------------------------------------%
        ##ESTA PARTE NO ESTÁ TESTEADA YA QUE EN EL EJEMPLO QUE TENEMOS DE MONFORTE-LUGO NO USAN ESTE TIPO
        elif tipo_men[i] == 'B1' and Mensulas_Calculo[i, 1] == 'No hay solución':
                
            # Cargar datos de MATLAB
            ruta=os.path.join('Bibliotecas', 'Tipos de Ménsulas', nombre_men[i])
            herrajes_mensula_biblio = loadmat(ruta)
            grapas_vertical = herrajes_mensula_biblio['grapas_vertical']
            terminales_vertical = herrajes_mensula_biblio['terminales_vertical']
            parametros_vertical = herrajes_mensula_biblio['parametros_vertical'].flatten()
            otrosherrajes_vertical = herrajes_mensula_biblio['otrosherrajes_vertical']
            medidas_herrajes_mensula = herrajes_mensula_biblio['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_biblio['herrajes_mensula']

            # Extraer medidas específicas
            brazo_supsa=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_vertical[3])
            ais_tir=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_vertical[0])
            ais_men=obtener_medida(medidas_herrajes_mensula, herrajes_mensula, otrosherrajes_vertical[1])
            
            cota_fija_1 = parametros_vertical[0][0][0]
            cota_fija_2 = parametros_vertical[1][0][0]
            cota_fija_3 = parametros_vertical[2][0][0]
            cota_seguridad_1 = parametros_vertical[4][0][0]
            cota_seguridad_2 = parametros_vertical[5][0][0]

            # Cargar datos de postes y brazos
            ruta=os.path.join('Bibliotecas','Postes',tipo_poste[i])
            poste_mensula_biblio = loadmat(ruta)
            Lposte = poste_mensula_biblio['h']
            binf = poste_mensula_biblio['h0']
            bsup = poste_mensula_biblio['h1']

            ruta=os.path.join('Bibliotecas','Brazos de atirantado',tipo_brazo[i])
            brazo_mensula_biblio = loadmat(tipo_brazo[i])
            t_b = brazo_mensula_biblio['tipo'][0]  # Tipo de brazo
            
            # Configuración según tipo de brazo
            if t_b == 1:
                a, b, c = brazo_mensula_biblio['datos'][0:3]
                d, e, f = np.radians(brazo_mensula_biblio['datos'][3:6])
            elif t_b == 2:
                a, b, c, g, h = brazo_mensula_biblio['datos'][0:5]
                d, e, f = np.radians(brazo_mensula_biblio['datos'][5:8])
            elif t_b == 3:
                a, b, c, d = brazo_mensula_biblio['datos'][0:4]
                e, f = np.radians(brazo_mensula_biblio['datos'][4:6])

            # Cálculos de ángulos
            alfa = math.atan(peralte[i] / (Ancho_via + Carril))
            beta = abs(math.atan(Fv_hc[i] / Fr_hc[i]))
            beta_max = math.radians(parametros_vertical[3])
            
            if beta > beta_max:
                beta = beta_max
            
            elev_brazo = l_brazo[i] * math.sin(beta)
            x_brazo = l_brazo[i] * math.cos(beta)
            ganma = math.atan((binf/2 - bsup/2) / Lposte)
            delta = math.atan(despl[i] / 1000)

            # Sistema de coordenadas
            x0, y0 = 0, 0
            x1 = datos_alt[i] * math.sin(alfa) + datos_desc[i] * math.cos(alfa)
            y1 = datos_alt[i] * math.cos(alfa) - datos_desc[i] * math.sin(alfa) if alfa > 0 else datos_alt[i] * math.cos(alfa) + datos_desc[i] * math.sin(abs(alfa))
            
            x2, y2 = x1, y1 + alt_cat[i]
            x3, y3 = x1 + x_brazo, y1 + elev_brazo
            
            # Configuración de puntos según tipo de brazo
            if t_b == 1:
                xba1 = x1 - b * abs(math.cos(d - beta))
                yba1 = y1 + b * math.sin(d + beta)
                xba2 = x3 - c * abs(math.cos(e - beta))
                yba2 = y3 + c * math.sin(e - beta)
                xba3, yba3 = xba2, yba2
            elif t_b == 2:
                xba1 = x1 - b * abs(math.cos(d + beta))
                yba1 = y1 + b * math.sin(d + beta)
                xba2 = x3 - c * abs(math.cos(e - beta))
                yba2 = y3 + c * math.sin(e - beta)
                xba3 = xba2 - h * math.cos(math.pi/2 + beta - f)
                yba3 = yba2 - h * math.sin(math.pi/2 + beta - f)
            elif t_b == 3:
                xba1 = x1 + b * abs(math.cos(e + beta))
                yba1 = y1 + b * math.sin(e + beta)
                xba2 = x3 - c * math.cos(f - beta)
                yba2 = y3 + c * math.sin(f - beta)
                xba3, yba3 = xba2, yba2

            # Más coordenadas
            x4, y4 = x3 + brazo_supsa[0], y3
            x6, y6 = x4, y4 - cota_fija_1 - brazo_supsa[1]/2
            xgalibo_poste, ygalibo_poste = galibo[i], 0
            xbase_poste = xgalibo_poste - ht[i] * math.tan(ganma + delta)
            ybase_poste = ygalibo_poste - ht[i]
            xaltura_poste = xbase_poste + Lposte * math.tan(ganma + delta)
            yaltura_poste = ybase_poste + Lposte
            
            # Cálculo de pendientes
            mposte = abs((yaltura_poste - ybase_poste) / (xaltura_poste - xbase_poste)) if xaltura_poste != xbase_poste else float('inf')
            mgiros = 0 if mposte == float('inf') else -1/mposte

            # Posiciones de giros
            xGM = xbase_poste + alt_GM[i] * math.tan(ganma + delta)
            yGM = ybase_poste + alt_GM[i]
            xGT = xGM + dist_giros[i] * math.tan(ganma + delta)
            yGT = yGM + dist_giros[i]
            
            # Cálculos de distancias y comprobaciones
            dist_compr_1 = math.sqrt((x11 - x23)**2 + (y11 - y23)**2)
            if dist_compr_1 < cota_seguridad_1 or x7 > x28:
                Mensulas_Calculo[i, 1] = 'No hay solución'
            else:
                Mensulas_Calculo[i, 1] = 'Vertical'

            dist_compr_2 = math.sqrt((x7 - x28)**2 + (y7 - y28)**2)
            if dist_compr_2 < cota_seguridad_2 or x11 > x23:
                Mensulas_Calculo[i, 1] = 'No hay solución'
            else:
                Mensulas_Calculo[i, 1] = 'Vertical'

                # Crear la matriz de coordenadas
            coords = [
                [x0, y0], [x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5], [x6, y6], [x7, y7], [x8, y8],
                [x9, y9], [x10, y10], [x11, y11], [x12, y12], [x13, y13], [x14, y14], [x15, y15], [x16, y16],
                [x17, y17], [x18, y18], [x19, y19], [x20, y20], [x22, y22], [x23, y23], [x24, y24], [x25, y25],
                [x26, y26], [x27, y27], [x28, y28], [x29, y29], [x30, y30], [x31, y31], [x32, y32], [x33, y33],
                [x34, y34], [x9bis, y9bis], [x17bis, y17bis], [x13bis, y13bis], [x14bis, y14bis], [x31bis, y31bis],
                [x32bis, y32bis], [xGM, yGM], [xGT, yGT], [xGMBis, yGMBis], [xGTBis, yGTBis],
                [xgalibo_poste, ygalibo_poste], [xbase_poste, ybase_poste], [xaltura_poste, yaltura_poste],
                [xbase_poste_atras, ybase_poste_atras], [xaltura_poste_atras, yaltura_poste_atras],
                [xba1, yba1], [xba2, yba2], [xba3, yba3]
            ]

            # Verificación y cambio de coordenadas si el lado del poste es 'Izquierda'
            if lado_poste[i] == 'Izquierda':
                Coord_Mensulas_Calculo[:, 2*i-1] = -Coord_Mensulas_Calculo[:, 2*i-1]

            Coord_Mensulas_Calculo[:, 2*i : 2*i+2]=coords

    return Mensulas_Calculo, Coord_Mensulas_Calculo