import numpy as np

def Fr_Calculo_f(Coord_descentramientos, t_hc):
    """
    Calcula las fuerzas radiales a partir de las coordenadas con descentramientos
    y la tensión del hilo conductor.

    Parámetros
    ----------
    Coord_descentramientos : ndarray (n x 2)
        Matriz con las coordenadas (X, Y) de los postes con descentramientos.
    t_hc : float
        Tensión del hilo conductor.

    Returns
    -------
    Fr_Calculo : ndarray (n x 1)
        Array columna con las fuerzas radiales calculadas.
    """

    # --- Calcular pendientes m de cada vano ---
    dx = np.diff(Coord_descentramientos[:, 0])  # Diferencia en X
    dy = np.diff(Coord_descentramientos[:, 1])  # Diferencia en Y
    m = dy / dx                                 # Pendientes

    # --- Calcular ángulos alfa entre vanos adyacentes ---
    dm = m[1:] - m[:-1]                         # Diferencia de pendientes
    denom = 1 + m[1:] * m[:-1]                  # Denominador común
    delta_theta = np.arctan(dm / denom)         # Ángulo relativo
    alfa = np.pi - delta_theta                  # Ángulo entre vanos

    # --- Calcular fuerzas radiales (sin bucle) ---
    Fr_hc_core = np.sqrt(2 * t_hc**2 + 2 * t_hc**2 * np.cos(alfa)) \
                 * np.sign(delta_theta)

    # --- Añadir ceros en los extremos (anclajes) ---
    Fr_hc = np.concatenate(([0], Fr_hc_core, [0]))

    # --- Salida como columna ---
    return Fr_hc.reshape(-1, 1)
