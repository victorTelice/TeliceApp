// taskpane.js
//import pipeline from "./pipeline.py"
let pyodide;

async function initPyodide() {
  console.log("🔄 Cargando Pyodide...");
  pyodide = await loadPyodide();
  await pyodide.loadPackage(["numpy", "pandas", "scipy"]);
  console.log("✅ Pyodide listo");

  // Cargar pipeline.py en el FS virtual
  //pyodide.FS.writeFile("pipeline.py", pipeline);
  //await pyodide.runPythonAsync("import pipeline");
}

initPyodide();


async function getFiles() {
  // Recoger archivos de los inputs HTML
  let kwargs = {};
   try{
    const fileInput = document.getElementById("fileSecc");
    const seccFile = fileInput.files[0];
    const fileInput1=document.getElementById("fileVia");
    const viaFile = fileInput1.files[0];
    const fileInput2=document.getElementById("fileCond");
    const cndFile = fileInput2.files[0];
    const fileInput3=document.getElementById("fileTrz");
    const trzFile = fileInput3.files[0];
    const fileInput4=document.getElementById("fileDefMen");
    const defMenFile = fileInput4.files[0];
    const fileInput5=document.getElementById("fileHerMen");
    const herMenFile = fileInput5.files[0];
    const fileInput6=document.getElementById("fileHerCat");
    const HerCatFile = fileInput6.files[0];
 
    const arrayBuffer = await seccFile.arrayBuffer();
    const uint8Array = new Uint8Array(arrayBuffer);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(seccFile.name, uint8Array);
    console.log(`📂 Archivo ${seccFile.name} cargado en Pyodide FS`);


    const arrayBuffer1 = await viaFile.arrayBuffer();
    const uint8Array1 = new Uint8Array(arrayBuffer1);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(viaFile.name, uint8Array1);
    console.log(`📂 Archivo ${viaFile.name} cargado en Pyodide FS`);


    const arrayBuffer2 = await cndFile.arrayBuffer();
    const uint8Array2 = new Uint8Array(arrayBuffer2);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(cndFile.name, uint8Array2);
    console.log(`📂 Archivo ${cndFile.name} cargado en Pyodide FS`);


    const arrayBuffer3 = await trzFile.arrayBuffer();
    const uint8Array3 = new Uint8Array(arrayBuffer3);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(trzFile.name, uint8Array3);
    console.log(`📂 Archivo ${trzFile.name} cargado en Pyodide FS`);


    const arrayBuffer4 = await defMenFile.arrayBuffer();
    const uint8Array4 = new Uint8Array(arrayBuffer4);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(defMenFile.name, uint8Array4);
    console.log(`📂 Archivo ${defMenFile.name} cargado en Pyodide FS`);


    const arrayBuffer5 = await herMenFile.arrayBuffer();
    const uint8Array5 = new Uint8Array(arrayBuffer5);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(herMenFile.name, uint8Array5);
    console.log(`📂 Archivo ${herMenFile.name} cargado en Pyodide FS`);


    const arrayBuffer6 = await HerCatFile.arrayBuffer();
    const uint8Array6 = new Uint8Array(arrayBuffer6);
    // Pasar archivo al FS virtual de Pyodide
    pyodide.FS.writeFile(HerCatFile.name, uint8Array6);
    console.log(`📂 Archivo ${HerCatFile.name} cargado en Pyodide FS`);
        
    // Cargar el archivo Python desde la carpeta python
    const response = await fetch("./python/Calcular_Seccionamiento_f.py");
    const code = await response.text();

    // Guardar en FS de Pyodide
    pyodide.FS.writeFile("Calcular_Seccionamiento_f.py", code);
    console.log("📂 Archivo Python Calcular_Seccionamiento cargado en Pyodide");


    // Cargar el archivo Python desde la carpeta python
    const responseFR = await fetch("./python/Fr_Calculo_f.py");
    const codeFR = await responseFR.text();

    // Guardar en FS de Pyodide
    pyodide.FS.writeFile("Fr_Calculo_f.py", codeFR);
    console.log("📂 Archivo Python calc_FR cargado en Pyodide");

    // Cargar el archivo Python desde la carpeta python
    const responseFV = await fetch("./python/Fv_Calculo_f.py");
    const codeFV = await responseFV.text();

    // Guardar en FS de Pyodide
    pyodide.FS.writeFile("Fv_Calculo_f.py", codeFV);
    console.log("📂 Archivo Python calc_FR cargado en Pyodide");
    
    

    // Cargar logger.py
    const responseUtils = await fetch("./python/logger.py");
    const codeUtils = await responseUtils.text();

    // Guardar en FS de Pyodide dentro de /utils
    pyodide.FS.writeFile("logger.py", codeUtils);

    console.log("📂 Archivo Python logger cargado en Pyodide");

        // Creamos el diccionario kwargs en JS con rutas
    kwargs = {
      secc: seccFile.name,
      via: viaFile.name,
      cnd: cndFile.name,
      trz: trzFile.name,
      defMen: defMenFile.name,
      herMen: herMenFile.name,
      herCat: HerCatFile.name,
    };

    // Guardamos en el entorno global de Pyodide
    pyodide.globals.set("kwargs", kwargs);
  }

  catch (e) {
    console.error("Error al leer archivo:", e);
    return;
  }

const pyCode = `
import json
from scipy.io import loadmat
import numpy as np
import pandas as pd
import math
import Calcular_Seccionamiento_f as cs
# kwargs viene de JS como JSON string
kwargs = json.loads('${JSON.stringify(kwargs)}')
print("Archivos recibidos en Python:", kwargs)



def to_serializable(obj):
    """Convierte objetos de NumPy a tipos nativos JSON serializables."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()  # array -> lista anidada
    if isinstance(obj, np.generic):
        return obj.item()    # int32, float64 -> int o float
    if isinstance(obj, (list, tuple)):
        return [to_serializable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    return obj

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





resultados = {}

def aplanar_varias_veces(array, veces):
    resultado = array
    for _ in range(veces):
        resultado = [item for subarray in resultado for item in subarray]
    return resultado
# Construcción de las rutas de archivo
biblioteca_via = kwargs['via']
print("Ruta de archivo de vía:", biblioteca_via)
biblioteca_conductores = kwargs['cnd']
print("Ruta de archivo de conductores:", biblioteca_conductores)
biblioteca_her_men = kwargs['herMen']
print("Ruta de archivo de herrajes mensula:", biblioteca_her_men)
biblioteca_her_cat = kwargs['herCat'] 
biblioteca_def_men = kwargs['defMen']
trazado = kwargs['trz']
secc = kwargs['secc']
print("Rutas de archivo:", biblioteca_via, biblioteca_conductores, biblioteca_her_men, biblioteca_her_cat, biblioteca_def_men, trazado, secc)

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
print(type(herrajes_mensula))
medidas_herrajes_mensula=aplanar_varias_veces(her_men_data['medidas_herrajes_mensula'],2) 
print(type(medidas_herrajes_mensula))
matriz_herrajes_mensula = her_men_data['matriz_herrajes_mensula']
print(type(matriz_herrajes_mensula))

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

data = loadmat(secc)
Coord_seccionamientos_eje = data['Coord_seccionamientos_eje']
vectores_normal=data['vectores_normal']
datos_tabla_vanos=data['datos_tabla_vanos']
p_tabla_tipo=data['p_tabla_tipo']
Coord_descentramientos=data['Coord_descentramientos']
Fhc_Calculo=data['Fhc_Calculo']
rel_comp=data['rel_comp']

nombres_postes=datos_tabla_vanos[::2, 0]
print("nombres_postes: ", limpiar_tabla(nombres_postes))
datos_vanos= np.concatenate((np.array([0]), datos_tabla_vanos[1:-1:2,3]))
print("datos vanos: ", to_serializable(datos_vanos))
datos_desc=datos_tabla_vanos[::2, 4].astype(float) * (-10) ##estaba en cm y lo queremos en mm
print("datos desc: ", to_serializable(datos_desc))
datos_alt=datos_tabla_vanos[::2, 5]
print("datos alt: ", to_serializable(datos_alt))
pki=datos_tabla_vanos[0,2]*1000 #queremos el primer pk en m
print("pki: ", to_serializable(pki))
pk_i=datos_tabla_tramos[:,1]*1000
pk_f=datos_tabla_tramos[:,2]*1000
tipo=datos_tabla_vanos[:,1]
print("tipo: ", limpiar_tabla(tipo))

datos_tabla_vanos_Excel={
    "postes": limpiar_tabla(nombres_postes),
    "tipo": limpiar_tabla(tipo),
    "vanos": to_serializable(datos_vanos),
    "desc": to_serializable(datos_desc),
    "alturas": to_serializable(datos_alt),
    "pki": to_serializable(pki)
}
print("datos tabla vanos: ")
print(datos_tabla_vanos_Excel)


print("Datos cargados satisfactoriamente")






limpiar_tabla(datos_tabla_tramos)

def native_type(val):
    if isinstance(val, np.generic):  # int32, float64, etc.
        return val.item()            # convierte a int/float nativo
    return val  




# datos tabla vanos por separado

data_cln = {k: v for k, v in data.items() if not k.startswith('__')}

datos_tabla_vanos = data_cln.get('datos_tabla_vanos')
filas = []
if datos_tabla_vanos is not None:
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

import sys
if "" not in sys.path:
  sys.path.append("")  # permite imports relativos desde la raíz
seccionamientos=cs.Seccionamientos_Calculo_f(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, ancho_via, ancho_carril)
print("coordenadas seccionamiento: ", seccionamientos[3])
coord=seccionamientos[3]
fR=seccionamientos[4]
print("fR: ", fR)
fv=seccionamientos[5]
print("fv: ", fv)
datos_validados = []
for i in range(len(filas)):
    pk_km = filas[i][2]
    vanos_m = filas[i][3]
    if vanos_m is None and i + 1 < len(filas):
        vanos_m = filas[i + 1][3]

    if pk_km is None or vanos_m is None:
        continue
    if (isinstance(pk_km, float) and math.isnan(pk_km)) or (isinstance(vanos_m, float) and math.isnan(vanos_m)):
        continue

    fila_dict = {
        "poste": filas[i][0],
        "tipo_mensula": filas[i][1],
        "pk_km": pk_km,
        "vanos_m": vanos_m,
        "descentramiento_cm": filas[i][4],
        "altura_hhcc_cm": filas[i][5]
    }
    datos_validados.append(fila_dict)

df = pd.DataFrame(datos_validados)
df.to_json(orient="split")    

resultados={
  "via": {
    "ancho_via": float(ancho_via),
    "ancho_carril": float(ancho_carril)
  },
  "conductores": {
      "s_hc": s_hc.tolist(),
      "t_hc": t_hc.tolist(),
      "ro_hc": ro_hc.tolist(),
      "s_hs": s_hs.tolist(),
      "t_hs": t_hs.tolist(),
      "ro_hs": ro_hs.tolist(),
      "tipo_pendolado":  native_type(tipo_pendolado),
      "n_hhcc":  native_type(n_hhcc)
  },
  "datos_tabla_tramos": limpiar_tabla(datos_tabla_tramos), 
  "datos_tabla_vanos": datos_tabla_vanos_Excel,     
  # "tabla_datos_topografía": datos_tabla_topografía.tolist()
  "coordenadas_descentramientos": coord.tolist(),
}
# Aplicar la conversión recursiva antes de JSON


resultados_json = json.dumps(to_serializable(resultados))

resultados_json

`;

  const resultJson = await pyodide.runPythonAsync(pyCode);
  const result = JSON.parse(resultJson);
  console.log("📊 Variables desde Pyodide (JSON):", result);


  // Mostrar en HTML
  document.getElementById("output").textContent = JSON.stringify(result, null, 2);

  // Insertar en Excel
  await insertIntoExcel(result);
}

/* function limpiarParaExcel(data) {
  return data.map(row =>
    row.map(cell => {
      if (cell === null || cell === undefined) return "";
      if (typeof cell === "number" && !isFinite(cell)) return "";
      return cell;
    })
  );
} */

/* // 🔧 Convierte array de objetos a 2D array (keys en la primera fila)
function dictsTo2DArray(dicts) {
  if (!Array.isArray(dicts) || dicts.length === 0) return [[]];
  const headers = Object.keys(dicts[0]);
  const values = dicts.map(obj => headers.map(h => obj[h]));
  return [headers, ...values];
} */
/* function dictOfArraysTo2DRelaxed(dict) {
  const keys = Object.keys(dict);
  const maxLen = Math.max(...keys.map(k => dict[k].length));
  const rows = [];

  // cabeceras
  rows.push(keys);

  for (let i = 0; i < maxLen; i++) {
    const row = keys.map(k => {
      const col = dict[k];
      if (i < col.length) {
        let val = col[i];
        if (Array.isArray(val) && val.length === 1) val = val[0]; // desempaquetar [[x]]
        return val ?? "";
      } else {
        return ""; // no hay dato → celda vacía
      }
    });
    rows.push(row);
  }

  return rows;
} */

// --- Función para insertar datos en Excel MÁS ROBUSTA ---
async function insertIntoExcel(resultObj) {
  console.log("🔍 Iniciando inserción en Excel con datos:", resultObj);
  
  // Procesar cada hoja por separado para evitar sobrecargar Excel
  for (const [sheetName, datos] of Object.entries(resultObj)) {
    console.log(`📝 Procesando hoja individual: ${sheetName}`);
    
    try {
      await insertSingleSheet(sheetName, datos);
      console.log(`✅ Hoja completada: ${sheetName}`);
      
      // Pequeña pausa entre hojas para dar tiempo a Excel
      await new Promise(resolve => setTimeout(resolve, 100));
      
    } catch (error) {
      console.error(`❌ Error en hoja ${sheetName}:`, error);
      // Continuar con las otras hojas aunque una falle
    }
  }
  
  console.log("🎉 Proceso de inserción completado");
}

// Función auxiliar para insertar una sola hoja
async function insertSingleSheet(sheetName, datos) {
  return await Excel.run(async (context) => {
    try {
      if (!datos) {
        console.warn(`⚠️ Hoja ${sheetName} sin datos, se omite.`);
        return;
      }

      // Limitar nombre a 31 caracteres (Excel)
      const safeSheetName = sheetName.substring(0, 31);
      console.log(`📋 Procesando hoja: ${safeSheetName}`);

      const workbook = context.workbook;
      const sheets = workbook.worksheets;
      
      // Verificar si la hoja existe
      let existingSheet = null;
      let sheetExists = false;
      
      try {
        existingSheet = sheets.getItem(safeSheetName);
        existingSheet.load("name");
        await context.sync();
        sheetExists = true;
        console.log(`🗑️ Eliminando hoja existente: ${safeSheetName}`);
      } catch (e) {
        console.log(`📄 La hoja ${safeSheetName} no existe, se creará nueva`);
        sheetExists = false;
      }

      if (sheetExists && existingSheet) {
        existingSheet.delete();
        await context.sync();
        // Pausa después de eliminar
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      // Crear hoja nueva
      console.log(`➕ Creando nueva hoja: ${safeSheetName}`);
      const sheet = sheets.add(safeSheetName);
      await context.sync();

      // Preparar datos
      let datosLimpios;
      console.log(`🔧 Preparando datos para ${sheetName}:`, typeof datos);

      if (Array.isArray(datos)) {
        if (datos.length === 0) {
          console.warn(`⚠️ Array vacío para ${sheetName}`);
          return;
        }
        
        if (Array.isArray(datos[0])) {
          // Ya es 2D array
          datosLimpios = limpiarParaExcel(datos);
        } else if (typeof datos[0] === "object" && datos[0] !== null) {
          // Array de objetos → convertir a 2D
          datosLimpios = dictsTo2DArray(datos);
        } else {
          // Array 1D → convertir a columna
          datosLimpios = datos.map(d => [d]);
        }
      } else if (typeof datos === "object" && datos !== null) {
        // Es un objeto/diccionario
        const keys = Object.keys(datos);
        const values = Object.values(datos);
        
        // Verificar si todos los valores son arrays
        if (values.every(v => Array.isArray(v))) {
          console.log(`📊 Convirtiendo diccionario de arrays para ${sheetName}`);
          datosLimpios = dictOfArraysTo2DRobust(datos);
        } else {
          // Diccionario normal → tabla key/value
          datosLimpios = Object.entries(datos).map(([key, value]) => [key, value]);
          datosLimpios.unshift(["Parámetro", "Valor"]);
        }
      } else {
        // Valor escalar
        datosLimpios = [[datos]];
      }

      if (!datosLimpios || datosLimpios.length === 0 || datosLimpios[0].length === 0) {
        console.warn(`⚠️ No hay datos válidos para insertar en ${sheetName}`);
        return;
      }

      // Validar dimensiones
      const numRows = datosLimpios.length;
      const numCols = datosLimpios[0].length;
      
      if (numRows > 1048576 || numCols > 16384) {
        console.error(`❌ Dimensiones exceden límites de Excel: ${numRows}x${numCols}`);
        return;
      }

      console.log(`📊 Insertando ${numRows}x${numCols} celdas en ${safeSheetName}`);
      
      // Insertar datos en lotes si son muchos
      if (numRows > 1000) {
        await insertDataInBatches(sheet, datosLimpios, context);
      } else {
        // Insertar todo de una vez
        const rango = sheet.getRangeByIndexes(0, 0, numRows, numCols);
        rango.values = datosLimpios;
        await context.sync();
      }
      
      // Aplicar formato
      const fullRange = sheet.getRangeByIndexes(0, 0, numRows, numCols);
      fullRange.format.autofitColumns();
      
      // Aplicar estilo a cabeceras si hay más de una fila
      if (numRows > 1) {
        const headerRange = sheet.getRangeByIndexes(0, 0, 1, numCols);
        headerRange.format.font.bold = true;
        headerRange.format.fill.color = "#E6E6FA";
      }

      await context.sync();
      console.log(`✅ Datos insertados correctamente en: ${safeSheetName}`);
      
    } catch (err) {
      console.error(`❌ Error en hoja individual ${sheetName}:`, err);
      throw err;
    }
  });
}

// Función para insertar datos en lotes grandes
async function insertDataInBatches(sheet, data, context, batchSize = 500) {
  console.log(`📦 Insertando datos en lotes de ${batchSize} filas`);
  
  for (let i = 0; i < data.length; i += batchSize) {
    const endIndex = Math.min(i + batchSize, data.length);
    const batch = data.slice(i, endIndex);
    
    const rango = sheet.getRangeByIndexes(i, 0, batch.length, data[0].length);
    rango.values = batch;
    
    await context.sync();
    console.log(`✅ Lote insertado: filas ${i + 1} a ${endIndex}`);
    
    // Pequeña pausa entre lotes
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}

// Versión más robusta para diccionarios de arrays
function dictOfArraysTo2DRobust(dict) {
  console.log("🔄 Convirtiendo diccionario de arrays (robusto):", dict);
  
  const keys = Object.keys(dict);
  const maxLen = Math.max(...keys.map(k => {
    const arr = dict[k];
    return Array.isArray(arr) ? arr.length : 1;
  }));
  
  console.log(`📏 Máxima longitud: ${maxLen}, Claves:`, keys);
  
  const rows = [];
  
  // Cabeceras
  rows.push(keys);

  for (let i = 0; i < maxLen; i++) {
    const row = keys.map(k => {
      const col = dict[k];
      
      if (Array.isArray(col)) {
        if (i < col.length) {
          let val = col[i];
          
          // Manejar arrays anidados y valores especiales
          if (Array.isArray(val)) {
            if (val.length === 0) {
              return ""; // Array vacío
            } else if (val.length === 1) {
              val = val[0]; // Desempaquetar array de un elemento
            } else {
              return JSON.stringify(val); // Array con múltiples elementos → string
            }
          }
          
          // Manejar valores null/undefined
          if (val === null || val === undefined) {
            return "";
          }
          
          // Manejar números especiales
          if (typeof val === "number" && !isFinite(val)) {
            return "";
          }
          
          return val;
        } else {
          return ""; // Fuera del rango
        }
      } else {
        // Si no es array, solo en la primera fila
        return i === 0 ? col : "";
      }
    });
    rows.push(row);
  }

  console.log(`✅ Conversión completa: ${rows.length} filas x ${keys.length} columnas`);
  return rows;
}

// Función mejorada para limpiar datos
function limpiarParaExcel(data) {
  return data.map((row, rowIndex) => {
    if (!Array.isArray(row)) {
      return [row];
    }
    
    return row.map((cell, colIndex) => {
      // Manejar valores null/undefined
      if (cell === null || cell === undefined) return "";
      
      // Manejar números especiales
      if (typeof cell === "number" && !isFinite(cell)) return "";
      
      // Manejar objetos y arrays anidados
      if (typeof cell === "object") {
        if (Array.isArray(cell)) {
          if (cell.length === 0) return "";
          if (cell.length === 1) return cell[0];
          return JSON.stringify(cell);
        }
        return JSON.stringify(cell);
      }
      
      // Convertir a string si es muy largo
      if (typeof cell === "string" && cell.length > 32767) {
        console.warn(`⚠️ Truncando texto largo en [${rowIndex}][${colIndex}]`);
        return cell.substring(0, 32767);
      }
      
      return cell;
    });
  });
}

// Función auxiliar para arrays de objetos a 2D
function dictsTo2DArray(dicts) {
  if (!Array.isArray(dicts) || dicts.length === 0) return [[]];
  
  const headers = Object.keys(dicts[0]);
  const values = dicts.map(obj => 
    headers.map(h => {
      const val = obj[h];
      if (val === null || val === undefined) return "";
      if (typeof val === "object") return JSON.stringify(val);
      return val;
    })
  );
  
  return [headers, ...values];
}








// --- Función específica para calcular fR, se actiba con boton ---
async function CalculaFR() {
  let coordDescentramientos = [];
  let t_hc = 0;
  try {
  // Leer datos de Excel
  coordDescentramientos = await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("coordenadas_descentramientos");

    // Ojo: aquí ajusta el rango a tu número de filas reales
    const range = sheet.getUsedRange();
    range.load("values");

    await context.sync();
    return range.values; // devuelve la matriz n x 2
  });
  t_hc=await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getItem("conductores");
    const range = sheet.getRange("B2"); // t_hc en B2
    range.load("values");
    await context.sync();
    return range.values[0][0]; // devuelve el valor escalar
  });
  console.log("Matriz leída desde Excel:", coordDescentramientos);
  console.log("t_hc:", t_hc);
} catch (e) {
    console.error("Error al leer datos de Excel:", e);
    return;
  }
  // Cargar Pyodide
  const pyodide = await loadPyodide();
  console.log("✅ Pyodide listo");
  await pyodide.loadPackage(["numpy", "pandas", "scipy"]);
  
  // Cargar el archivo Python desde la carpeta python
  const responseFR = await fetch("./python/Fr_Calculo_f.py");
  const codeFR = await responseFR.text();

  // Guardar en FS de Pyodide
  pyodide.FS.writeFile("Fr_Calculo_f.py", codeFR);
  console.log("📂 Archivo Python calc_FR cargado en Pyodide");

  // Cargar el archivo Python desde la carpeta python
  const responseFV = await fetch("./python/Fv_Calculo_f.py");
  const codeFV = await responseFV.text();

  // Guardar en FS de Pyodide
  pyodide.FS.writeFile("Fv_Calculo_f.py", codeFV);
  console.log("📂 Archivo Python calc_FV cargado en Pyodide");



  // Cargar logger.py
  const responseUtils = await fetch("./python/logger.py");
  const codeUtils = await responseUtils.text();

  // Guardar en FS de Pyodide dentro de /utils
  pyodide.FS.writeFile("logger.py", codeUtils);

  console.log("📂 Archivo Python logger cargado en Pyodide");



  // Pasar la matriz y el parámetro
  //pyodide.globals.set("Coord_descentramientos", coordDescentramientos);
  //pyodide.globals.set("t_hc", t_hc);

  // Ejecutar Python
 const result= await pyodide.runPythonAsync(`
import json
from scipy.io import loadmat
import numpy as np
import Fr_Calculo_f as fr
import sys
if "" not in sys.path:
  sys.path.append("")  # permite imports relativos desde la raíz


Coord_descentramientos = json.loads('${JSON.stringify(coordDescentramientos)}')
print("coordenadas descentramiento desde JS: ", Coord_descentramientos)
coord_descentramientos = np.array(Coord_descentramientos, dtype=float)
print("coordenadas descentramiento como array numpy: ", coord_descentramientos)


# t_hc = json.loads('${JSON.stringify(t_hc)}')
t_hc = ${t_hc}
print("t_hc desde JS: ", ${t_hc})
print("t_hc : ", t_hc)


resultado = fr.Fr_Calculo_f(coord_descentramientos, t_hc)
print("fR: ", resultado)

if isinstance(resultado, np.ndarray):
    resultado = resultado.tolist()

resultado=json.dumps(resultado)  # convertir a JSON

print("resultado en python:", resultado)
resultado
  `);

  console.log("Resultado Python:", result);
  const parsed = JSON.parse(result); // array de arrays
  parsed.map(v => [v]); // asegurar 2D (columna en Excel)
  console.log("excelInput: ", parsed);
  insertIntoExcel({"Fr_Calculo_f": parsed});
  return result;
}




// --- Botón para ejecutar ---
document.getElementById("loadFiles").addEventListener("click", getFiles);
document.getElementById("btnCalcularFr").addEventListener("click", CalculaFR);