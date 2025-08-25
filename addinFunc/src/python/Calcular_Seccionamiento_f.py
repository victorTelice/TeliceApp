import numpy as np
import Fr_Calculo_f, Fv_Calculo_f
from utils.logger import Logger 

def Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, 
                             datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, 
                             ro_hc, n_hhcc, tipo_pendolado, rel_comp, Ancho_via, Carril):
    """
    Esta función calcula las coordenadas de los postes de la vía, vectores normales y las fuerzas radiales y verticales.
    
    Parámetros:
    - datos_tabla_vanos: tabla con información de los vanos
    - datos_vanos: Longitudes de vanos, en verdad es una columna de datos_tabla_vanos
    - datos_desc: Descentramientos , en verdad es una columna de datos_tabla_vanos
    - datos_alt: Alturas , en verdad es una columna de datos_tabla_vanos
    - En estas columnas dichas que se supone que ya te vienen en datos_tabla_vanos los he puesto porque he copiado tal cual como estaba en matlab, y la tenían así
    - pki: Punto kilométrico inicial
    - datos_tabla_tramos: Datos de los tramos del trazado 
    - Coord_trazado: Coordenadas del trazado, se obtiene de la función Calcular_Trazado_f
    - npuntos: Número de puntos por tramo 
    - t_hc, t_hs, ro_hc, n_hhcc: Parámetros de conductores
    - tipo_pendolado, Ancho_via, Carril: Parámetros de la vía
    - rel_comp: Relación de compensación

    Returns:
    - Coord_seccionamientos_eje: Coordenadas de los postes en el eje
    - vectores_normal: Vectores normales
    - p_tabla_tipo: Tabla con información de tramos
    - Coord_descentramientos: Coordenadas con descentramientos
    - Fr_Calculo: Fuerzas radiales
    - Fv_Calculo: Fuerzas verticales
    """

    Logger.add_to_log("llamada", "Llamada a la función Seccionamiento_Calculo_f")


    tipo_tramo = np.array([str(tipo[0]) for tipo in datos_tabla_tramos[:, 0]])
    pk_i= datos_tabla_tramos[:,1]*1000
    pk_f=datos_tabla_tramos[:,2]*1000
    parametro= datos_tabla_tramos[:,3].astype(float)
    giro= np.where(datos_tabla_tramos[:, 4] == 'Izquierda', 1, -1)  # 1 para Izquierda, -1 para Derecha
    peralte_tramo=datos_tabla_tramos[:,5]

    # Asignación de tipo de tramo
    tipo_dict = {
        'Recta': 1,
        'Clotoide (Recta-Círculo)': 2,
        'Círculo': 3,
        'Clotoide (Círculo-Recta)': 4,
        'Clotoide (R1>R2)': 5,
        'Clotoide (R2>R1)': 6
    }
    tipo_tramo_aux = np.array([tipo_dict.get(tipo,0) for tipo in tipo_tramo])
    datos_tabla_tramos=np.column_stack((tipo_tramo_aux,pk_i,pk_f,parametro, giro, peralte_tramo))

    # Ajustar radios para tramos especiales
    for k in range(len(tipo_tramo)):
        if datos_tabla_tramos[k, 0] in [5, 6]:
            datos_tabla_tramos[k, 3] = datos_tabla_tramos[k-1, 3]  # Radio R1ç
            if datos_tabla_tramos.shape[1]!=7:
                datos_tabla_tramos = np.column_stack((
                    datos_tabla_tramos, 
                    np.zeros(len(tipo_tramo))
                ))
            datos_tabla_tramos[k, 6] = datos_tabla_tramos[k+1, 3]  # Radio R2
    
    ## Calcular ángulos iniciales y finales de cada tramo
    sigma_inicial = np.zeros(len(tipo_tramo))
    sigma_final = np.zeros(len(tipo_tramo))
    L = np.zeros(len(tipo_tramo))
    R1 = np.zeros(len(tipo_tramo))
    R2 = np.zeros(len(tipo_tramo))
    Ltotal = np.zeros(len(tipo_tramo))
    L_R1 = np.zeros(len(tipo_tramo))
    sigmatotal = np.zeros(len(tipo_tramo))


    
    for j in range(len(tipo_tramo)):
        tipo = datos_tabla_tramos[j, 0]
        L_aux = datos_tabla_tramos[j, 2] - datos_tabla_tramos[j, 1]
        R = datos_tabla_tramos[j, 3] * datos_tabla_tramos[j, 4]
        
        if tipo == 1:  # Recta
            if j == 0:
                sigma_inicial[j] = 0
            else:
                sigma_inicial[j] = sigma_final[j-1]
            sigma_final[j] = sigma_inicial[j]
            
        elif tipo == 2:  # Clotoide Recta-Curva
            if j == 0:
                sigma_inicial[j] = 0
            else:
                sigma_inicial[j] = sigma_final[j-1]
            sigma_final[j] = sigma_inicial[j] + L_aux / (2 * R)
            
        elif tipo == 3:  # Círculo
            if j == 0:
                sigma_inicial[j] = 0
            else:
                sigma_inicial[j] = sigma_final[j-1]
            sigma_final[j] = sigma_inicial[j] + L_aux/ R
            
        elif tipo == 4:  # Clotoide Curva-Recta
            if j == 0:
                sigma_inicial[j] = 0
            else:
                sigma_inicial[j] = sigma_final[j-1]
            sigma_final[j] = sigma_inicial[j] + L_aux / (2 * R)
            
        elif tipo == 5:  # Clotoide R1>R2
            L[j]= L_aux
            R1[j] = datos_tabla_tramos[j, 3] * datos_tabla_tramos[j, 4]
            R2[j] = datos_tabla_tramos[j, 6] * datos_tabla_tramos[j, 4]
            Ltotal[j] = L[j] + R2[j]*L[j]/(R1[j]-R2[j])
            sigmatotal[j] = Ltotal[j]/(2*R2[j])
            L_R1[j] = Ltotal[j] - L[j]
            
            if j == 0:
                sigma_inicial[j] = 0
            else:
                sigma_inicial[j] = sigma_final[j-1] - sigmatotal[j]*(L_R1[j]/Ltotal[j])**2
            sigma_final[j] = sigma_inicial[j] + Ltotal[j]/(2*R2[j])

        elif tipo == 6:  # Clotoide R2>R1
            L[j]= L_aux
            R1[j] = datos_tabla_tramos[j, 3] * datos_tabla_tramos[j, 4]
            R2[j] = datos_tabla_tramos[j, 6] * datos_tabla_tramos[j, 4]
            if j==0:
                Ltotal[j] = L[j] + R2[j]*L[j]/(R2[j]-R1[j])
            else:
                Ltotal[j] = L[j] + R1[j]*L[j]/(R2[j]-R1[j])
            sigmatotal[j] = Ltotal[j]/(2*R1[j])
            L_R1[j] = Ltotal[j] - L[j]

            if j == 0:
                sigma_inicial[j] = 0 + Ltotal[j]/(2*R1[j])
            else:
                sigma_inicial[j] = sigma_final[j-1] + Ltotal[j]/(2*R1[j])
            sigma_final[j] = sigma_inicial[j] - sigmatotal[j]*(L_R1[j]/Ltotal[j])**2
    
    

    array_aux =  np.zeros(len(tipo_tramo))
    datos_tabla_tramos = np.column_stack((datos_tabla_tramos, array_aux, array_aux,sigma_inicial, sigma_final))

    tabla_pks = np.zeros(len(datos_vanos))  # Inicializamos el array de tabla_pks
    n_tramo = np.zeros(len(datos_vanos), dtype=int)

    for i in range(1, len(datos_vanos)):
        tabla_pks[0] = pki
        
        tabla_pks[i] = tabla_pks[i-1] + datos_vanos[i]  # Calculamos los pks de los postes
        n_tramo[0] = np.where((datos_tabla_tramos[:, 2] > tabla_pks[0]) & (datos_tabla_tramos[:, 1] <= tabla_pks[0]))[0][0]
        n_tramo[i] = np.where((datos_tabla_tramos[:, 2] > tabla_pks[i]) & (datos_tabla_tramos[:, 1] <= tabla_pks[i]))[0][0]  # Fila en la que se encuentra el pk en datos_tabla_tramos

    p_tabla_tipo = datos_tabla_tramos[n_tramo, :]  # Extraemos las filas de la tabla según los valores de n_tramo

    tabla_pks = tabla_pks.reshape(-1, 1)  # Transponemos tabla_pks para que sea columna
    p_tabla_tipo[:, 7] = tabla_pks.flatten()  # Asignamos tabla_pks a la columna 8 (índice 7)

    # Añadimos los datos de los descentramientos y alturas en metros
    datos_desc_div= np.zeros(len(datos_desc))
    datos_alt_div= np.zeros(len(datos_alt))

    for i in range(len(n_tramo)):
        datos_desc_div[i] = datos_desc[i] / 1000  # Datos de los descentramientos en metros
        datos_alt_div[i] = datos_alt[i] / 1000  # Datos de las alturas en metros
    p_tabla_tipo = np.column_stack((p_tabla_tipo, datos_desc_div, datos_alt_div))  # Añadimos las columnas de descentramientos y alturas
    


    # Calcular coordenadas de los postes
    x_poste = np.zeros(len(datos_vanos))
    y_poste = np.zeros(len(datos_vanos))
    sigma_poste = np.zeros(len(datos_vanos))
    x_temp_1 = np.zeros(len(datos_vanos))
    y_temp_1 = np.zeros(len(datos_vanos))
    x_temp_2 = np.zeros(len(datos_vanos))
    y_temp_2 = np.zeros(len(datos_vanos))
    
    for j in range(len(datos_vanos)):
        tipo = p_tabla_tipo[j, 0]
        L = float(p_tabla_tipo[j, 2] - p_tabla_tipo[j, 1])
        R = float( p_tabla_tipo[j, 3] * p_tabla_tipo[j, 4])
        sigma_inicial_p = float( p_tabla_tipo[j, 8])
        sigma_final_p = float(p_tabla_tipo[j, 9])
        sc_temp = float (p_tabla_tipo[j, 7] - p_tabla_tipo[j, 1])  # Posición relativa al inicio del tramo
        
        if tipo == 1:  # Recta
            x_temp_2[j] = sc_temp * np.cos(sigma_inicial_p)
            y_temp_2[j] = sc_temp * np.sin(sigma_inicial_p)
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1]
            sigma_poste[j] = sigma_final_p
            
        elif tipo == 2:  # Clotoide Recta-Curva
            A = np.sqrt(L * R + 0j)  # A puede ser complejo si L o R son cero o negativo, por lo que se añade +0j
            sigma_total = L / (2 * R)
            
            if sc_temp == 0:
                x_temp_1[j] = 0
                y_temp_1[j] = 0
            else:
                rc_temp = A**2 / sc_temp
                p = 2 * sc_temp * rc_temp
                
                x_temp_1[j] = (sc_temp - sc_temp**5/(10*p**2) + sc_temp**9/(216*p**4) - sc_temp**13/(9360*p**6) + sc_temp**17/(685440*p**8) - sc_temp**21/(76204800*p**10))
                
                y_temp_1[j] = (sc_temp**3/(3*p) - sc_temp**7/(42*p**3) + sc_temp**11/(1320*p**5) - sc_temp**15/(5600*p**7) + sc_temp**19/(6894720*p**9) - sc_temp**23/(918086400*p**11))
            
            # Rotación de coordenadas
            x_temp_2[j] = x_temp_1[j] * np.cos(sigma_inicial_p) + y_temp_1[j] * -np.sin(sigma_inicial_p)
            y_temp_2[j] = x_temp_1[j] * np.sin(sigma_inicial_p) + y_temp_1[j] * np.cos(sigma_inicial_p)
            
           
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1]
            sigma_poste[j] = sigma_inicial_p + sigma_total * (sc_temp/L)**2
            
        elif tipo == 3:  # Círculo
            if sc_temp == 0:
                x_temp_1[j] = 0
                y_temp_1[j] = 0
            else:
                x_temp_1[j] = R * np.sin(sc_temp/R)
                y_temp_1[j] = R * (1 - np.cos(sc_temp/R))

            # Rotación de coordenadas
            x_temp_2[j] = x_temp_1[j] * np.cos(sigma_inicial_p) + y_temp_1[j] * -np.sin(sigma_inicial_p)
            y_temp_2[j] = x_temp_1[j] * np.sin(sigma_inicial_p) + y_temp_1[j] * np.cos(sigma_inicial_p)

            
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1]
            
            sigma_poste[j] = sigma_inicial_p + sc_temp/R
            
        elif tipo == 4:  # Clotoide Curva-Recta
            A = np.sqrt(L * R + 0j)  # A puede ser complejo si L o R son cero o negativo, por lo que se añade +0j
            sigma_total = L / (2 * R)
            sc_temp = L - sc_temp  # Invertir posición
            
            if sc_temp == 0:
                x_temp_1[j] = 0
                y_temp_1[j] = 0
            else:
                rc_temp = A**2 / sc_temp
                p = 2 * sc_temp * rc_temp

                x_temp_1[j] = (sc_temp - sc_temp**5/(10*p**2) + sc_temp**9/(216*p**4) - sc_temp**13/(9360*p**6) + sc_temp**17/(685440*p**8) - sc_temp**21/(76204800*p**10))

                y_temp_1[j] = (sc_temp**3/(3*p) - sc_temp**7/(42*p**3) + sc_temp**11/(1320*p**5) - sc_temp**15/(5600*p**7) + sc_temp**19/(6894720*p**9) - sc_temp**23/(918086400*p**11))

            # Rotación inversa
            x_temp_2[j] = -x_temp_1[j] * np.cos(sigma_final_p) + y_temp_1[j] * -np.sin(sigma_final_p)
            y_temp_2[j] = -x_temp_1[j] * np.sin(sigma_final_p) + y_temp_1[j] * np.cos(sigma_final_p)

            # Calcular último punto de la clotoide completa
            a_1 = (L - L**5/(10*(2*L*R)**2) + L**9/(216*(2*L*R)**4) - L**13/(9360*(2*L*R)**6) + L**17/(685440*(2*L*R)**8) - L**21/(76204800*(2*L*R)**10))
            
            b_1 = (L**3/(3*(2*L*R)) - L**7/(42*(2*L*R)**3) + L**11/(1320*(2*L*R)**5) - L**15/(5600*(2*L*R)**7) + L**19/(6894720*(2*L*R)**9) - L**23/(918086400*(2*L*R)**11))
            
            a_2 = -a_1 * np.cos(sigma_final_p) + b_1 * -np.sin(sigma_final_p)
            b_2 = -a_1 * np.sin(sigma_final_p) + b_1 * np.cos(sigma_final_p)

            
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] - a_2 ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1] - b_2
            
            sigma_poste[j] = sigma_inicial_p + sigma_total * ((p_tabla_tipo[j, 7]-p_tabla_tipo[j, 1])/L)**2
            
        elif tipo == 5:  # Clotoide R1>R2
            R1 = p_tabla_tipo[j, 3] * p_tabla_tipo[j, 4]
            R2 = p_tabla_tipo[j, 6] * p_tabla_tipo[j, 4]
            Ltotal = L + R2*L/(R1-R2)
            sigmatotal = Ltotal/(2*R2)
            A = np.sqrt(Ltotal * R2 + 0j)  # A puede ser complejo si Ltotal o R2 son cero o negativo, por lo que se añade +0j
            L_R1 = Ltotal - L
            sc_temp = sc_temp + L_R1  # Ajustar posición
            
            # Calcular punto de referencia
            a = (L_R1 - L_R1**5/(10*(2*L_R1*R1)**2) + L_R1**9/(216*(2*L_R1*R1)**4) - L_R1**13/(9360*(2*L_R1*R1)**6) + L_R1**17/(685440*(2*L_R1*R1)**8) - L_R1**21/(76204800*(2*L_R1*R1)**10))

            b = (L_R1**3/(3*(2*L_R1*R1)) - L_R1**7/(42*(2*L_R1*R1)**3) + L_R1**11/(1320*(2*L_R1*R1)**5) - L_R1**15/(5600*(2*L_R1*R1)**7) + L_R1**19/(6894720*(2*L_R1*R1)**9) - L_R1**23/(918086400*(2*L_R1*R1)**11))

            if sc_temp == 0:
                x_temp_1[j] = 0 - a
                y_temp_1[j] = 0 - b
            else:
                rc_temp = A**2 / sc_temp
                p = 2 * sc_temp * rc_temp

                x_temp_1[j] = (sc_temp - sc_temp**5/(10*p**2) + sc_temp**9/(216*p**4) - sc_temp**13/(9360*p**6) + sc_temp**17/(685440*p**8) - sc_temp**21/(76204800*p**10)) - a

                y_temp_1[j] = (sc_temp**3/(3*p) - sc_temp**7/(42*p**3) + sc_temp**11/(1320*p**5) - sc_temp**15/(5600*p**7) + sc_temp**19/(6894720*p**9) - sc_temp**23/(918086400*p**11)) - b

            # Rotación de coordenadas
            x_temp_2[j] = x_temp_1[j] * np.cos(sigma_inicial_p) + y_temp_1[j] * -np.sin(sigma_inicial_p)
            y_temp_2[j] = x_temp_1[j] * np.sin(sigma_inicial_p) + y_temp_1[j] * np.cos(sigma_inicial_p)
            
            
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1]
    
            sigma_poste[j] = sigma_inicial_p + sigmatotal * (sc_temp/Ltotal)**2
            
        elif tipo == 6:  # Clotoide R2>R1
            R1 = p_tabla_tipo[j, 3] * p_tabla_tipo[j, 4]
            R2 = p_tabla_tipo[j, 6] * p_tabla_tipo[j, 4]
            Ltotal = L + R1*L/(R2-R1)
            sigmatotal = Ltotal/(2*R1)
            A = np.sqrt(Ltotal * R1 + 0j)  # A puede ser complejo si Ltotal o R1 son cero o negativo, por lo que se añade +0j
            L_R1 = Ltotal - L
            sc_temp = L - sc_temp + L_R1  # Ajustar posición invertida
            
            # Calcular punto de referencia
            a = (L_R1 - L_R1**5/(10*(2*L_R1*R2)**2) + L_R1**9/(216*(2*L_R1*R2)**4) - L_R1**13/(9360*(2*L_R1*R2)**6) + L_R1**17/(685440*(2*L_R1*R2)**8) - L_R1**21/(76204800*(2*L_R1*R2)**10))

            b = (L_R1**3/(3*(2*L_R1*R2)) - L_R1**7/(42*(2*L_R1*R2)**3) + L_R1**11/(1320*(2*L_R1*R2)**5) - L_R1**15/(5600*(2*L_R1*R2)**7) + L_R1**19/(6894720*(2*L_R1*R2)**9) - L_R1**23/(918086400*(2*L_R1*R2)**11))

            if sc_temp == 0:
                x_temp_1[j] = 0 - a
                y_temp_1[j] = 0 - b
            else:
                rc_temp = A**2 / sc_temp
                p = 2 * sc_temp * rc_temp

                x_temp_1[j] = (sc_temp - sc_temp**5/(10*p**2) + sc_temp**9/(216*p**4) - sc_temp**13/(9360*p**6) + sc_temp**17/(685440*p**8) - sc_temp**21/(76204800*p**10)) - a

                y_temp_1[j] = (sc_temp**3/(3*p) - sc_temp**7/(42*p**3) + sc_temp**11/(1320*p**5) - sc_temp**15/(5600*p**7) + sc_temp**19/(6894720*p**9) - sc_temp**23/(918086400*p**11)) - b

            # Rotación inversa
            x_temp_2[j] = -x_temp_1[j] * np.cos(sigma_inicial_p) + y_temp_1[j] * -np.sin(sigma_inicial_p)
            y_temp_2[j] = -x_temp_1[j] * np.sin(sigma_inicial_p) + y_temp_1[j] * np.cos(sigma_inicial_p)

            # Calcular último punto de la clotoide completa
            a_1 = (Ltotal - Ltotal**5/(10*(2*Ltotal*R1)**2) + Ltotal**9/(216*(2*Ltotal*R1)**4) - Ltotal**13/(9360*(2*Ltotal*R1)**6) + Ltotal**17/(685440*(2*Ltotal*R1)**8) - Ltotal**21/(76204800*(2*Ltotal*R1)**10)) - a

            b_1 = (Ltotal**3/(3*(2*Ltotal*R1)) - Ltotal**7/(42*(2*Ltotal*R1)**3) + Ltotal**11/(1320*(2*Ltotal*R1)**5) - Ltotal**15/(5600*(2*Ltotal*R1)**7) + Ltotal**19/(6894720*(2*Ltotal*R1)**9) - Ltotal**23/(918086400*(2*Ltotal*R1)**11)) - b

            a_2 = -a_1 * np.cos(sigma_inicial_p) + b_1 * -np.sin(sigma_inicial_p)
            b_2 = -a_1 * np.sin(sigma_inicial_p) + b_1 * np.cos(sigma_inicial_p)

            
            x_poste[j] = x_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 0] - a_2 ##cambiado respecto a matlab por el tema de indexacion de filas
            y_poste[j] = y_temp_2[j] + Coord_trazado[(n_tramo[j])*npuntos, 1] - b_2
           
            sigma_poste[j] = sigma_inicial_p - sigmatotal * (sc_temp/Ltotal)**2
    
    # Coordenadas de los postes en el eje
    Coord_seccionamientos_eje = np.column_stack((x_poste, y_poste, sigma_poste))
    
    # Vectores normales (90 grados a la derecha del eje)
    vectores_normal = np.zeros(len(datos_vanos))
    for j in range(len(datos_vanos)):
        vectores_normal[j] = sigma_poste[j] + np.pi / 2  # Añadir pi/2 para rotar 90 grados

    # Coordenadas con descentramientos
    x_desc = x_poste + p_tabla_tipo[:, 10] * np.cos(vectores_normal)
    y_desc = y_poste + p_tabla_tipo[:, 10] * np.sin(vectores_normal)
    Coord_descentramientos = np.column_stack((x_desc, y_desc))
    
    for i in range(len(datos_vanos)):   
        if p_tabla_tipo[i, 0] == 2:   # Recta-Círculo
            p_tabla_tipo[i, 5] = (
                peralte_tramo[n_tramo[i] + 1]
                - peralte_tramo[n_tramo[i] + 1] / (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 1])
                * (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 7])
            )

        if p_tabla_tipo[i, 0] == 4:   # Círculo-Recta
            p_tabla_tipo[i, 5] = (
                peralte_tramo[n_tramo[i] - 1]
                - peralte_tramo[n_tramo[i] - 1] / (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 1])
                * (p_tabla_tipo[i, 7] - p_tabla_tipo[i, 1])
            )

        if p_tabla_tipo[i, 0] == 5:   # R1 > R2
            p_tabla_tipo[i, 5] = (
                peralte_tramo[n_tramo[i] - 1]
                - peralte_tramo[n_tramo[i] + 1] / (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 1])
                * (p_tabla_tipo[i, 7] - p_tabla_tipo[i, 1])
            )

        if p_tabla_tipo[i, 0] == 6:   # R1 < R2
            p_tabla_tipo[i, 5] = (
                peralte_tramo[n_tramo[i] + 1]
                - peralte_tramo[n_tramo[i] - 1] / (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 1])
                * (p_tabla_tipo[i, 2] - p_tabla_tipo[i, 7])
            )

    # Segundo bucle: invertir signo si curva a izquierdas
    for i in range(len(datos_vanos)):
        if p_tabla_tipo[i, 4] == 1:
            p_tabla_tipo[i, 5] = -p_tabla_tipo[i, 5]
        
    # Calcular fuerzas (funciones auxiliares)
    Fr_Calculo = Fr_Calculo_f.Fr_Calculo_f(Coord_descentramientos, t_hc)
    Logger.add_to_log("info", "Cálculos Fuerza_radial realizados correctamente")

    Fv_Calculo= Fv_Calculo_f.Fv_Calculo_f(datos_tabla_vanos, Coord_descentramientos, p_tabla_tipo, n_hhcc, tipo_pendolado, ro_hc, t_hc, t_hs, rel_comp,Ancho_via, Carril)
    Logger.add_to_log("info", "Cálculos Fuerza_vertical realizados correctamente")

    # Devolver resultados
    return Coord_seccionamientos_eje, vectores_normal, p_tabla_tipo, Coord_descentramientos, Fr_Calculo, Fv_Calculo
    



