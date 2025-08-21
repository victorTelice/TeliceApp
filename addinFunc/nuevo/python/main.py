from scipy.io import loadmat
import numpy as np
import pandas as pd
import xlwings as xw
import DatoVano
import urllib.request
import urllib.parse
import json
from datetime import datetime
import math

input("Presiona Enter para empezar el procesamiento...")

# Cargar archivo .secc
data = loadmat('Pall_L900_47_338-04 a 339-12.secc')
data_cln = {k: v for k, v in data.items() if not k.startswith('__')}
print(f"Variables encontradas: {list(data_cln.keys())}")

datos_tabla_vanos = data_cln.get('datos_tabla_vanos')
if datos_tabla_vanos is None:
    print("❌ No se encontró 'datos_tabla_vanos'")
    exit()

# Normalizar y limpiar filas
filas = []
for fila in datos_tabla_vanos:
    fila_flat = []
    for val in fila:
        if isinstance(val, np.ndarray):
            if val.size == 0:
                fila_flat.append(None)
            elif val.size == 1:
                fila_flat.append(val.item())
            else:
                fila_flat.append(val.tolist())
        else:
            fila_flat.append(val)
    filas.append(fila_flat)
datos_validados = []
resultados_operacion_chorra = []

for i in range(len(filas)):
    pk_km = filas[i][2]
    vanos_m = filas[i][3]
    # Si vanos_m es None, intentar cogerlo de la siguiente fila
    if vanos_m is None and i + 1 < len(filas):
        vanos_m = filas[i + 1][3]
    print(f"Fila: pk_km={pk_km}, vanos_m={vanos_m}")
    

    if pk_km is None or vanos_m is None:
        continue
    if (isinstance(pk_km, float) and math.isnan(pk_km)) or (isinstance(vanos_m, float) and math.isnan(vanos_m)):
        continue

    try:
        dato = DatoVano.DatoVano(
            poste=filas[i][0],
            tipo_mensula=filas[i][1],
            pk_km=pk_km,
            vanos_m=vanos_m,
            descentramiento_cm=filas[i][4],
            altura_hhcc_cm=filas[i][5]
        )
        fila_dict = dato.model_dump()
        datos_validados.append(fila_dict)

        pk = dato.pk_km
        vanos = dato.vanos_m
        if pk is None or vanos is None:
            resultados_operacion_chorra.append(None)
            continue

        if (isinstance(pk, float) and math.isnan(pk)) or (isinstance(vanos, float) and math.isnan(vanos)):
            resultados_operacion_chorra.append(None)
            continue

        url = f"http://localhost:8000/calculochorra/?pk_km={pk}&vanos_m={vanos}"
        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read().decode())
            resultado = result.get("resultado")

        resultados_operacion_chorra.append(resultado)

    except Exception as e:
        print(f"Error procesando fila {filas[i]}: {e}")
        resultados_operacion_chorra.append(None)

# Luego agregar la columna resultado al DataFrame:
df = pd.DataFrame(datos_validados)
print (df)
df['resultado_operacion_chorra'] = resultados_operacion_chorra

# Exportar a Excel si el DataFrame no está vacío
if not df.empty:
    print( df)
    book = xw.Book("Trazado_procesado.xlsx")
    @xw.func
    def hello():
        return "Hello from xlwings!"
    sheet = book.sheets[0]
    sheet.range("A1").value = [df.columns.tolist()] + df.values.tolist()
    sheet['Z9'].value=hello()
    book.save("Trazado_procesado.xlsx")
    print(f"📤 Guardado como Trazado_procesado.xlsx")
else:
    print("⚠️ El DataFrame está vacío, no se exporta a Excel")
    print(df)
