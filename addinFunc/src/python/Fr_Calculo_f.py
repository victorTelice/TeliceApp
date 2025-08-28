import numpy as np
import math
from logger import Logger 


def Fr_Calculo_f(Coord_descentramientos, t_hc):
    """
    Calcula las fuerzas radiales.
    Parámetros:
    - Coord_descentramientos: Matriz numpy con las coordenadas con los descentramientos.
    - t_hc: Valor de la tensión del hilo conductor.
    
    Returns:
    - Fr_Calculo: Array con las fuerzas radiales calculadas.
    """
    print("coordenadas descentramiento en la funcion: \n", Coord_descentramientos)
    Logger.add_to_log("llamada", "Llamada a la función Fr_Calculo_f")
    
    t_hc = float(t_hc)
    
    # Convertir a array NumPy si no lo es
    Coord_descentramientos = np.asarray(Coord_descentramientos)
    
    # Verificar entrada mínima
    n_points = len(Coord_descentramientos)
    if n_points < 3:
        return np.zeros((n_points, 1))
    
    # Calcular pendientes recta-vanos
    x_coords = np.asarray(Coord_descentramientos[:, 0], dtype=float)
    y_coords = np.asarray(Coord_descentramientos[:, 1], dtype=float)
    
    # Calcular diferencias
    dx = x_coords[:-1] - x_coords[1:]
    dy = y_coords[:-1] - y_coords[1:]
    
    # Evitar divisiones por cero
    dx = np.where(np.abs(dx) < 1e-10, 1e-10, dx)
    
    # Calcular pendientes
    m = dy / dx
    
    # Verificar que tenemos suficientes pendientes
    if len(m) < 2:
        return np.zeros((n_points, 1))
    
    # Calcular ángulos alfa 
    n_angles = len(m) - 1
    alfa = np.zeros(n_angles)
    
    # Vectorizar los cálculos intermedios
    m_i = m[:-1]  # m[i]
    m_i1 = m[1:]  # m[i+1]
    
    numerator = m_i1 - m_i  # m[i+1] - m[i]
    denominator = 1 + m_i1 * m_i  # 1 + m[i+1] * m[i]
    
    # Proteger contra división por cero
    denominator = np.where(np.abs(denominator) < 1e-10, 1e-10, denominator)
    
    # Calcular argumentos del arctan
    arctan_args = numerator / denominator
   
   #usamos math pq np.actan daba errores
    for i in range(n_angles):
        alfa[i] = np.pi - math.atan(float(arctan_args[i]))
    
    #Calcular Fr_hc de forma vectorizada
    cos_half_alfa = np.cos(alfa / 2)
    Fr_hc = 2 * t_hc * cos_half_alfa
    
    #Agregar ceros en los anclajes
    Fr_result = np.concatenate(([0], Fr_hc, [0]))
    
    #Preparar tabla para el GUI
    return Fr_result[:, np.newaxis].astype(float) #modo columna


##esta era la funcion que tenía antes sin optimizar, no se usa pero la dejo por si acaso, dan lo mismo
def Fr_Calculo_f_antigua(Coord_descentramientos, t_hc):
    """
    Calcula las fuerzas radiales.
    
    Parámetros:
    - Coord_descentramientos: Matriz numpy con las coordenadas con los descentramientos.
    - t_hc: Valor de la tensión del hilo conductor.
    
    Returns:
    - Fr_Calculo: Array con las fuerzas radiales calculadas.
    """

    Logger.add_to_log("llamada", "Llamada a la función Fr_Calculo_f")

    t_hc=float(t_hc)
    # 1. Calcular pendientes recta-vanos
    m = np.zeros(len(Coord_descentramientos) - 1)
    for i in range(len(Coord_descentramientos) - 1):
        m[i] = (Coord_descentramientos[i, 1] - Coord_descentramientos[i+1, 1]) / (Coord_descentramientos[i, 0] - Coord_descentramientos[i+1, 0])

    # 2. Calcular ángulos alfa entre dos vanos
    alfa = np.zeros(len(m) - 1)
    for i in range(len(m) - 1):
        alfa[i] = np.pi - np.arctan((m[i+1] - m[i]) / (1 + m[i+1] * m[i]))

    # 3. Calcular Fr_hc
    Fr_hc = np.zeros(len(m) - 1).astype(float)
    for i in range(len(m) - 1):

        Fr_hc[i] = np.sqrt(t_hc**2 + t_hc**2 + 2 * t_hc * t_hc * np.cos(alfa[i])) * np.sign(np.arctan((m[i+1] - m[i]) / (1 + m[i+1] * m[i])))

    # 4. Agregar ceros en los anclajes
    Fr_hc = np.concatenate(([0], Fr_hc, [0]))

    # 5. Preparar tabla para el GUI (columna)
    Fr_Calculo = Fr_hc.reshape(-1, 1)
    return Fr_Calculo


