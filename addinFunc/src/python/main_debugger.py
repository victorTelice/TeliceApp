import numpy as np
import os
import Calcular_Seccionamiento_f, Calcular_Trazado_f, Calcular_Mensula_f

######### PARTE 1 #################################
##Programa para debuggear las funciones de trazado y seccionamiento y así comprobar que funcionan correctamente, con los siguientes datos de entrada de ejemplo.

## Ejemplo para debuggear la funcion trazado


datos_in = np.array([
    [1, 0.0, 100.0, 0.0, 1],
    [2, 100.0, 150.0, 50.0, -1],
    [3, 150.0, 200.0, 100.0, -1],
    [4, 200.0, 250.0, 150.0, 1],
    [5, 250.0, 300.0, 200.0, 1],
    [6, 300.0, 350.0, 250.0, -1],
    [3, 350.0, 400.0, 450.0, -1]
])

# Llamada a la función
Coord3D, Coord_trazado, datos_out = Calcular_Trazado_f.Trazado_Calculo_f(datos_in)

print("Coordenadas 3D del trazado:")
print(Coord3D)  

print("Coordenadas del trazado:")
print(Coord_trazado)

print("Datos de entrada modificados:")
print(datos_out)

######### PARTE 2 ###################################
##Ejemplo para debuggear la funcion seccionamiento

datos_tabla_tramos_sin_peralte = np.array([
    ['Recta', 0.0, 0.05, 0.0, 'Izquierda'],
    ['Clotoide Recta-Curva', 0.05, 0.08, 50.0, 'Derecha'],
    ['Curva', 0.08, 0.14, 100.0, 'Derecha'],
    ['Clotoide Curva-Recta', 0.14, 0.19, 150.0, 'Izquierda'],
    ['Clotoide Curva-Curva (en C R1>R2)', 0.19, 0.23, 200.0, 'Izquierda'],
    ['Clotoide Curva-Curva (en C R2>R1)', 0.23, 0.26, 250.0, 'Derecha'],
    ['Curva', 0.26, 1.0, 450.0, 'Derecha']
])

#Utilizar la función de trazado para obtener las coordenadas del trazado
result= Calcular_Trazado_f.Trazado_Calculo_f(datos_tabla_tramos_sin_peralte)

datos_vanos= [0, 40, 32, 54, 61, 20, 45] #columna de datos_tabla_vanos
datos_desc=[-335, 61, 8, -40, -25, 5, 20] #columna de datos_tabla_vanos
datos_alt=[6300, 5800, 5900, 6000, 6100, 6200, 6300] #columna de datos_tabla_vanos
pki=0 #primer pk
Coord_trazado= result[1] #obtener las coordenadas que es el segundo elemento de result
npuntos=30# numero de puntos a calcular en cada tramo
datos_tabla_tramos = np.array([
    ['Recta', 0.0, 0.05, 0.0, 'Izquierda', 0],
    ['Clotoide Recta-Curva', 0.05, 0.08, 50.0, 'Derecha', 160],
    ['Curva', 0.08, 0.14, 100.0, 'Derecha',140],
    ['Clotoide Curva-Recta', 0.14, 0.19, 150.0, 'Izquierda',140],
    ['Clotoide Curva-Curva (en C R1>R2)', 0.19, 0.23, 200.0, 'Izquierda',160],
    ['Clotoide Curva-Curva (en C R2>R1)', 0.23, 0.26, 250.0, 'Derecha',160],
    ['Curva', 0.26, 1.0, 450.0, 'Derecha',140]
], dtype=object)

#los valores estan cogidos a ojo copiando del video de la reunion, pero se supone que son reales (la mayoria)
t_hc= 3150
t_hs= 1575
n_hhcc=1 
tipo_pendolado='CA-220'
Ancho_via=14.35 
Carril=72  
ro_hc=1.33 
rel_comp= 3

#aqui los unicos reales son la segunda y la cuarta columna, que son las importantes, lo demas es relleno
datos_tabla_vanos= np.array([
    ['338-04', 'Anclaje', 0, 40, -335, 6200],
    ['338-06', 'Elevación',0.040, 32, 61, 6200],
    ['338-08', 'Vía General', 0.072, 54, 8, 6200],
    ['338-10', 'Vía General', 0.126, 61, -40, 6200],
    ['338-12', 'Vía General', 0.187, 20, -25, 6200],
    ['338-14', 'Vía General', 0.207, 45, 5, 6200],
    ['338-16', 'Vía General', 0.252, 25, 20, 6200],
], dtype=object)

# Llamada a la función de seccionamiento
Coord_seccionamientos_eje, vectores_normal, p_tabla_tipo, Coord_descentramientos, Fr_Calculo, Fv_Calculo =Calcular_Seccionamiento_f.Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, Ancho_via, Carril)

print("Coordenadas de los postes en el eje:")
print(Coord_seccionamientos_eje)   
print("Vectores normales:")
print(vectores_normal)  
print("Tabla de tramos:")
print(p_tabla_tipo)
print("Coordenadas con descentramientos:")
print(Coord_descentramientos)
print("Fuerzas radiales calculadas:")
print(Fr_Calculo)
print("Fuerzas verticales calculadas:")
print(Fv_Calculo)

######### PARTE 3 ###################################
##Ejemplo para debuggear la funcion de calculo de mensulas
nombres_postes= datos_tabla_vanos[:, 0]  # Primera columna de datos_tabla_vanos
Fhc_Calculo=np.column_stack((
        nombres_postes, Fr_Calculo, Fv_Calculo
    ))

'''
 Parámetros:
    - datos_tabla_vanos: Tabla de los datos de los vanos. SI
    - Fhc_Calculo: Tabla con tres columnsas: nombre del poste, fuerza radial y fuerza vertical. SI
    - tabla_datos_topografia: Datos topográficos de los postes. SI
    - t_hs, ro_hs, t_hc, ro_hc: Parámetros de tensión y densidad de los conductores SI
    - Ancho_via, Carril: Dimensiones de la vía. SI
    - biblioteca_escogida_cat: Ruta a la biblioteca de catenaria. NO
    - datos_tabla_tramos: Datos de los tramos. SI
    - np: Número de puntos. SI
    - Coord_trazado: Coordenadas del trazado. SI
    - n_hhcc: Número de hilos de contacto. SI
    - tipo_pendolado: Tipo de péndola. SI
    - rel_comp: Relación de compensación. SI
'''

ro_hs= 0.81  # Densidad del hilo conductor
biblioteca_escogida_cat = 'Bibliotecas\Herrajes de catenaria\Giros_Telice_prueba.her_cat'  # Ruta a la biblioteca de catenaria



##aqui voy a hacer la tabla_topografia, el codigoe es la traduccion de una parte de mensulas.m
datos_postes = datos_tabla_vanos[:, 0]  # Nombres de los postes
dir_postes='Bibliotecas\Postes'
tipo_poste_aux = [f for f in os.listdir(dir_postes) if f.endswith('.pos')]

if not tipo_poste_aux:
        tipo_poste_aux = ['No hay postes']
else:
    lista_postes = tipo_poste_aux
    n_postes_tipo = len(lista_postes)
    tipo_poste_aux = lista_postes.copy()  # en teoría son la misma matriz
    
tipo_poste = [tipo_poste_aux[0] for _ in range(len(datos_postes))]
tipo_poste = np.array(tipo_poste).reshape(-1, 1)
tipologia=datos_tabla_vanos[:, 1]  # Tipología de la ménsula
lado_poste_aux={'lado_poste': 'Derecha'}  # Lado del poste
lado_poste = np.full((len(datos_postes), 1), lado_poste_aux['lado_poste'])
tipo_giros_aux = {'tipo_giro': 'Simple'}
tipo_giros = np.full((len(datos_postes), 1), tipo_giros_aux['tipo_giro'])

desc = p_tabla_tipo[:, 10] * -100  # Porque viene con el criterio cambiado (Están en cm)
desc = desc.reshape(-1, 1)

alt_hc = p_tabla_tipo[:, 11] * 1000  # a mm
alt_hc = alt_hc.reshape(-1, 1)

tipo_cat = np.full((len(datos_postes), 1), 1400)


dir_definicion_mensulas = 'Bibliotecas\Tipos de Ménsulas'
tipo_mensula_aux = [f for f in os.listdir(dir_definicion_mensulas) if f.endswith('.def_men')]
    
if not tipo_mensula_aux:
    tipo_mensula_aux = ['No hay ménsulas']
else:
    lista_mensulas = tipo_mensula_aux
    n_mensulas_tipo = len(lista_mensulas)
    tipo_mensula_aux = lista_mensulas.copy()
    
tipo_mensula = [tipo_mensula_aux[0] for _ in range(len(datos_postes))]
tipo_mensula = np.array(tipo_mensula).reshape(-1, 1)

galibo = np.full((len(datos_postes), 1), 3150)
ht = np.zeros((len(datos_postes), 1))
angulo_brazo = np.zeros((len(datos_postes), 1))
peralte = p_tabla_tipo[:, 5].reshape(-1, 1)
altura_GM = np.full((len(datos_postes), 1), 5300)
dist_giros = np.full((len(datos_postes), 1), 1300)
desplome = np.zeros((len(datos_postes), 1))


dir_brazos = 'Bibliotecas\Brazos de atirantado'
tipo_brazo_aux = [f for f in os.listdir(dir_brazos) if f.endswith('.brz')]
    
if not tipo_brazo_aux:
    tipo_brazo_aux = ['No hay brazos']
else:
    lista_brazos = tipo_brazo_aux
    n_tipo_brazo = len(lista_brazos)
    tipo_brazo_aux = lista_brazos.copy()
    
tipo_brazo = [tipo_brazo_aux[0] for _ in range(len(datos_postes))]
tipo_brazo = np.array(tipo_brazo).reshape(-1, 1)

p_brazo_supsa = np.full((len(datos_postes), 1), 200)

tabla_datos_topografia = np.column_stack([
        datos_postes.reshape(-1, 1), 
        tipo_poste, 
        tipologia, 
        lado_poste, 
        tipo_giros, 
        desc, 
        alt_hc, 
        tipo_cat, 
        tipo_mensula,
        galibo,  
        ht, 
        peralte,  
        altura_GM, 
        dist_giros,  
        desplome,  
        tipo_brazo, 
        p_brazo_supsa,
        angulo_brazo
    ])

print(tabla_datos_topografia)

# Llamada a la función de cálculo de mensulas
#Comentada para que no de error, DESCOMENTAR CUANDO SE QUIERA TRABAJAR CON ELLA
Coord_mensulas, datos_mensulas = Calcular_Mensula_f.Mensulas_Calculo_f(datos_tabla_vanos, Fhc_Calculo, tabla_datos_topografia, t_hs, ro_hs, t_hc, ro_hc, Ancho_via, Carril, biblioteca_escogida_cat, datos_tabla_tramos, npuntos, Coord_trazado, n_hhcc, tipo_pendolado, rel_comp)
