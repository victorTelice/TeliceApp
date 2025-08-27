import os
import numpy as np
import pandas as pd
from scipy.io import loadmat  # Para cargar archivos .mat
import Calcular_Trazado_f, Calcular_Seccionamiento_f, Calcular_Mensula_f, corte_control_f
from logger import Logger


Logger.add_to_log('info', '-------INICIO PROGRAMA-------')

#Funcion para desacorchetar algunas variables que vienen sobreencorchetadas de matlab
def aplanar_varias_veces(array, veces):
    resultado = array
    for _ in range(veces):
        resultado = [item for subarray in resultado for item in subarray]
    return resultado


#Funcion para simplificar multiples arrrays, que leen así datos de los archivos de matlab
def limpiar_tabla(tabla):
    """
    Limpia un numpy.array de objetos con varias filas y columnas,
    extrayendo escalares y quitando corchetes innecesarios.
    Devuelve una lista de listas (tabla limpia).
    """
    tabla_limpia = []
    for fila in tabla:
        fila_limpia = []
        for item in fila:
            # Desempaquetar hasta que deje de ser un array
            while isinstance(item, np.ndarray):
                if item.shape == ():   # escalar numpy
                    item = item.item()
                elif item.size == 1:   # array 1x1
                    item = item.item()
                else:                  # lista normal si tiene más de 1
                    item = item.tolist()
            fila_limpia.append(item)
        tabla_limpia.append(fila_limpia)
    return tabla_limpia



#Funcion para imprimir una tabla por terminal
def imprimir_tabla(array: np.ndarray):
    """
    Imprime un array de numpy en forma de tabla visual y alineada, sin decimales.
    
    Parámetros:
        array (np.ndarray): El array a imprimir.
    """
    # Convertimos todos los elementos a enteros y luego a string
    filas_str = [[str(elem) for elem in fila] for fila in array]

    # Calculamos el ancho máximo de cada columna
    anchos = [max(len(fila[i]) for fila in filas_str) for i in range(array.shape[1])]

    # Imprimimos las filas alineadas
    for fila in filas_str:
        fila_justificada = [elem.rjust(anchos[i]) for i, elem in enumerate(fila)]
        print(" | ".join(fila_justificada))
        print("-" * (sum(anchos) + 3 * (len(fila) - 1)))

# Construcción de las rutas de archivo
biblioteca_via = os.path.join('Bibliotecas', 'Tipos de vía', '1435_72.via')
biblioteca_conductores = os.path.join('Bibliotecas', 'Tipo de conductores', 'hhcc_120_1575_sust_95_1575cnd.cnd')
biblioteca_her_men = os.path.join('Bibliotecas', 'Herrajes de ménsula', 'Herrajes_Mnf-Lug.her_men')
biblioteca_her_cat = os.path.join('Bibliotecas', 'Herrajes de catenaria', 'Giros_Mnf_Lug.her_cat')
biblioteca_def_men = os.path.join('Bibliotecas', 'Tipos de Ménsulas', 'Ménsulas Monf_Lugo.def_men')
trazado = os.path.join('Trazado', 'Mnf-Lug - - Our_Sarr-386_500 a 395_310.trz')
secc = os.path.join('Seccionamiento', 'OU_Sr_05_388-25 A 389-6.secc')
Logger.add_to_log("info", "Rutas Leidas Correctamente")

# Cargar los archivos 
via_data = loadmat(biblioteca_via)
ancho_via= via_data['ancho_via'][0][0].astype(float)
ancho_carril= via_data['ancho_carril'][0][0].astype(float)
Logger.add_to_log("info", "Datos de vía Cargados Correctamente")

conductores_data = loadmat(biblioteca_conductores)
s_hc = conductores_data['s_hc'][0][0].astype(float)
t_hc = conductores_data['t_hc'][0][0].astype(float)
ro_hc = conductores_data['ro_hc'][0][0].astype(float)
s_hs = conductores_data['s_hs'][0][0].astype(float)
t_hs = conductores_data['t_hs'][0][0].astype(float)
ro_hs = conductores_data['ro_hs'][0][0].astype(float)
tipo_pendolado = conductores_data['tipo_pendolado'][0][0][0]
n_hhcc = conductores_data['n_hhcc'][0][0].astype(int)
Logger.add_to_log("info", "Conductores Cargados Correctamente")


trazado_data = loadmat(trazado)
Coord3D = trazado_data['Coord3D']
Coord_trazado = trazado_data['Coord_trazado']
datos_in = trazado_data['datos_in']
npuntos= trazado_data['np']
datos_tabla_tramos = trazado_data['datos_tabla_tramos']
Logger.add_to_log("info", "Trazado Cargado Correctamente")


#limpio la tabla leida del archivo de matlab para que no de errores si la queremos meter a una hoja excel o algo así
tabla_tramos_limpia=limpiar_tabla(datos_tabla_tramos)


secc_data = loadmat(secc)
Coord_seccionamientos_eje = secc_data['Coord_seccionamientos_eje']
vectores_normal=aplanar_varias_veces(secc_data['vectores_normal'],1)
datos_tabla_vanos=secc_data['datos_tabla_vanos']
p_tabla_tipo=secc_data['p_tabla_tipo']
Coord_descentramientos=secc_data['Coord_descentramientos']
Fhc_Calculo=secc_data['Fhc_Calculo']
rel_comp=secc_data['rel_comp']
Logger.add_to_log("info", "Seccionamientos Cargados Correctamente")


nombres_postes=datos_tabla_vanos[::2, 0]
datos_vanos= np.concatenate((np.array([0]), datos_tabla_vanos[1:-1:2,3]))
datos_desc=datos_tabla_vanos[::2, 4].astype(float) * (-10) ##estaba en cm y lo queremos en mm
datos_alt=datos_tabla_vanos[::2, 5]
pki=datos_tabla_vanos[0,2]*1000 #queremos el primer pk en m
pk_i=datos_tabla_tramos[:,1]*1000
pk_f=datos_tabla_tramos[:,2]*1000
print("Datos cargados satisfactoriamente")
Logger.add_to_log("info", "Postes Cargados Correctamente")

# Ejecutar el cálculo de trazado
Coord3D_2, Coord_trazado_2, datos_out_2 = Calcular_Trazado_f.Trazado_Calculo_f(datos_in)
print("Cálculos trazado realizados correctamente")
Logger.add_to_log("info", "Cálculos trazado realizados correctamente")

# Comparamos con lo que devuelve matlab
comparacion_trazados=np.allclose(Coord_trazado, Coord_trazado_2)
comparación_Coord3D=np.allclose(Coord3D, Coord3D_2)
print('Las coordenadas_trazado son iguales: ', comparacion_trazados)
Logger.add_to_log("debug", f"Coordenadas del trazado comparadas. Son iguales: {comparacion_trazados} {'✅' if comparacion_trazados else '❌'}")


Coord_seccionamientos_eje_2, vectores_normal_2, p_tabla_tipo_2, Coord_descentramientos_2, Fr_Calculo, Fv_Calculo =Calcular_Seccionamiento_f.Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, ancho_via, ancho_carril)
print('Fr_calculo',Fr_Calculo)
print('fv_calculo',Fv_Calculo)
print("Cálculos seccionamiento realizados correctamente")
Logger.add_to_log("info", "Cálculos seccionamiento realizados correctamente")


comparacion_seccionamientos_eje_=np.allclose(Coord_seccionamientos_eje, Coord_seccionamientos_eje_2)
Logger.add_to_log("debug", f"Coordenadas de seccionamiento eje comparadas. Son iguales: {comparacion_seccionamientos_eje_} {'✅' if comparacion_seccionamientos_eje_ else '❌'}")

comparacion_vectores_normal=np.allclose(vectores_normal, vectores_normal_2)
Logger.add_to_log("debug", f"Coordenadas de vectores normal comparadas. Son iguales: {comparacion_vectores_normal} {'✅' if comparacion_vectores_normal else '❌'}")

comparacion_Coord_descentramientos= np.allclose(Coord_descentramientos.astype(float), Coord_descentramientos_2)
Logger.add_to_log("debug", f"Coordenadas con descentramiento comparadas. Son iguales: {comparacion_Coord_descentramientos} {'✅' if comparacion_Coord_descentramientos else '❌'}")

comparacion_Fr=np.allclose(Fr_Calculo.ravel(),Fhc_Calculo[:,1].astype(float))
Logger.add_to_log("debug", f"Fuerzas_radiales comparadas. Son iguales: {comparacion_Fr} {'✅' if comparacion_Fr else '❌'}")

Fv_matlab=np.array([6.4140, 18.4421,6.4140,3.1490,6.9959,6.8391,7.2305,6.8730,6.8039,6.9485,6.9485,5.9130,9.0530,7.4830,7.4830,10.6225,1050], dtype=float)#esta se la pongo a mano pq no corresponde a la que hay en fvhc
comparacion_Fv=np.allclose(Fv_Calculo.ravel(),Fv_matlab, 1e-2)#pongo esta tolerancia pq en matlab solo pone 2 decimales en la tabla
Logger.add_to_log("debug", f"Fuerzas_verticales comparadas. Son iguales: {comparacion_Fv} {'✅' if comparacion_Fv else '❌'}")

ruta_datos_topograficos=os.path.join('Datos_topograficos', '05_Oural - Sarria.xlsx')
datos_topograficos_hoja=pd.read_excel(ruta_datos_topograficos, sheet_name=4)
tabla_datos_topografia=datos_topograficos_hoja.iloc[10:27, 4:22].values
imprimir_tabla(tabla_datos_topografia)
print("datos leidos correctamente del excel")
Logger.add_to_log("info", "Datos leídos correctamente del excel de datos topográficos")

datos_mensulas, Coord_mensulas  = Calcular_Mensula_f.Mensulas_Calculo_f(datos_tabla_vanos, Fhc_Calculo, tabla_datos_topografia, t_hs, ro_hs, t_hc, ro_hc, ancho_via, ancho_carril, biblioteca_her_cat , datos_tabla_tramos, npuntos, Coord_trazado, n_hhcc, tipo_pendolado, rel_comp)
print('Calculos mensulas realizados correctamente')
Logger.add_to_log("info", "Cálculos ménsulas realizados correctamente")

#guardamos las coordenadas de ménsulas en un .txt
ruta_coords_python=os.path.join('Coordenadas_Mensulas', 'Coordenadas_python.txt')
np.savetxt(ruta_coords_python, Coord_mensulas, fmt='%s', delimiter='\t')
Logger.add_to_log("debug", "Coordenadas mensulas guardadas en el .txt")
imprimir_tabla(datos_mensulas)

##voy a comparar coord_mensulas que me ha dado a mi con las que dan en el programa de matlab
#funcion que quita parentesis, para que luego use la matriz hector para dibujar el dxf
def quitar_parentesis_en_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as fin:
        lineas = fin.readlines()
    with open(ruta, "w", encoding="utf-8") as fout:
        for linea in lineas:
            fout.write(linea.replace("(", "").replace(")", ""))

ruta_archivo1=os.path.join('Coordenadas_Mensulas', 'Coordenadas_python.txt')
quitar_parentesis_en_archivo(ruta_archivo1)

# Ejemplo de uso:
ruta_archivo2=os.path.join('Coordenadas_Mensulas','matrixcompleja2.txt')#estas son las de matlab

archivo1 = ruta_archivo1
archivo2 = ruta_archivo2

#difs = comparar_archivos_txt(archivo1, archivo2)
matriz1=np.loadtxt(archivo1, dtype=complex)
matriz2=np.loadtxt(archivo2, dtype=str)
matriz2 = np.char.replace(matriz2, 'i', 'j')
matriz2= matriz2.astype(complex)
a=np.allclose(matriz1,matriz2, 1e-6)#esta tolerancia pq es el numero aprox de decimales que exporta la matriz de matlab
print('Las coordenadas son iguales con tolerancia 0.000001: ', a)#yo diria que tiene más pero como matlab da los datos redondeado a 11 cifras pues ahí acorta
Logger.add_to_log("debug", f"Coordenadas mensulas comparadas. Son iguales: {a} {'✅' if a else '❌'}")


corte_control_f.corte_control_f(Coord_mensulas, datos_mensulas, tabla_datos_topografia, "mondongo", "desktop")
Logger.add_to_log("debug", "Excel de corte y control exportado")

Logger.add_to_log('info', '-------FIN PROGRAMA-------')



