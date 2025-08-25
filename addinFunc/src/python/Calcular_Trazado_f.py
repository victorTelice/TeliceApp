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
        
        if tipo_tramo == 1:  # Recta
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                delta = L / (npuntos - 1)
                x_temp[0]=0
                x_temp[i] = x_temp[i-1] + delta * np.cos(sigma)
                y_temp[0]=0
                y_temp[i] = y_temp[i-1] + delta * np.sin(sigma)
            
            Coord = np.column_stack((x_temp, y_temp))
            Coord3D[:, :, j] = Coord
            
        elif tipo_tramo == 2:  # Clotoide Recta-Curva
            A = np.sqrt(L * R + 0j)
            sc_temp = np.zeros(npuntos)
            rc_temp = np.zeros(npuntos)
            p = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                sc_temp[i] = sc_temp[i-1] + L/(npuntos-1)
                rc_temp[i] = A**2 / sc_temp[i]
                p[i] = 2 * sc_temp[i] * rc_temp[i]
                
                x_temp[i] = (sc_temp[i] - sc_temp[i]**5/(10*p[i]**2) + sc_temp[i]**9/(216*p[i]**4) - sc_temp[i]**13/(9360*p[i]**6) + sc_temp[i]**17/(685440*p[i]**8) - sc_temp[i]**21/(76204800*p[i]**10))

                y_temp[i] = (sc_temp[i]**3/(3*p[i]) - sc_temp[i]**7/(42*p[i]**3) + sc_temp[i]**11/(1320*p[i]**5) - sc_temp[i]**15/(5600*p[i]**7) + sc_temp[i]**19/(6894720*p[i]**9) - sc_temp[i]**23/(918086400*p[i]**11))

            # Matriz de rotación
            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                          [np.sin(sigma), np.cos(sigma)]])
            
            Coord_temp = np.column_stack((x_temp, y_temp))
            Coord = np.dot(Coord_temp, MC.T)
            Coord3D[:, :, j] = Coord
            
            sigma += L / (2 * R)
            
        elif tipo_tramo == 3:  # Círculo
            sc_temp = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                sc_temp[0] = 0
                sc_temp[i] = sc_temp[i-1] + L/(npuntos-1)
                x_temp[0] = 0
                x_temp[i] = R * np.sin(sc_temp[i]/R)
                y_temp[0] = 0
                y_temp[i] = R * (1 - np.cos(sc_temp[i]/R))
            
            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                          [np.sin(sigma), np.cos(sigma)]])
            
            Coord_temp = np.column_stack((x_temp, y_temp))
            Coord = np.dot(Coord_temp, MC.T)
            Coord3D[:, :, j] = Coord
            
            sigma += L / R
            
        elif tipo_tramo == 4:  # Clotoide Curva-Recta
            A = np.sqrt(L * R + 0j) ##aquí se añadió el +0j para evitar problemas con números complejos
            sigma += L / (2 * R)  # para la inversa

            sc_temp = np.zeros(npuntos)
            rc_temp = np.zeros(npuntos)
            p = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                sc_temp[0] = 0
                sc_temp[i] = sc_temp[i-1] + L/(npuntos-1)
                rc_temp[0] = 0
                rc_temp[i] = A**2 / sc_temp[i]
                p[0] = 0
                p[i] = 2 * sc_temp[i] * rc_temp[i]
                x_temp[0] = 0
                x_temp[i] = (sc_temp[i] - sc_temp[i]**5/(10*p[i]**2) + sc_temp[i]**9/(216*p[i]**4) - sc_temp[i]**13/(9360*p[i]**6) + sc_temp[i]**17/(685440*p[i]**8) - sc_temp[i]**21/(76204800*p[i]**10))
                y_temp[0] = 0
                y_temp[i] = (sc_temp[i]**3/(3*p[i]) - sc_temp[i]**7/(42*p[i]**3) + sc_temp[i]**11/(1320*p[i]**5) - sc_temp[i]**15/(5600*p[i]**7) + sc_temp[i]**19/(6894720*p[i]**9) - sc_temp[i]**23/(918086400*p[i]**11))

            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                          [np.sin(sigma), np.cos(sigma)]])
            
            Coord_temp = np.column_stack((-x_temp, y_temp))  # clotoide inversa
            Coord = np.dot(Coord_temp, MC.T)
            Coord = np.rot90(Coord, 2)  
            Coord = np.fliplr(Coord)    # Voltear izquierda-derecha
            Coord3D[:, :, j] = Coord
            
        elif tipo_tramo == 5:  # Clotoide empalme R1>R2
            R1 = parametro[j-1] * giro_num[j]
            R2 = parametro[j+1] * giro_num[j] 
            Ltotal = L + R2*L/(R1-R2)
            sigmatotal = Ltotal/(2*R2)
            A = np.sqrt(Ltotal * R2 + 0j)##aquí se añadió el +0j para evitar problemas con números complejos
            L_R1 = Ltotal - L
            sigma -= sigmatotal * (L_R1/Ltotal)**2
            
            sc_temp = np.zeros(npuntos)
            rc_temp = np.zeros(npuntos)
            p = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                sc_temp[0]=L_R1
                sc_temp[i] = sc_temp[i-1] + L/(npuntos-1)
                rc_temp[0] = R1
                rc_temp[i] = A**2 / sc_temp[i]
                p[0] = 2 * sc_temp[0] * rc_temp[0]
                p[i] = 2 * sc_temp[i] * rc_temp[i]
                
                x_temp[0] = (sc_temp[0] - sc_temp[0]**5/(10*p[0]**2) + sc_temp[0]**9/(216*p[0]**4) - sc_temp[0]**13/(9360*p[0]**6) + sc_temp[0]**17/(685440*p[0]**8) - sc_temp[0]**21/(76204800*p[0]**10))
                x_temp[i] = (sc_temp[i] - sc_temp[i]**5/(10*p[i]**2) + sc_temp[i]**9/(216*p[i]**4) - sc_temp[i]**13/(9360*p[i]**6) + sc_temp[i]**17/(685440*p[i]**8) - sc_temp[i]**21/(76204800*p[i]**10) )

                y_temp[0] = (sc_temp[0]**3/(3*p[0]) - sc_temp[0]**7/(42*p[0]**3) + sc_temp[0]**11/(1320*p[0]**5) - sc_temp[0]**15/(5600*p[0]**7) + sc_temp[0]**19/(6894720*p[0]**9) - sc_temp[0]**23/(918086400*p[0]**11))
                y_temp[i] = (sc_temp[i]**3/(3*p[i]) - sc_temp[i]**7/(42*p[i]**3) + sc_temp[i]**11/(1320*p[i]**5) - sc_temp[i]**15/(5600*p[i]**7) + sc_temp[i]**19/(6894720*p[i]**9) - sc_temp[i]**23/(918086400*p[i]**11))

             # Punto de referencia
            a = x_temp[0]

            b = y_temp[0]
            # Trasladar al origen
            a_ref = x_temp[0]
            b_ref = y_temp[0]
            x_temp -= a_ref
            y_temp -= b_ref
            
            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                          [np.sin(sigma), np.cos(sigma)]])
            
            Coord_temp = np.column_stack((x_temp, y_temp))
            Coord = np.dot(Coord_temp, MC.T)
            Coord3D[:, :, j] = Coord
            
            sigma += Ltotal/(2*R2)
            
        elif tipo_tramo == 6:  # Clotoide empalme R2>R1
            R1 = parametro[j-1] * giro_num[j] 
            R2 = parametro[j+1] * giro_num[j] 
            Ltotal = L + R1*L/(R2-R1)
            sigmatotal = Ltotal/(2*R1)
            A = np.sqrt(Ltotal * R1 + 0j) ##aquí se añadió el +0j para evitar problemas con números complejos
            L_R1 = Ltotal - L
            sigma += sigmatotal
            
            sc_temp = np.zeros(npuntos)
            rc_temp = np.zeros(npuntos)
            p = np.zeros(npuntos)
            x_temp = np.zeros(npuntos)
            y_temp = np.zeros(npuntos)
            
            for i in range(1, npuntos):
                sc_temp[0] = L_R1
                sc_temp[i] = sc_temp[i-1] + L/(npuntos-1)
                rc_temp[0] = A**2 / sc_temp[0]
                rc_temp[i] = A**2 / sc_temp[i]
                p[0] = 2 * sc_temp[0] * rc_temp[0]
                p[i] = 2 * sc_temp[i] * rc_temp[i]
                
                # Punto de referencia
                x_temp[0] = (sc_temp[0] - sc_temp[0]**5/(10*p[0]**2) + sc_temp[0]**9/(216*p[0]**4) - sc_temp[0]**13/(9360*p[0]**6) + sc_temp[0]**17/(685440*p[0]**8) - sc_temp[0]**21/(76204800*p[0]**10))
                x_temp[i] = (sc_temp[i] - sc_temp[i]**5/(10*p[i]**2) + sc_temp[i]**9/(216*p[i]**4) - sc_temp[i]**13/(9360*p[i]**6) + sc_temp[i]**17/(685440*p[i]**8) - sc_temp[i]**21/(76204800*p[i]**10))

                y_temp[0] = (sc_temp[0]**3/(3*p[0]) - sc_temp[0]**7/(42*p[0]**3) + sc_temp[0]**11/(1320*p[0]**5) - sc_temp[0]**15/(5600*p[0]**7) + sc_temp[0]**19/(6894720*p[0]**9) - sc_temp[0]**23/(918086400*p[0]**11))
                y_temp[i] = (sc_temp[i]**3/(3*p[i]) - sc_temp[i]**7/(42*p[i]**3) + sc_temp[i]**11/(1320*p[i]**5) - sc_temp[i]**15/(5600*p[i]**7) + sc_temp[i]**19/(6894720*p[i]**9) - sc_temp[i]**23/(918086400*p[i]**11))

            # Punto de referencia
            a = x_temp[0]  
            b = y_temp[0]

            # Trasladar al origen
            a_ref = x_temp[0]
            b_ref = y_temp[0]
            x_temp -= a_ref
            y_temp -= b_ref
            
            MC = np.array([[np.cos(sigma), -np.sin(sigma)],
                          [np.sin(sigma), np.cos(sigma)]])
            
            Coord_temp = np.column_stack((-x_temp, y_temp))  # clotoide inversa
            Coord = np.dot(Coord_temp, MC.T)
            Coord = np.rot90(Coord, 2)  # Rotar 180 grados
            Coord = np.fliplr(Coord)    # Voltear izquierda-derecha
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


