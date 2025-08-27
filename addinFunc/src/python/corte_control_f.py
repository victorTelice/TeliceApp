import numpy as np
import math
import scipy.io as sio
import os
from tkinter import filedialog
import openpyxl
from openpyxl.styles import Border, Side, Font
from utils.logger import Logger 

def corte_control_f(Coord_Mensulas_Calculo, Mensulas_Calculo, tabla_datos_topografia, archivo_mensulas, dir_mensulas):
    
    Logger.add_to_log("llamada", "Llamada a la función Corte_control_f")

    tipo_atirantado = Mensulas_Calculo[:, 1]  # Columna 2 en MATLAB (índice 1 en Python)
    nombre_men = tabla_datos_topografia[:, 8]  # Columna 9 en MATLAB (índice 8 en Python) - Nombre de la biblioteca de la ménsula
    tipo_brazo = tabla_datos_topografia[:, 15]  # Columna 16 en MATLAB (índice 15 en Python)
    nombre_perfil = tabla_datos_topografia[:, 0]  # Columna 1 en MATLAB (índice 0 en Python)
    lado_perfil = tabla_datos_topografia[:, 3]  # Columna 4 en MATLAB (índice 3 en Python)
    
    # Inicializar listas para almacenar resultados
    num_mensulas = Mensulas_Calculo.shape[0]
    
    # Inicializar arrays/listas para diámetros y cortes
    diam_men = [None] * num_mensulas
    diam_tir = [None] * num_mensulas
    diam_estb = [None] * num_mensulas
    diam_pend = [None] * num_mensulas
    diam_diag = [None] * num_mensulas
    
    corte_mensula = [None] * num_mensulas
    corte_tirante = [None] * num_mensulas
    corte_estabilizador = [None] * num_mensulas
    corte_pendola = [None] * num_mensulas
    corte_diagonal = [None] * num_mensulas
    corte_supsa = [None] * num_mensulas
    corte_brazo = [None] * num_mensulas
    
    # Inicializar arrays/listas para comprobaciones
    comprobacion_mensula1 = [None] * num_mensulas
    comprobacion_mensula2 = [None] * num_mensulas
    comprobacion_mensula3 = [None] * num_mensulas
    comprobacion_tirante1 = [None] * num_mensulas
    comprobacion_tirante2 = [None] * num_mensulas
    comprobacion_estabilizador1 = [None] * num_mensulas
    comprobacion_estabilizador2 = [None] * num_mensulas
    comprobacion_pendola = [None] * num_mensulas
    comprobacion_diagonal = [None] * num_mensulas
    p_brz_supsa = [None] * num_mensulas
    
    herrajes_mensula_biblio = [None] * num_mensulas

    # Función auxiliar para extraer valores escalares de arrays anidados
    def extract_scalar(value):
        """Extrae un valor escalar de arrays anidados de NumPy"""
        if isinstance(value, np.ndarray):
            if value.size == 1:
                return value.item()
            elif value.size > 1:
                # Si es un array multidimensional, tomar el primer elemento
                return value.flat[0]
        return value

    # Función auxiliar para extraer valores de arrays indexados
    def extract_indexed_value(array, index):
        """Extrae un valor escalar de un array en un índice específico"""
        try:
            if isinstance(array, np.ndarray) and array.size > 0:
                # Para arrays con estructura: array([array([[valores...]], dtype=uint8)], dtype=object)
                inner_array = array[0]  # Acceder al array interno
                if isinstance(inner_array, np.ndarray) and inner_array.size > 0:
                    # Aplanar el array interno para obtener los valores
                    values = inner_array.flatten()
                    if len(values) > index:
                        return extract_scalar(values[index])
        except (IndexError, AttributeError, TypeError):
            pass
        return 0

    # Encuentra todas las medidas correspondientes
    def find_medidas(herrajes_list, target):
        for i, item in enumerate(herrajes_list.flatten()):
            if str(item).lower() == str(target).lower():
                result = medidas_herrajes_mensula[i]
                # Extraer valor escalar si es necesario
                if isinstance(result, np.ndarray):
                    return result
                return result
        return None
    
    # Aplana a una lista de strings
    def flat_lista(herrajes_cola):
        flat_list = []
        for item in herrajes_cola:
            if isinstance(item, np.ndarray):
                # Manejar arrays anidados
                if item.size > 0:
                    inner_item = item.flat[0]
                    if isinstance(inner_item, np.ndarray) and inner_item.size > 0:
                        flat_list.append(inner_item.flat[0])
                    else:
                        flat_list.append(inner_item)
                else:
                    flat_list.append(item)
            else:
                flat_list.append(item)
        return flat_list

    for j in range(num_mensulas):
        
        # LLAMADA A LOS HERRAJES DE CADA MÉNSULA
        
        ruta_mensula = os.path.join('Bibliotecas', 'Tipos de Ménsulas', nombre_men[j])

        if tipo_atirantado[j] == 'B1':
            
            herrajes_mensula_biblio[j] = sio.loadmat(ruta_mensula)
            
            grapas_b1 = herrajes_mensula_biblio[j]['grapas_b1']
            terminales_b1 = herrajes_mensula_biblio[j]['terminales_b1']
            parametros_b1 = herrajes_mensula_biblio[j]['parametros_b1']
            otrosherrajes_b1 = herrajes_mensula_biblio[j]['otrosherrajes_b1']
            medidas_herrajes_mensula = herrajes_mensula_biblio[j]['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_biblio[j]['herrajes_mensula']
            
            brazo_supsa = find_medidas(herrajes_mensula, otrosherrajes_b1[4][0])
            supsa = find_medidas(herrajes_mensula, otrosherrajes_b1[3][0])
            ais_tir = find_medidas(herrajes_mensula, otrosherrajes_b1[0][0])
            ais_men = find_medidas(herrajes_mensula, otrosherrajes_b1[1][0])
            
            # Extraer valores escalares de parámetros
            cota_fija_1 = extract_scalar(parametros_b1[0][0])
            cota_fija_2 = extract_scalar(parametros_b1[1][0])
            cota_fija_3 = extract_scalar(parametros_b1[2][0])
            cota_fija_4 = extract_scalar(parametros_b1[3][0])
            cota_fija_5 = extract_scalar(parametros_b1[4][0])
            cota_fija_6 = extract_scalar(parametros_b1[5][0])
            cota_fija_7 = extract_scalar(parametros_b1[6][0])
            cota_seguridad_1 = extract_scalar(parametros_b1[9][0])
            cota_seguridad_2 = extract_scalar(parametros_b1[10][0])
            
            grapa_men_estab = find_medidas(herrajes_mensula, grapas_b1[1][0])
            grapa_pend_men = find_medidas(herrajes_mensula, grapas_b1[2][0])
            grapa_pend_estab = find_medidas(herrajes_mensula, grapas_b1[3][0])
            grapa_u_tirmen = find_medidas(herrajes_mensula, grapas_b1[0][0])
            grapa_diag_tir = find_medidas(herrajes_mensula, grapas_b1[5][0])
            grapa_diag_men = find_medidas(herrajes_mensula, grapas_b1[4][0])
            
            terminal_men = find_medidas(herrajes_mensula, terminales_b1[0][0])
            terminal_estab = find_medidas(herrajes_mensula, terminales_b1[1][0])
            terminal_pend_men = find_medidas(herrajes_mensula, terminales_b1[2][0])
            terminal_pend_estab = find_medidas(herrajes_mensula, terminales_b1[3][0])
            terminal_diag_men = find_medidas(herrajes_mensula, terminales_b1[4][0])
            terminal_diag_tir = find_medidas(herrajes_mensula, terminales_b1[5][0])
            
            BS = find_medidas(herrajes_mensula, otrosherrajes_b1[2][0])
        
        elif tipo_atirantado[j] == 'B2':
            
            herrajes_mensula_biblio[j] = sio.loadmat(ruta_mensula)
            
            grapas_b2 = herrajes_mensula_biblio[j]['grapas_b2']
            terminales_b2 = herrajes_mensula_biblio[j]['terminales_b2']
            parametros_b2 = herrajes_mensula_biblio[j]['parametros_b2']
            otrosherrajes_b2 = herrajes_mensula_biblio[j]['otrosherrajes_b2']
            medidas_herrajes_mensula = herrajes_mensula_biblio[j]['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_biblio[j]['herrajes_mensula']
            
            brazo_supsa = find_medidas(herrajes_mensula, otrosherrajes_b2[4][0])
            supsa = find_medidas(herrajes_mensula, otrosherrajes_b2[3][0])
            ais_tir = find_medidas(herrajes_mensula, otrosherrajes_b2[0][0])
            ais_men = find_medidas(herrajes_mensula, otrosherrajes_b2[1][0])
            
            # Extraer valores escalares de parámetros
            cota_fija_1 = extract_scalar(parametros_b2[0][0])
            cota_fija_2 = extract_scalar(parametros_b2[1][0])
            cota_fija_3 = extract_scalar(parametros_b2[2][0])
            cota_fija_4 = extract_scalar(parametros_b2[3][0])
            cota_fija_5 = extract_scalar(parametros_b2[4][0])
            cota_fija_6 = extract_scalar(parametros_b2[5][0])
            cota_fija_7 = extract_scalar(parametros_b2[6][0])
            cota_seguridad_1 = extract_scalar(parametros_b2[9][0])
            
            grapa_men_estab = find_medidas(herrajes_mensula, grapas_b2[1][0])
            grapa_pend_men = find_medidas(herrajes_mensula, grapas_b2[2][0])
            grapa_pend_estab = find_medidas(herrajes_mensula, grapas_b2[3][0])
            grapa_u_tirmen = find_medidas(herrajes_mensula, grapas_b2[0][0])
            grapa_diag_tir = find_medidas(herrajes_mensula, grapas_b2[5][0])
            grapa_diag_men = find_medidas(herrajes_mensula, grapas_b2[4][0])
            
            terminal_men = find_medidas(herrajes_mensula, terminales_b2[0][0])
            terminal_estab = find_medidas(herrajes_mensula, terminales_b2[1][0])
            terminal_pend_men = find_medidas(herrajes_mensula, terminales_b2[2][0])
            terminal_pend_estab = find_medidas(herrajes_mensula, terminales_b2[3][0])
            terminal_diag_men = find_medidas(herrajes_mensula, terminales_b2[4][0])
            terminal_diag_tir = find_medidas(herrajes_mensula, terminales_b2[5][0])
            
            BS = find_medidas(herrajes_mensula, otrosherrajes_b2[2][0])
        
        elif tipo_atirantado[j] == 'Elevación':
            
            herrajes_mensula_biblio[j] = sio.loadmat(ruta_mensula)
            
            grapas_cola = herrajes_mensula_biblio[j]['grapas_cola']
            terminales_cola = herrajes_mensula_biblio[j]['terminales_cola']
            parametros_cola = herrajes_mensula_biblio[j]['parametros_cola']
            otrosherrajes_cola = herrajes_mensula_biblio[j]['otrosherrajes_cola']
            medidas_herrajes_mensula = herrajes_mensula_biblio[j]['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_biblio[j]['herrajes_mensula']

            otrosherrajes_cola_flat = flat_lista(otrosherrajes_cola)

            anclaje_hc = find_medidas(herrajes_mensula, otrosherrajes_cola_flat[3])
            ais_tir = find_medidas(herrajes_mensula, otrosherrajes_cola_flat[0])
            ais_men = find_medidas(herrajes_mensula, otrosherrajes_cola_flat[1])
            
            # Extraer valores escalares de parámetros
            cota_fija_1 = extract_scalar(parametros_cola[0][0])
            cota_fija_2 = extract_scalar(parametros_cola[1][0])
            cota_fija_3 = extract_scalar(parametros_cola[2][0])
            cota_fija_4 = extract_scalar(parametros_cola[3][0])
            cota_fija_5 = extract_scalar(parametros_cola[4][0])
            cota_fija_6 = extract_scalar(parametros_cola[5][0])
            cota_fija_7 = extract_scalar(parametros_cola[6][0])
            cota_seguridad_1 = extract_scalar(parametros_cola[8][0])
            
            grapa_men_estab = find_medidas(herrajes_mensula, grapas_cola[1][0])
            grapa_pend_men = find_medidas(herrajes_mensula, grapas_cola[2][0])
            grapa_pend_estab = find_medidas(herrajes_mensula, grapas_cola[3][0])
            grapa_u_tirmen = find_medidas(herrajes_mensula, grapas_cola[0][0])
            grapa_diag_tir = find_medidas(herrajes_mensula, grapas_cola[5][0])
            grapa_diag_men = find_medidas(herrajes_mensula, grapas_cola[4][0])
            
            terminal_men = find_medidas(herrajes_mensula, terminales_cola[0][0])
            terminal_estab = find_medidas(herrajes_mensula, terminales_cola[1][0])
            terminal_pend_men = find_medidas(herrajes_mensula, terminales_cola[2][0])
            terminal_pend_estab = find_medidas(herrajes_mensula, terminales_cola[3][0])
            terminal_diag_men = find_medidas(herrajes_mensula, terminales_cola[4][0])
            terminal_diag_tir = find_medidas(herrajes_mensula, terminales_cola[5][0])
            
            BS = find_medidas(herrajes_mensula, otrosherrajes_cola[2][0])
        
        elif tipo_atirantado[j] == 'Vertical':
            
            herrajes_mensula_biblio[j] = sio.loadmat(ruta_mensula)
            
            grapas_vertical = herrajes_mensula_biblio[j]['grapas_vertical']
            terminales_vertical = herrajes_mensula_biblio[j]['terminales_vertical']
            parametros_vertical = herrajes_mensula_biblio[j]['parametros_vertical']
            otrosherrajes_vertical = herrajes_mensula_biblio[j]['otrosherrajes_vertical']
            medidas_herrajes_mensula = herrajes_mensula_biblio[j]['medidas_herrajes_mensula']
            herrajes_mensula = herrajes_mensula_biblio[j]['herrajes_mensula']
            
            brazo_supsa = find_medidas(herrajes_mensula, otrosherrajes_vertical[3][0])
            ais_tir = find_medidas(herrajes_mensula, otrosherrajes_vertical[0][0])
            ais_men = find_medidas(herrajes_mensula, otrosherrajes_vertical[1][0])
            
            # Extraer valores escalares de parámetros
            cota_fija_1 = extract_scalar(parametros_vertical[0][0])
            cota_fija_2 = extract_scalar(parametros_vertical[1][0])
            cota_fija_3 = extract_scalar(parametros_vertical[2][0])
            cota_seguridad_1 = extract_scalar(parametros_vertical[4][0])
            cota_seguridad_2 = extract_scalar(parametros_vertical[5][0])
            
            grapa_u_tirmen = find_medidas(herrajes_mensula, grapas_vertical[0][0])
            grapa_union_tir_estab = find_medidas(herrajes_mensula, grapas_vertical[1][0])
            grapa_union_men_estab = find_medidas(herrajes_mensula, grapas_vertical[2][0])
            grapa_union_estab_tir = find_medidas(herrajes_mensula, grapas_vertical[3][0])
            grapa_union_estab_men = find_medidas(herrajes_mensula, grapas_vertical[4][0])
            terminal_men = find_medidas(herrajes_mensula, terminales_vertical[0][0])
            
            BS = find_medidas(herrajes_mensula, otrosherrajes_vertical[2][0])
        
        # ---------------------------------CORTE--------------------------
        # Diámetros tubos
        
        if tipo_atirantado[j] == 'No hay ménsula':
            diam_men[j] = '-'
            diam_tir[j] = '-'
            diam_estb[j] = '-'
            diam_pend[j] = '-'
            diam_diag[j] = '-'
        
        elif tipo_atirantado[j] == 'B1':
            diam_men[j] = extract_scalar(grapas_b1[1, 0])
            diam_tir[j] = extract_scalar(grapas_b1[0, 0])
            diam_estb[j] = extract_scalar(grapas_b1[3, 0])
            diam_pend[j] = extract_scalar(terminales_b1[3, 0])
            
            if Coord_Mensulas_Calculo[28, 2*j] == 0:  # No hay diagonal
                diam_diag[j] = 'No hay diagonal'
            else:
                diam_diag[j] = extract_scalar(terminales_b1[4, 0])
        
        elif tipo_atirantado[j] == 'B2':
            diam_men[j] = extract_scalar(grapas_b2[1, 0])
            diam_tir[j] = extract_scalar(grapas_b2[0, 0])
            diam_estb[j] = extract_scalar(grapas_b2[3, 0])
            diam_pend[j] = 'PA - FLEX'
            
            if Coord_Mensulas_Calculo[28, 2*j] == 0:  # No hay diagonal
                diam_diag[j] = 'No hay diagonal'
            else:
                diam_diag[j] = extract_scalar(terminales_b2[4, 0])
        
        elif tipo_atirantado[j] == 'Elevación':
            diam_men[j] = extract_scalar(grapas_cola[1, 0])
            diam_tir[j] = extract_scalar(grapas_cola[0, 0])
            diam_estb[j] = extract_scalar(grapas_cola[3, 0])
            diam_pend[j] = 'PA - FLEX'
            
            if Coord_Mensulas_Calculo[28, 2*j] == 0:  # No hay diagonal
                diam_diag[j] = 'No hay diagonal'
            else:
                diam_diag[j] = extract_scalar(terminales_cola[4, 0])
        
        elif tipo_atirantado[j] == 'Vertical':
            diam_men[j] = extract_scalar(grapas_vertical[2, 0])
            diam_tir[j] = extract_scalar(grapas_vertical[0, 0])
            diam_estb[j] = extract_scalar(grapas_vertical[4, 0])
            diam_pend[j] = 'No hay péndola'
            diam_diag[j] = 'No hay diagonal'
        
        # Corte tubo de ménsula
        if tipo_atirantado[j] == 'No hay ménsula':
            corte_mensula[j] = '-'
        else:
            corte_mensula[j] = math.sqrt((Coord_Mensulas_Calculo[35, 2*j] - Coord_Mensulas_Calculo[23, 2*j])**2 + 
                                       (Coord_Mensulas_Calculo[35, 2*j+1] - Coord_Mensulas_Calculo[23, 2*j+1])**2)
        
        # Corte tubo de tirante
        if tipo_atirantado[j] == 'No hay ménsula':
            corte_tirante[j] = '-'
        else:
            corte_tirante[j] = math.sqrt((Coord_Mensulas_Calculo[21, 2*j] - Coord_Mensulas_Calculo[27, 2*j])**2 + 
                                       (Coord_Mensulas_Calculo[21, 2*j+1] - Coord_Mensulas_Calculo[27, 2*j+1])**2)
        
        # Corte tubo estabilizador
        if tipo_atirantado[j] == 'No hay ménsula':
            corte_estabilizador[j] = '-'
        else:
            corte_estabilizador[j] = math.sqrt((Coord_Mensulas_Calculo[9, 2*j] - Coord_Mensulas_Calculo[8, 2*j])**2 + 
                                             (Coord_Mensulas_Calculo[9, 2*j+1] - Coord_Mensulas_Calculo[8, 2*j+1])**2)
        
        if tipo_atirantado[j] == 'Vertical':
            corte_estabilizador[j] = math.sqrt((Coord_Mensulas_Calculo[8, 2*j] - Coord_Mensulas_Calculo[6, 2*j])**2 + 
                                             (Coord_Mensulas_Calculo[8, 2*j+1] - Coord_Mensulas_Calculo[6, 2*j+1])**2)
        
        # Corte tubo péndola
        if tipo_atirantado[j] == 'Vertical':
            corte_pendola[j] = 'No tiene'
        elif tipo_atirantado[j] == 'No hay ménsula':
            corte_pendola[j] = '-'
        else:
            corte_pendola[j] = math.sqrt((Coord_Mensulas_Calculo[14, 2*j] - Coord_Mensulas_Calculo[13, 2*j])**2 + 
                                       (Coord_Mensulas_Calculo[14, 2*j+1] - Coord_Mensulas_Calculo[13, 2*j+1])**2)
        
        # Corte tubo diagonal
        dist_diagonal = math.sqrt((Coord_Mensulas_Calculo[31, 2*j] - Coord_Mensulas_Calculo[30, 2*j])**2 + 
                                (Coord_Mensulas_Calculo[31, 2*j+1] - Coord_Mensulas_Calculo[30, 2*j+1])**2)
        
        if dist_diagonal == 0:
            corte_diagonal[j] = 'No tiene'
        elif tipo_atirantado[j] == 'No hay ménsula':
            corte_diagonal[j] = '-'
        else:
            corte_diagonal[j] = dist_diagonal
        
        # Corte SUPSA
        # LA SUPSA EN LAS MÉNSULAS MNF ES UNA PIEZA MÁS POR LO QUE NO ES UN CORTE
        
        if tipo_atirantado[j] == 'No hay ménsula':
            corte_supsa[j] = '-'
        elif tipo_atirantado[j] == 'B1':
            corte_supsa[j] = extract_scalar(otrosherrajes_b1[3, 0])
        elif tipo_atirantado[j] == 'B2':
            corte_supsa[j] = extract_scalar(otrosherrajes_b2[3, 0])
        elif tipo_atirantado[j] == 'Elevación':
            corte_supsa[j] = 'No hay supsa'
        elif tipo_atirantado[j] == 'Vertical':
            corte_supsa[j] = 'No hay supsa'
        
        # Tipo de brazo
        if tipo_atirantado[j] == 'No hay ménsula':
            corte_brazo[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2']:
            corte_brazo[j] = tipo_brazo[j]
        elif tipo_atirantado[j] == 'Elevación':
            corte_brazo[j] = 'Anclaje HC'
        elif tipo_atirantado[j] == 'Vertical':
            corte_brazo[j] = tipo_brazo[j]
        
        # ---------------------------------CONTROL--------------------------
        # Comprobación tubo de ménsula1 CONTROL D
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_mensula1[j] = '-'
        else:
            comprobacion_mensula1[j] = math.sqrt((Coord_Mensulas_Calculo[35, 2*j] - Coord_Mensulas_Calculo[22, 2*j])**2 + 
                                               (Coord_Mensulas_Calculo[35, 2*j+1] - Coord_Mensulas_Calculo[22, 2*j+1])**2)
        
        # Comprobaciones tubo de ménsula2 CONTROL C
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_mensula2[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2', 'Elevación']:
            grapa_value = extract_indexed_value(grapa_men_estab, 1)
            comprobacion_mensula2[j] = (math.sqrt((Coord_Mensulas_Calculo[22, 2*j] - Coord_Mensulas_Calculo[11, 2*j])**2 + 
                                                (Coord_Mensulas_Calculo[22, 2*j+1] - Coord_Mensulas_Calculo[11, 2*j+1])**2) - 
                                      grapa_value/2)
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Derecha':
            m_men = ((Coord_Mensulas_Calculo[5, 2*j+1] - Coord_Mensulas_Calculo[22, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[5, 2*j] - Coord_Mensulas_Calculo[22, 2*j]))
            alfa_men = math.atan(m_men)
            alfa_men_prima = alfa_men - math.pi/2
            grapa_union_men_estab_val = extract_indexed_value(grapa_union_men_estab, 0)
            grapa_union_estab_men_val0 = extract_indexed_value(grapa_union_estab_men, 0)
            grapa_union_estab_men_val2 = extract_indexed_value(grapa_union_estab_men, 2)
            
            x_aux1 = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux1 = Coord_Mensulas_Calculo[5, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_aux2 = Coord_Mensulas_Calculo[22, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux2 = Coord_Mensulas_Calculo[22, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_cinco_prima = Coord_Mensulas_Calculo[5, 2*j] - grapa_union_estab_men_val0
            y_cinco_prima = (((Coord_Mensulas_Calculo[5, 2*j] - grapa_union_estab_men_val0) - x_aux1) * 
                           (y_aux2 - y_aux1) / (x_aux2 - x_aux1) + y_aux1)
            comprobacion_mensula2[j] = (math.sqrt((Coord_Mensulas_Calculo[22, 2*j] - x_cinco_prima)**2 + 
                                                (Coord_Mensulas_Calculo[22, 2*j+1] - y_cinco_prima)**2) + 
                                      grapa_union_estab_men_val2)
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Izquierda':
            m_men = ((Coord_Mensulas_Calculo[5, 2*j+1] - Coord_Mensulas_Calculo[22, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[5, 2*j] - Coord_Mensulas_Calculo[22, 2*j]))
            alfa_men = math.atan(m_men)
            alfa_men_prima = alfa_men - math.pi/2
            grapa_union_men_estab_val = extract_indexed_value(grapa_union_men_estab, 0)
            grapa_union_estab_men_val0 = extract_indexed_value(grapa_union_estab_men, 0)
            grapa_union_estab_men_val2 = extract_indexed_value(grapa_union_estab_men, 2)
            
            x_aux1 = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux1 = Coord_Mensulas_Calculo[5, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_aux2 = Coord_Mensulas_Calculo[22, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux2 = Coord_Mensulas_Calculo[22, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_cinco_prima = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_estab_men_val0
            y_cinco_prima = (((Coord_Mensulas_Calculo[5, 2*j] + grapa_union_estab_men_val0) - x_aux1) * 
                           (y_aux2 - y_aux1) / (x_aux2 - x_aux1) + y_aux1)
            comprobacion_mensula2[j] = (math.sqrt((Coord_Mensulas_Calculo[22, 2*j] - x_cinco_prima)**2 + 
                                                (Coord_Mensulas_Calculo[22, 2*j+1] - y_cinco_prima)**2) + 
                                      grapa_union_estab_men_val2)
        
        # Comprobaciones tubo de ménsula3 CONTROL D - AQUÍ SI CALCULA BIEN EL CONTROL D
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_mensula3[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2', 'Elevación']:
            if Coord_Mensulas_Calculo[28, 2*j] == 0:  # No hay diagonal
                comprobacion_mensula3[j] = 'No hay diagonal'
            else:
                grapa_diag_men_val = extract_indexed_value(grapa_diag_men, 1)
                comprobacion_mensula3[j] = (math.sqrt((Coord_Mensulas_Calculo[22, 2*j] - Coord_Mensulas_Calculo[33, 2*j])**2 + 
                                                    (Coord_Mensulas_Calculo[22, 2*j+1] - Coord_Mensulas_Calculo[33, 2*j+1])**2) - 
                                          grapa_diag_men_val/2)
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Derecha':
            m_tir = ((Coord_Mensulas_Calculo[7, 2*j+1] - Coord_Mensulas_Calculo[27, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[7, 2*j] - Coord_Mensulas_Calculo[27, 2*j]))
            alfa_tir = math.atan(m_tir)
            alfa_tir_prima = alfa_tir - math.pi/2
            grapa_union_tir_estab_val = extract_indexed_value(grapa_union_tir_estab, 0)
            grapa_union_estab_tir_val0 = extract_indexed_value(grapa_union_estab_tir, 0)
            grapa_union_estab_tir_val2 = extract_indexed_value(grapa_union_estab_tir, 2)
            
            x_aux3 = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux3 = Coord_Mensulas_Calculo[7, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_aux4 = Coord_Mensulas_Calculo[27, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux4 = Coord_Mensulas_Calculo[27, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_siete_prima = Coord_Mensulas_Calculo[7, 2*j] - grapa_union_estab_tir_val0
            y_siete_prima = (((Coord_Mensulas_Calculo[7, 2*j] - grapa_union_estab_tir_val0) - x_aux3) * 
                           (y_aux4 - y_aux3) / (x_aux4 - x_aux3) + y_aux3)
            comprobacion_mensula3[j] = (math.sqrt((Coord_Mensulas_Calculo[27, 2*j] - x_siete_prima)**2 + 
                                                (Coord_Mensulas_Calculo[27, 2*j+1] - y_siete_prima)**2) + 
                                      grapa_union_estab_tir_val2)
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Izquierda':
            m_tir = ((Coord_Mensulas_Calculo[7, 2*j+1] - Coord_Mensulas_Calculo[27, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[7, 2*j] - Coord_Mensulas_Calculo[27, 2*j]))
            alfa_tir = math.atan(m_tir)
            alfa_tir_prima = alfa_tir - math.pi/2
            grapa_union_tir_estab_val = extract_indexed_value(grapa_union_tir_estab, 0)
            grapa_union_estab_tir_val0 = extract_indexed_value(grapa_union_estab_tir, 0)
            grapa_union_estab_tir_val2 = extract_indexed_value(grapa_union_estab_tir, 2)
            
            x_aux3 = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux3 = Coord_Mensulas_Calculo[7, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_aux4 = Coord_Mensulas_Calculo[27, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux4 = Coord_Mensulas_Calculo[27, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_siete_prima = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_estab_tir_val0
            y_siete_prima = (((Coord_Mensulas_Calculo[7, 2*j] + grapa_union_estab_tir_val0) - x_aux3) * 
                           (y_aux4 - y_aux3) / (x_aux4 - x_aux3) + y_aux3)
            comprobacion_mensula3[j] = (math.sqrt((Coord_Mensulas_Calculo[27, 2*j] - x_siete_prima)**2 + 
                                                (Coord_Mensulas_Calculo[27, 2*j+1] - y_siete_prima)**2) + 
                                      grapa_union_estab_tir_val2)
        
        # Comprobaciones tubo de tirante1 CONTROL A
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_tirante1[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2', 'Elevación']:
            grapa_u_tirmen_val = extract_indexed_value(grapa_u_tirmen, 1)
            grapa_diag_tir_val = extract_indexed_value(grapa_diag_tir, 1)
            comprobacion_tirante1[j] = (math.sqrt((Coord_Mensulas_Calculo[27, 2*j] - Coord_Mensulas_Calculo[19, 2*j])**2 + 
                                                (Coord_Mensulas_Calculo[27, 2*j+1] - Coord_Mensulas_Calculo[19, 2*j+1])**2) - 
                                      grapa_u_tirmen_val/2 - grapa_diag_tir_val)
            a = grapa_u_tirmen_val; aa = grapa_diag_tir_val
        elif tipo_atirantado[j] == 'Vertical':
            grapa_u_tirmen_val = extract_indexed_value(grapa_u_tirmen, 1)
            grapa_diag_tir_val = extract_indexed_value(grapa_diag_tir, 1)
            comprobacion_tirante1[j] = (math.sqrt((Coord_Mensulas_Calculo[27, 2*j] - Coord_Mensulas_Calculo[19, 2*j])**2 + 
                                                (Coord_Mensulas_Calculo[27, 2*j+1] - Coord_Mensulas_Calculo[19, 2*j+1])**2) - 
                                      grapa_u_tirmen_val/2 - grapa_diag_tir_val)
        
        # Comprobaciones tubo de tirante2 CONTROL B
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_tirante2[j] = '-'
        else:
            BS_val = extract_indexed_value(BS, 1)
            grapa_diag_tir_val = extract_indexed_value(grapa_diag_tir, 1)
            comprobacion_tirante2[j] = (math.sqrt((Coord_Mensulas_Calculo[27, 2*j] - Coord_Mensulas_Calculo[20, 2*j])**2 + 
                                                (Coord_Mensulas_Calculo[27, 2*j+1] - Coord_Mensulas_Calculo[20, 2*j+1])**2) - 
                                      BS_val/2 - grapa_diag_tir_val)
        
        # Comprobación tubo estabilizador1 CONTROL E
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_estabilizador1[j] = '-'
        elif tipo_atirantado[j] == 'B1':
            supsa_val = extract_indexed_value(supsa, 2)
            comprobacion_estabilizador1[j] = (math.sqrt((Coord_Mensulas_Calculo[34, 2*j] - Coord_Mensulas_Calculo[5, 2*j])**2 + 
                                                       (Coord_Mensulas_Calculo[34, 2*j+1] - Coord_Mensulas_Calculo[5, 2*j+1])**2) - 
                                            supsa_val/2 + 8)
        elif tipo_atirantado[j] == 'B2':
            supsa_val = extract_indexed_value(supsa, 2)
            comprobacion_estabilizador1[j] = (math.sqrt((Coord_Mensulas_Calculo[34, 2*j] - Coord_Mensulas_Calculo[5, 2*j])**2 + 
                                                       (Coord_Mensulas_Calculo[34, 2*j+1] - Coord_Mensulas_Calculo[5, 2*j+1])**2) - 
                                            supsa_val/2 - 8)
        elif tipo_atirantado[j] == 'Elevación':
            anclaje_hc_val1 = extract_indexed_value(anclaje_hc, 1)
            anclaje_hc_val2 = extract_indexed_value(anclaje_hc, 2)
            comprobacion_estabilizador1[j] = (math.sqrt((Coord_Mensulas_Calculo[34, 2*j] - Coord_Mensulas_Calculo[5, 2*j])**2 + 
                                                       (Coord_Mensulas_Calculo[34, 2*j+1] - Coord_Mensulas_Calculo[5, 2*j+1])**2) - 
                                            (anclaje_hc_val1 - anclaje_hc_val2))
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Derecha':
            m_men = ((Coord_Mensulas_Calculo[5, 2*j+1] - Coord_Mensulas_Calculo[22, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[5, 2*j] - Coord_Mensulas_Calculo[22, 2*j]))
            alfa_men = math.atan(m_men)
            alfa_men_prima = alfa_men - math.pi/2
            grapa_union_men_estab_val = extract_indexed_value(grapa_union_men_estab, 0)
            grapa_union_estab_men_val0 = extract_indexed_value(grapa_union_estab_men, 0)
            grapa_union_estab_men_val2 = extract_indexed_value(grapa_union_estab_men, 2)
            
            x_aux1 = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux1 = Coord_Mensulas_Calculo[5, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_aux2 = Coord_Mensulas_Calculo[22, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux2 = Coord_Mensulas_Calculo[22, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_cinco_prima = Coord_Mensulas_Calculo[5, 2*j] - grapa_union_estab_men_val0
            y_cinco_prima = (((Coord_Mensulas_Calculo[5, 2*j] - grapa_union_estab_men_val0) - x_aux1) * 
                           (y_aux2 - y_aux1) / (x_aux2 - x_aux1) + y_aux1)
            comprobacion_estabilizador1[j] = y_cinco_prima - Coord_Mensulas_Calculo[6, 2*j+1] - grapa_union_estab_men_val2
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Izquierda':
            m_men = ((Coord_Mensulas_Calculo[5, 2*j+1] - Coord_Mensulas_Calculo[22, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[5, 2*j] - Coord_Mensulas_Calculo[22, 2*j]))
            alfa_men = math.atan(m_men)
            alfa_men_prima = alfa_men - math.pi/2
            grapa_union_men_estab_val = extract_indexed_value(grapa_union_men_estab, 0)
            grapa_union_estab_men_val0 = extract_indexed_value(grapa_union_estab_men, 0)
            grapa_union_estab_men_val2 = extract_indexed_value(grapa_union_estab_men, 2)
            
            x_aux1 = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux1 = Coord_Mensulas_Calculo[5, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_aux2 = Coord_Mensulas_Calculo[22, 2*j] + grapa_union_men_estab_val * math.cos(alfa_men_prima)
            y_aux2 = Coord_Mensulas_Calculo[22, 2*j+1] + grapa_union_men_estab_val * math.sin(alfa_men_prima)
            x_cinco_prima = Coord_Mensulas_Calculo[5, 2*j] + grapa_union_estab_men_val0
            y_cinco_prima = (((Coord_Mensulas_Calculo[5, 2*j] + grapa_union_estab_men_val0) - x_aux1) * 
                           (y_aux2 - y_aux1) / (x_aux2 - x_aux1) + y_aux1)
            comprobacion_estabilizador1[j] = y_cinco_prima - Coord_Mensulas_Calculo[6, 2*j+1] - grapa_union_estab_men_val2
        
        # Comprobación tubo estabilizador2 CONTROL G
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_estabilizador2[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2', 'Elevación']:
            grapa_pend_estab_val = extract_indexed_value(grapa_pend_estab, 1)
            comprobacion_estabilizador2[j] = (math.sqrt((Coord_Mensulas_Calculo[34, 2*j] - Coord_Mensulas_Calculo[7, 2*j])**2 + 
                                                       (Coord_Mensulas_Calculo[34, 2*j+1] - Coord_Mensulas_Calculo[7, 2*j+1])**2) - 
                                            grapa_pend_estab_val/2)
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Derecha':
            m_tir = ((Coord_Mensulas_Calculo[7, 2*j+1] - Coord_Mensulas_Calculo[27, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[7, 2*j] - Coord_Mensulas_Calculo[27, 2*j]))
            alfa_tir = math.atan(m_tir)
            alfa_tir_prima = alfa_tir - math.pi/2
            grapa_union_tir_estab_val = extract_indexed_value(grapa_union_tir_estab, 0)
            grapa_union_estab_tir_val0 = extract_indexed_value(grapa_union_estab_tir, 0)
            grapa_union_estab_tir_val2 = extract_indexed_value(grapa_union_estab_tir, 2)
            
            x_aux3 = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux3 = Coord_Mensulas_Calculo[7, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_aux4 = Coord_Mensulas_Calculo[27, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux4 = Coord_Mensulas_Calculo[27, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_siete_prima = Coord_Mensulas_Calculo[7, 2*j] - grapa_union_estab_tir_val0
            y_siete_prima = (((Coord_Mensulas_Calculo[7, 2*j] - grapa_union_estab_tir_val0) - x_aux3) * 
                           (y_aux4 - y_aux3) / (x_aux4 - x_aux3) + y_aux3)
            comprobacion_estabilizador2[j] = y_siete_prima - Coord_Mensulas_Calculo[6, 2*j+1] - grapa_union_estab_tir_val2
        elif tipo_atirantado[j] == 'Vertical' and lado_perfil[j] == 'Izquierda':
            m_tir = ((Coord_Mensulas_Calculo[7, 2*j+1] - Coord_Mensulas_Calculo[27, 2*j+1]) / 
                    (Coord_Mensulas_Calculo[7, 2*j] - Coord_Mensulas_Calculo[27, 2*j]))
            alfa_tir = math.atan(m_tir)
            alfa_tir_prima = alfa_tir - math.pi/2
            grapa_union_tir_estab_val = extract_indexed_value(grapa_union_tir_estab, 0)
            grapa_union_estab_tir_val0 = extract_indexed_value(grapa_union_estab_tir, 0)
            grapa_union_estab_tir_val2 = extract_indexed_value(grapa_union_estab_tir, 2)
            
            x_aux3 = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux3 = Coord_Mensulas_Calculo[7, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_aux4 = Coord_Mensulas_Calculo[27, 2*j] + grapa_union_tir_estab_val * math.cos(alfa_tir_prima)
            y_aux4 = Coord_Mensulas_Calculo[27, 2*j+1] + grapa_union_tir_estab_val * math.sin(alfa_tir_prima)
            x_siete_prima = Coord_Mensulas_Calculo[7, 2*j] + grapa_union_estab_tir_val0
            y_siete_prima = (((Coord_Mensulas_Calculo[7, 2*j] + grapa_union_estab_tir_val0) - x_aux3) * 
                           (y_aux4 - y_aux3) / (x_aux4 - x_aux3) + y_aux3)
            comprobacion_estabilizador2[j] = y_siete_prima - Coord_Mensulas_Calculo[6, 2*j+1] - grapa_union_estab_tir_val2
        
        # Comprobación tubo péndola CONTROL P
        if tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_pendola[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2', 'Elevación']:
            comprobacion_pendola[j] = math.sqrt((Coord_Mensulas_Calculo[37, 2*j] - Coord_Mensulas_Calculo[36, 2*j])**2 + 
                                              (Coord_Mensulas_Calculo[37, 2*j+1] - Coord_Mensulas_Calculo[36, 2*j+1])**2)
        elif tipo_atirantado[j] == 'Vertical':
            comprobacion_pendola[j] = 'No hay pendola'
        
        # Comprobación tubo diagonal CONTROL Diag
        if tipo_atirantado[j] == 'Vertical':
            comprobacion_diagonal[j] = 'No hay diagonal'
        elif tipo_atirantado[j] == 'No hay ménsula':
            comprobacion_diagonal[j] = '-'
        else:
            if Coord_Mensulas_Calculo[28, 2*j] == 0:  # No hay diagonal
                comprobacion_diagonal[j] = 'No hay diagonal'
            else:
                comprobacion_diagonal[j] = math.sqrt((Coord_Mensulas_Calculo[39, 2*j] - Coord_Mensulas_Calculo[38, 2*j])**2 + 
                                                   (Coord_Mensulas_Calculo[39, 2*j+1] - Coord_Mensulas_Calculo[38, 2*j+1])**2)
        
        # Posición del brazo en la supsa CONTROL bAt
        if tipo_atirantado[j] == 'No hay ménsula':
            p_brz_supsa[j] = '-'
        elif tipo_atirantado[j] == 'Vertical':
            p_brz_supsa[j] = '-'
        elif tipo_atirantado[j] in ['B1', 'B2']:
            p_brz_supsa[j] = (math.sqrt((Coord_Mensulas_Calculo[6, 2*j] - Coord_Mensulas_Calculo[4, 2*j])**2 + 
                                      (Coord_Mensulas_Calculo[6, 2*j+1] - Coord_Mensulas_Calculo[4, 2*j+1])**2) - 5)
        elif tipo_atirantado[j] == 'Elevación':
            p_brz_supsa[j] = '-'
    
    # Crear las tablas finales
    TABLA_CORTE = np.array([
        nombre_perfil,
        tipo_atirantado,
        diam_men,
        corte_mensula,
        diam_tir,
        corte_tirante,
        diam_estb,
        corte_estabilizador,
        diam_pend,
        corte_pendola,
        diam_diag,
        corte_diagonal,
        corte_supsa,
        corte_brazo
    ]).T
    
    TABLA_CONTROL = np.array([
        nombre_perfil,
        tipo_atirantado,
        comprobacion_tirante1,
        comprobacion_tirante2,
        comprobacion_mensula2,
        comprobacion_mensula1,
        comprobacion_mensula3,
        comprobacion_estabilizador1,
        comprobacion_estabilizador2,
        comprobacion_pendola,
        comprobacion_diagonal,
        p_brz_supsa
    ]).T
    
    # ----------------------------EXPORTACIÓN A EXCEL--------------------------
    file = archivo_mensulas
    file_plantilla = 'Fabricacion Mensulas_Plantilla2.xlsx'
    
    # Crea un libro con la plantilla del excel indicado en path\file
    path = os.path.join(os.getcwd(), 'Calculo de ménsulas', 'Documentación')
    plantilla_path = os.path.join(path, file_plantilla)
    
    # Cargar el archivo de plantilla
    wb = openpyxl.load_workbook(plantilla_path)
    
    # --- Hoja Corte de Tubos
    ws_corte = wb['CORTE TUBOS']
    
    # Escribir datos en la hoja CORTE TUBOS
    nfilas = TABLA_CORTE.shape[0]
    for i in range(nfilas):
        for j in range(TABLA_CORTE.shape[1]):
            cell = ws_corte.cell(row=12+i, column=5+j)
            cell.value = TABLA_CORTE[i, j]
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            cell.font = Font(size=16)
    
    # --- Hoja Control
    ws_control = wb['CONTROL']
    
    # Escribir datos en la hoja CONTROL
    nfilas = TABLA_CONTROL.shape[0]
    for i in range(nfilas):
        for j in range(TABLA_CONTROL.shape[1]):
            cell = ws_control.cell(row=12+i, column=5+j)
            cell.value = TABLA_CONTROL[i, j]
            cell.border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            cell.font = Font(size=16)
    
    # Guarda la excel con el nombre dado
    savepath = filedialog.askdirectory(title='Seleccione el directorio de exportación')
    if savepath:
        file_with_ext = f"{file}.xlsx"
        save_file_path = os.path.join(savepath, file_with_ext)
        wb.save(save_file_path)
        wb.close()
    
    return TABLA_CORTE, TABLA_CONTROL