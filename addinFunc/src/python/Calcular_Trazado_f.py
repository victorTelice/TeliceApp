import numpy as np
from utils.logger import Logger




def Trazado_Calculo_f(datos_in):
    """
    Calcula las coordenadas [X,Y,Z] del trazado de la vía.
    
    Parámetros:
    - datos_in: Matriz numpy con columnas:
        [tipo_tramo (str), pk_inicial (float), pk_final (float), 
         radio (float), sentido_giro (str)]
    
    Returns:
    - Coord3D: Matriz 3D con coordenadas
    - Coord_trazado: Matriz con todas las coordenadas concatenadas
    - datos_in: Datos de entrada 
    """
    Logger.add_to_log("llamada", "Llamada a la función Trazado_Calculo_f")

    npuntos = 30  # número de puntos por tramo
    sigma = 0      # ángulo azimut inicial en radianes
    
    # Convertir tipos de tramo y giros a valores numéricos
    tipo_tramo_num = datos_in[:,0].astype('<f8')
    
    giro_num=datos_in[:, 4].astype(float)
    
    
    # Extraer datos numéricos
    pk_i = datos_in[:, 1].astype(float)
    pk_f = datos_in[:, 2].astype(float)
    parametro = datos_in[:, 3].astype(float)
    
    # Inicializar matriz 3D para coordenadas
    num_tramos = len(datos_in)
    Coord3D = np.zeros((npuntos, 2, num_tramos))
    
    # ------------ CÁLCULO DEL TRAZADO ------------
    for j in range(num_tramos):
        tipo_tramo = tipo_tramo_num[j]
        L = pk_f[j] - pk_i[j]  # longitud de tramo
        R = parametro[j] * giro_num[j]  # radio con signo
        s_vals = np.linspace(0, L, npuntos)  # abscisas a lo largo del tramo

        if tipo_tramo == 1:  # Recta

            dx = s_vals * np.cos(sigma)
            dy = s_vals * np.sin(sigma)
            Coord = np.column_stack((dx, dy))
            Coord3D[:, :, j] = Coord

        elif tipo_tramo == 2:  # Clotoide Recta-Curva
            A = np.sqrt(L * R + 0j)
            sc_temp = np.zeros(npuntos)
            rc_temp = np.zeros(npuntos)
            p = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            sc_temp[1:] = sc_temp[0] + np.linspace(L/(npuntos-1), L, npuntos-1)
            rc_temp[1:] = A**2 / sc_temp[1:]
            p[1:] = 2 * sc_temp[1:] * rc_temp[1:]
            s, pv = sc_temp[1:], p[1:]
            x_temp[1:] = s - s**5/(10*pv**2) + s**9/(216*pv**4) - s**13/(9360*pv**6) + s**17/(685440*pv**8) - s**21/(76204800*pv**10)
            y_temp[1:] = s**3/(3*pv) - s**7/(42*pv**3) + s**11/(1320*pv**5) - s**15/(5600*pv**7) + s**19/(6894720*pv**9) - s**23/(918086400*pv**11)
            
            MC2 = np.array([[np.cos(sigma), -np.sin(sigma)],
                           [np.sin(sigma),  np.cos(sigma)]])
            Coord = np.dot(np.column_stack((x_temp, y_temp)), MC2.T)
            Coord3D[:, :, j] = Coord
            sigma += L / (2*R)
           
        elif tipo_tramo == 3:  # Círculo

            x = R * np.sin(s_vals/R)
            y = R * (1 - np.cos(s_vals/R))
            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                           [np.sin(sigma),  np.cos(sigma)]])
            Coord = np.dot(np.column_stack((x, y)), MC.T)
            Coord3D[:, :, j] = Coord
            sigma += L / R
            
            
            
        elif tipo_tramo == 4:  # Clotoide Curva-Recta
            A = np.sqrt(L * R + 0j) ##aquí se añadió el +0j para evitar problemas con números complejos
            sigma += L / (2 * R)  # para la inversa

            sc_temp = np.concatenate(([0], np.linspace(L/(npuntos-1), L, npuntos-1)))
            rc_temp = np.concatenate(([0], A**2 / sc_temp[1:]))
            p = np.concatenate(([0], 2 * sc_temp[1:] * rc_temp[1:]))

            # Cálculo vectorizado de coordenadas (solo para índices > 0)
            s, pv = sc_temp[1:], p[1:]
            x_temp = np.concatenate(([0], s - s**5/(10*pv**2) + s**9/(216*pv**4) - s**13/(9360*pv**6) + s**17/(685440*pv**8) - s**21/(76204800*pv**10)))
            y_temp = np.concatenate(([0], s**3/(3*pv) - s**7/(42*pv**3) + s**11/(1320*pv**5) - s**15/(5600*pv**7) + s**19/(6894720*pv**9) - s**23/(918086400*pv**11)))

            # Transformación de coordenadas optimizada
            MC = np.array([[np.cos(sigma), -np.sin(sigma)], [np.sin(sigma), np.cos(sigma)]])
          
            Coord=np.fliplr(np.rot90(np.column_stack((-x_temp, y_temp)) @ MC.T, 2))
            Coord3D[:, :, j] = Coord

        elif tipo_tramo == 5:  # Clotoide empalme R1>R2
            R1 = parametro[j-1] * giro_num[j]
            R2 = parametro[j+1] * giro_num[j] 
            Ltotal = L + R2*L/(R1-R2)
            sigmatotal = Ltotal/(2*R2)
            A = np.sqrt(Ltotal * R2 + 0j)##aquí se añadió el +0j para evitar problemas con números complejos
            L_R1 = Ltotal - L
            sigma -= sigmatotal * (L_R1/Ltotal)**2
            
            # Vectorizar arrays completos
            sc_temp = np.concatenate(([L_R1], L_R1 + np.linspace(L/(npuntos-1), L, npuntos-1)))
            rc_temp = np.concatenate(([R1], A**2 / sc_temp[1:]))
            p = 2 * sc_temp * rc_temp

            # Cálculo vectorizado para x_temp e y_temp (todos los elementos)
            s, pv = sc_temp, p
            x_temp = s - s**5/(10*pv**2) + s**9/(216*pv**4) - s**13/(9360*pv**6) + s**17/(685440*pv**8) - s**21/(76204800*pv**10)
            y_temp = s**3/(3*pv) - s**7/(42*pv**3) + s**11/(1320*pv**5) - s**15/(5600*pv**7) + s**19/(6894720*pv**9) - s**23/(918086400*pv**11)


            Coord= (np.column_stack((x_temp - x_temp[0], y_temp - y_temp[0])) @ 
                                np.array([[np.cos(sigma), -np.sin(sigma)], [np.sin(sigma), np.cos(sigma)]]).T)
            # Transformación final optimizada (trasladar y rotar en una operación)
            Coord3D[:, :, j] =Coord
            sigma += Ltotal/(2*R2)

        elif tipo_tramo == 6:  # Clotoide empalme R2>R1
            R1 = parametro[j-1] * giro_num[j] 
            R2 = parametro[j+1] * giro_num[j] 
            Ltotal = L + R1*L/(R2-R1)
            sigmatotal = Ltotal/(2*R1)
            A = np.sqrt(Ltotal * R1 + 0j) ##aquí se añadió el +0j para evitar problemas con números complejos
            L_R1 = Ltotal - L
            sigma += sigmatotal

            sc_temp = np.concatenate(([L_R1], L_R1 + np.linspace(L/(npuntos-1), L, npuntos-1)))
            rc_temp = A**2 / sc_temp
            p = 2 * sc_temp * rc_temp

            # Cálculo vectorizado para x_temp e y_temp (todos los elementos)
            s, pv = sc_temp, p
            x_temp = s - s**5/(10*pv**2) + s**9/(216*pv**4) - s**13/(9360*pv**6) + s**17/(685440*pv**8) - s**21/(76204800*pv**10)
            y_temp = s**3/(3*pv) - s**7/(42*pv**3) + s**11/(1320*pv**5) - s**15/(5600*pv**7) + s**19/(6894720*pv**9) - s**23/(918086400*pv**11)


            Coord= np.fliplr(np.rot90((np.column_stack((-(x_temp - x_temp[0]), y_temp - y_temp[0])) @ 
                                np.array([[np.cos(sigma), -np.sin(sigma)], [np.sin(sigma), np.cos(sigma)]]).T), 2))
           
            # Transformación final optimizada (trasladar, invertir x, rotar y voltear en una operación)
            Coord3D[:, :, j] = Coord
            sigma -= sigmatotal * (L_R1/Ltotal)**2

    # Sumar coordenadas del tramo anterior para continuidad
    for j in range(1, num_tramos):
        tipo_tramo = tipo_tramo_num[j]
        
        if tipo_tramo in [1, 2, 3, 5, 6]:
            for m in range(npuntos):
                Coord3D[m, 0, j] += Coord3D[-1, 0, j-1]
                Coord3D[m, 1, j] += Coord3D[-1, 1, j-1]
        
        if tipo_tramo in [4, 6]:

            for m in range(1, npuntos):
                Coord3D[m, 0, j] += (Coord3D[-1, 0, j-1] - Coord3D[0, 0, j])
                Coord3D[m, 1, j] += (Coord3D[-1, 1, j-1] - Coord3D[0, 1, j])

            for m in range(npuntos):
                Coord3D[m, 0, j] += (Coord3D[-1, 0, j-1] - Coord3D[0, 0, j])
                Coord3D[m, 1, j] += (Coord3D[-1, 1, j-1] - Coord3D[0, 1, j])
    
    # Obtener todas las coordenadas en una matriz
    Coord_trazado = np.zeros((num_tramos * npuntos, 2))
    Coord_trazado[:npuntos, :] = Coord3D[:, :, 0]
    
    for j in range(1, num_tramos):
        start_idx = j * npuntos
        end_idx = (j+1) * npuntos
        Coord_trazado[start_idx:end_idx, :] = Coord3D[:, :, j]
    
    #devuelve los datos 
    return Coord3D, Coord_trazado, datos_in