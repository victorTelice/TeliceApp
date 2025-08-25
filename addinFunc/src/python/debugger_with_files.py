import os
import numpy as np
import pandas as pd
from scipy.io import loadmat  # Para cargar archivos .mat
import Calcular_Trazado_f, Calcular_Seccionamiento_f, Calcular_Mensula_f
from utils.logger import Logger


Logger.add_to_log('info', '-------INICIO PROGRAMA-------')

#Funcion para simplificar multiples arrrays, que leen así datos de los archivos de matlab
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

conductores_data = loadmat(biblioteca_conductores)
s_hc = conductores_data['s_hc'][0][0].astype(float)
t_hc = conductores_data['t_hc'][0][0].astype(float)
ro_hc = conductores_data['ro_hc'][0][0].astype(float)
s_hs = conductores_data['s_hs'][0][0].astype(float)
t_hs = conductores_data['t_hs'][0][0].astype(float)
ro_hs = conductores_data['ro_hs'][0][0].astype(float)
tipo_pendolado = conductores_data['tipo_pendolado'][0][0][0]
n_hhcc = conductores_data['n_hhcc'][0][0].astype(int)


her_men_data = loadmat(biblioteca_her_men)
herrajes_mensula = aplanar_varias_veces(her_men_data['herrajes_mensula'], 2) 
medidas_herrajes_mensula=aplanar_varias_veces(her_men_data['medidas_herrajes_mensula'],2) 
matriz_herrajes_mensula = her_men_data['matriz_herrajes_mensula']

her_cat_data = loadmat(biblioteca_her_cat)
herrajes_catenaria = aplanar_varias_veces(her_cat_data['herrajes_catenaria'],2)
medidas_herrajes_catenaria = aplanar_varias_veces( her_cat_data['medidas_herrajes_catenaria'],2)
matriz_herrajes_catenaria = her_cat_data['matriz_herrajes_catenaria']

def_men_data = loadmat(biblioteca_def_men)
elegir_mensula_valor = def_men_data['elegir_mensula_valor']
biblioteca_escogida = def_men_data['biblioteca_escogida']
grapas_b1 = def_men_data['grapas_b1']
terminales_b1 = def_men_data['terminales_b1']
parametros_b1 = def_men_data['parametros_b1']
otrosherrajes_b1 = def_men_data['otrosherrajes_b1']
grapas_b2 = def_men_data['grapas_b2']
terminales_b2 = def_men_data['terminales_b2']
parametros_b2 = def_men_data['parametros_b2']
otrosherrajes_b2 = def_men_data['otrosherrajes_b2']
grapas_cola = def_men_data['grapas_cola']
terminales_cola = def_men_data['terminales_cola']
parametros_cola = def_men_data['parametros_cola']
otrosherrajes_cola = def_men_data['otrosherrajes_cola']
grapas_vertical = def_men_data['grapas_vertical']
terminales_vertical = def_men_data['terminales_vertical']
parametros_vertical = def_men_data['parametros_vertical']
otrosherrajes_vertical = def_men_data['otrosherrajes_vertical']
matriz_herrajes_mensula = def_men_data['matriz_herrajes_mensula']
herrajes_mensula = def_men_data['herrajes_mensula']
medidas_herrajes_mensula = def_men_data['medidas_herrajes_mensula']

trazado_data = loadmat(trazado)
Coord3D = trazado_data['Coord3D']
Coord_trazado = trazado_data['Coord_trazado']
datos_in = trazado_data['datos_in']
npuntos= trazado_data['np']
datos_tabla_tramos = trazado_data['datos_tabla_tramos']

#limpio la tabla leida del archivo de matlab para que no de errores si la queremos meter a una hoja excel o algo así
tabla_tramos_limpia=limpiar_tabla(datos_tabla_tramos)


secc_data = loadmat(secc)
Coord_seccionamientos_eje = secc_data['Coord_seccionamientos_eje']
vectores_normal=secc_data['vectores_normal']
datos_tabla_vanos=secc_data['datos_tabla_vanos']
p_tabla_tipo=secc_data['p_tabla_tipo']
Coord_descentramientos=secc_data['Coord_descentramientos']
Fhc_Calculo=secc_data['Fhc_Calculo']
rel_comp=secc_data['rel_comp']

nombres_postes=datos_tabla_vanos[::2, 0]
datos_vanos= np.concatenate((np.array([0]), datos_tabla_vanos[1:-1:2,3]))
datos_desc=datos_tabla_vanos[::2, 4].astype(float) * (-10) ##estaba en cm y lo queremos en mm
datos_alt=datos_tabla_vanos[::2, 5]
pki=datos_tabla_vanos[0,2]*1000 #queremos el primer pk en m
pk_i=datos_tabla_tramos[:,1]*1000
pk_f=datos_tabla_tramos[:,2]*1000
print("Datos cargados satisfactoriamente")
Logger.add_to_log("info", "Datos cargados correctamente de los archivos de matlab")

# Ejecutar el cálculo de trazado
Coord3D_2, Coord_trazado_2, datos_out_2 = Calcular_Trazado_f.Trazado_Calculo_f(datos_in)
print(Coord_trazado_2)
print("Cálculos trazado realizados correctamente")
Logger.add_to_log("info", "Cálculos trazado realizados correctamente")


Coord_seccionamientos_eje_2, vectores_normal_2, p_tabla_tipo_2, Coord_descentramientos_2, Fr_Calculo, Fv_Calculo =Calcular_Seccionamiento_f.Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, ancho_via, ancho_carril)
print('Fr_calculo',Fr_Calculo)
print('fv_calculo',Fv_Calculo)
print("Cálculos seccionamiento realizados correctamente")
Logger.add_to_log("info", "Cálculos seccionamiento realizados correctamente")

ruta_datos_topograficos=os.path.join('Datos_topograficos', '05_Oural - Sarria.xlsx')
datos_topograficos_hoja=pd.read_excel(ruta_datos_topograficos, sheet_name=4)
tabla_datos_topografia=datos_topograficos_hoja.iloc[10:27, 4:22].values
imprimir_tabla(tabla_datos_topografia)
print("datos leidos correctamente del excel")
Logger.add_to_log("info", "Datos leídos correctamente del excel de datos topográficos")

datos_mensulas, Coord_mensulas  = Calcular_Mensula_f.Mensulas_Calculo_f(datos_tabla_vanos, Fhc_Calculo, tabla_datos_topografia, t_hs, ro_hs, t_hc, ro_hc, ancho_via, ancho_carril, biblioteca_her_cat , datos_tabla_tramos, npuntos, Coord_trazado, n_hhcc, tipo_pendolado, rel_comp)
print('Calculos mensulas realizados correctamente')
Logger.add_to_log("info", "Cálculos ménsulas realizados correctamente")

ruta_coords_python=os.path.join('Coordenadas_Mensulas', 'Coordenadas_python.txt')
np.savetxt(ruta_coords_python, Coord_mensulas, fmt='%s', delimiter='\t')
Logger.add_to_log("debug", "Coordenadas mensulas guardadas en el .txt")
imprimir_tabla(datos_mensulas)

##voy a comparar coord_mensulas que me ha dado a mi con las que dan en el programa de matlab

##he hecho un par de funciones para ver las diferencias
def comparar_archivos_txt(archivo1, archivo2):
    """
    Compara dos archivos de texto con matrices numéricas sin tolerancia.
    
    Parámetros
    ----------
    archivo1 : str
        Ruta del primer archivo .txt
    archivo2 : str
        Ruta del segundo archivo .txt
    
    Retorna
    -------
    diferencias : list of tuple
        Lista de diferencias en la forma [(fila, col, valor1, valor2), ...]
    """
    # Leer los archivos como arrays numéricos
    matriz1 = np.loadtxt(archivo1, dtype=object)
    matriz2 = np.loadtxt(archivo2, dtype=object)

    # Verificar que tengan la misma forma
    if matriz1.shape != matriz2.shape:
        raise ValueError(f"Las matrices tienen formas distintas: {matriz1.shape} vs {matriz2.shape}")

    diferencias = []
    filas, cols = matriz1.shape
    for i in range(filas):
        for j in range(cols):
            if matriz1[i, j] != matriz2[i, j]:
                diferencias.append((i, j, matriz1[i, j], matriz2[i, j]))

    return diferencias


def comparar_archivos_txt2(archivo1, archivo2):
    """
    Compara dos archivos de texto con matrices numéricas sin tolerancia,
    considerando solo la parte antes del primer punto de cada número.
    
    Parámetros
    ----------
    archivo1 : str
        Ruta del primer archivo .txt
    archivo2 : str
        Ruta del segundo archivo .txt
    
    Retorna
    -------
    diferencias : list of tuple
        Lista de diferencias en la forma [(fila, col, valor1, valor2), ...]
    """
    # Leer los archivos como arrays de objetos (strings)
    matriz1 = np.loadtxt(archivo1, dtype=object)
    matriz2 = np.loadtxt(archivo2, dtype=object)

    # Verificar que tengan la misma forma
    if matriz1.shape != matriz2.shape:
        raise ValueError(f"Las matrices tienen formas distintas: {matriz1.shape} vs {matriz2.shape}")

    diferencias = []
    filas, cols = matriz1.shape
    for i in range(filas):
        for j in range(cols):
            # Tomar solo la parte antes del primer punto
            val1 = str(matriz1[i, j]).split('.')[0]
            val2 = str(matriz2[i, j]).split('.')[0]
            if val1 != val2:
                diferencias.append((i+1, j+1, val1, val2))

    return diferencias


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
ruta_archivo2=os.path.join('Coordenadas_Mensulas','matrixcompleja.txt')#estas son las de matlab
archivo1 = ruta_archivo1
archivo2 = ruta_archivo2

#difs = comparar_archivos_txt(archivo1, archivo2)

difs = comparar_archivos_txt2(archivo1, archivo2)

#lo imprimo por terminal
if difs:
    print(f"Se encontraron {len(difs)} diferencias:")
    for fila, col, v1, v2 in difs:
        print(f"({fila}, {col}): {v1} vs {v2}")
else:
    print("Los archivos son idénticos.")

Logger.add_to_log("debug", "Coordenadas mensulas comparadas (ver terminal)")

print('hecho')
Logger.add_to_log('info', '-------FIN PROGRAMA-------')


