import numpy as np
from utils.logger import Logger 
def Fr_Calculo_f(Coord_descentramientos, t_hc):
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
