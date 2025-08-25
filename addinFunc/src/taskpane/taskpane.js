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
        
    // Leer archivo como ArrayBuffer
    // Sacar coordenadas de descenttramientos
    const fileCalc = "../python/Calcular_Seccionamientos.py"
    const arrayBuffersecc = await fileCalc.arrayBuffer();
    const uint8Arraysecc = new Uint8Array(arrayBuffersecc);
    // Escribir en el FS virtual de Pyodide
    pyodide.FS.writeFile(fileCalc.name, uint8Arraysecc);
    console.log(`Archivo ${fileCalc.name} cargado en Pyodide`);
    
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
import Calcular_Seccionamiento as cs
# kwargs viene de JS como JSON string
kwargs = json.loads('${JSON.stringify(kwargs)}')
print("Archivos recibidos en Python:", kwargs)

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


#nombres_postes=datos_tabla_vanos[::2, 0]
#datos_vanos= np.concatenate((np.array([0]), datos_tabla_vanos[1:-1:2,3]))
#datos_desc=datos_tabla_vanos[::2, 4].astype(float) * (-10) ##estaba en cm y lo queremos en mm
#datos_alt=datos_tabla_vanos[::2, 5]
#pki=datos_tabla_vanos[0,2]*1000 #queremos el primer pk en m
pk_i=datos_tabla_tramos[:,1]*1000
pk_f=datos_tabla_tramos[:,2]*1000
print("Datos cargados satisfactoriamente")
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

limpiar_tabla(datos_tabla_tramos)

def native_type(val):
    if isinstance(val, np.generic):  # int32, float64, etc.
        return val.item()            # convierte a int/float nativo
    return val  




# datos tabla vanos por separado
data = loadmat(secc)
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


seccionamientos=cs.calcular_Seccionamiento(datos_tabla_vanos, datos_vanos, datos_desc, datos_alt, pki, datos_tabla_tramos, Coord_trazado, npuntos, t_hc, t_hs, ro_hc, n_hhcc, tipo_pendolado, rel_comp, ancho_via, ancho_carril)
coord=seccionamientos[3]

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
  "datos_tabla_vanos": datos_validados,     
  # "tabla_datos_topografía": datos_tabla_topografía.tolist()
  "coordenadas_descentramientos": coord.tolist(),
}
# Aplicar la conversión recursiva antes de JSON

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
/*
// --- Función para volcar datos en Excel ---
async function insertIntoExcel(result) {
  await Excel.run(async (context) => {
    let sheets = context.workbook.worksheets;
    sheets.load("items/name");
    await context.sync();

    for (const [key, val] of Object.entries(result)) {
      let sheetName = key.substring(0, 31); // Excel limita nombres a 31 chars
      let existingSheet = sheets.items.find(s => s.name === sheetName);
      if (existingSheet) {
        existingSheet.delete();
      }
      let sheet = sheets.add(sheetName);

      let row = 0;

      if (Array.isArray(val)) {
        // --- Caso array ---
        if (val.length > 0 && Array.isArray(val[0])) {
          // Array 2D → tabla
          val.forEach((subRow, i) => {
            subRow.forEach((subVal, j) => {
              sheet.getCell(row + i, j).values = [[subVal]];
            });
          });
        } else {
          // Array 1D → expandir en columnas
          val.forEach((subVal, j) => {
            sheet.getCell(row, j).values = [[subVal]];
          });
        }
      } else if (typeof val === "object" && val !== null) {
        // --- Caso objeto/dict ---
        let col = 0;
        for (const [subKey, subVal] of Object.entries(val)) {
          // Poner clave en la primera fila
          sheet.getCell(0, col).values = [[subKey]];
          // Poner valor en la segunda fila
          if (Array.isArray(subVal)) {
            subVal.forEach((sv, i) => {
              sheet.getCell(1 + i, col).values = [[sv]];
            });
          } else {
            sheet.getCell(1, col).values = [[subVal]];
          }
          col++;
        }
      } else {
        // --- Caso escalar ---
        sheet.getCell(row, 0).values = [[val]];
      }
    }

    await context.sync();
  });
} */
// 🔧 Función para limpiar datos antes de insertar en Excel
function limpiarParaExcel(data) {
  return data.map(row =>
    row.map(cell => {
      if (cell === null || cell === undefined) return "";
      if (typeof cell === "number" && !isFinite(cell)) return "";
      return cell;
    })
  );
}

// 🔧 Convierte array de objetos a 2D array (keys en la primera fila)
function dictsTo2DArray(dicts) {
  if (!Array.isArray(dicts) || dicts.length === 0) return [[]];
  const headers = Object.keys(dicts[0]);
  const values = dicts.map(obj => headers.map(h => obj[h]));
  return [headers, ...values];
}

// --- Función para insertar datos en Excel ---
async function insertIntoExcel(resultObj) {
  await Excel.run(async (context) => {
    try {
      const sheets = context.workbook.worksheets;

      for (const [sheetName, datos] of Object.entries(resultObj)) {
        if (!datos || datos.length === 0) {
          console.warn(`⚠️ Hoja ${sheetName} sin datos, se omite.`);
          continue;
        }

        // Limitar nombre a 31 caracteres (Excel)
        const safeSheetName = sheetName.substring(0, 31);

        // Borrar hoja si existe
        let existingSheet;
        try {
          existingSheet = sheets.getItem(safeSheetName);
          existingSheet.delete();
          await context.sync(); // 🔑 Esperar antes de crear otra
        } catch (e) {
          // La hoja no existía, ok
        }

        // Crear hoja nueva
        const sheet = sheets.add(safeSheetName);

        // Preparar datos
        let datosLimpios;
        if (Array.isArray(datos)) {
          if (datos.length > 0 && Array.isArray(datos[0])) {
            datosLimpios = limpiarParaExcel(datos); // 2D array
          } else if (typeof datos[0] === "object") {
            datosLimpios = dictsTo2DArray(datos);   // array de objetos → 2D
          } else {
            datosLimpios = datos.map(d => [d]);    // 1D array → columna
          }
        } else if (typeof datos === "object" && datos !== null) {
          // objeto/dict → clave/valor
          datosLimpios = dictsTo2DArray([datos]);
        } else {
          datosLimpios = [[datos]]; // escalar
        }

        // Insertar datos
        const rango = sheet.getRangeByIndexes(
          0,
          0,
          datosLimpios.length,
          datosLimpios[0].length
        );
        rango.values = datosLimpios;

        rango.format.autofitColumns();
        rango.format.autofitRows();

        console.log(`✅ Datos insertados en la hoja: ${safeSheetName}`);
      }

      await context.sync();
    } catch (err) {
      console.error("❌ Error al insertar datos en Excel:", err);
    }
  });
}




// --- Botón para ejecutar ---
document.getElementById("loadFiles").addEventListener("click", getFiles);
