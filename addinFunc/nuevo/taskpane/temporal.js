/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global console, document, Excel, Office */
/* import pipelineFileData from "./pipeline.py";
let pipelineReady = false;

async function loadPipeline() {
  if (pipelineReady) return; // Evitar recargarlo varias veces
  if (!pipelineFileData) {
    console.error("❌ No se pudo cargar pipeline.py");
    return;
  }
  // 🔹 Escribe el archivo en el sistema de ficheros virtual de Pyodide
  pyodide.FS.writeFile("pipeline.py", pipelineFileData);

  pipelineReady = true;
  console.log("✅ pipeline.py cargado en Pyodide");
}

let pyodide;

async function initPyodide() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
  });
  
  // Carga los paquetes necesarios
  await pyodide.loadPackage("numpy");
  await pyodide.loadPackage("pandas");
  await pyodide.loadPackage("scipy");
  //await pyodide.loadPackage("json");
  console.log("✅ Pyodide y paquetes listos");

}

Office.onReady(async (info) => {
  if (info.host === Office.HostType.Excel) {
    await initPyodide();
  }
});
async function dumpToExcel(fileName, pyPath, sheetName) {

await loadPipeline(); 
// Ejecutar el código Python para procesar el archivo
const retorno = await pyodide.runPythonAsync(`
    import pipeline
    pipeline.resultados_js  # <- el dict convertido
`);

console.log("📊 Variables listas para Excel:", retorno);

// Ejemplo: volcar directamente una de las matrices
await writeTableToExcel(retorno["Coord_trazado"], "Coord_Trazado");
}


// Convierte dict estilo {col: [..], col2: [..]} en Array 2D para Excel
function proxyToValues(jsObj) {
  const columns = Object.keys(jsObj); // ["ancho_via", "ancho_carril"]
  const rows = [];

  const numRows = jsObj[columns[0]].length;
  for (let i = 0; i < numRows; i++) {
    rows.push(columns.map(col => jsObj[col][i]));
  }

  return [columns, ...rows]; // encabezados + filas
}


async function writeTableToExcel(pyDf, sheetName) {
  const values = proxyToValues(pyDf);

  await Excel.run(async (context) => {
    let sheet;
    try {
      // Intentar obtener hoja existente
      sheet = context.workbook.worksheets.getItem(sheetName);
      sheet.load("name");
      await context.sync();
    } catch (e) {
      // Si no existe, la creamos
      sheet = context.workbook.worksheets.add(sheetName);
    }

    // Calcular dimensiones
    const rowCount = values.length;
    const colCount = values[0].length;

    // Escribir la tabla desde A1
    const range = sheet.getRangeByIndexes(0, 0, rowCount, colCount);
    range.values = values;

    await context.sync();
  });
}
document.getElementById("loadFiles").addEventListener("click", async () => {
  const viaFile = document.getElementById("fileVia").files[0];
  const cndFile = document.getElementById("fileCond").files[0];
  const HerMenFile = document.getElementById("fileHerMen").files[0];
  const HerCatFile = document.getElementById("fileHerCat").files[0];
  const DefMenFile = document.getElementById("fileDefMen").files[0];
  const trzFile = document.getElementById("fileTrz").files[0];
  const seccFile = document.getElementById("fileSecc").files[0];
  

  // Guardar cada archivo en el FS virtual de Pyodide
  async function saveToPyodide(file) {
    if (!file) return null;
    const data = new Uint8Array(await file.arrayBuffer());
    console.log(`📂 Guardando archivo ${file.name} en Pyodide...`);
    console.log(`Data ${data} de ${data.length} bytes`);
    pyodide.FS.writeFile(file.name, data);
    return file.name; // nombre como ruta
  }

  const viaPath = await saveToPyodide(viaFile);
  const cndPath = await saveToPyodide(cndFile);
  const seccPath = await saveToPyodide(seccFile);
  const trzPath = await saveToPyodide(trzFile);
  const DefMenPath = await saveToPyodide(DefMenFile);
  const HerMenPath = await saveToPyodide(HerMenFile);
  const HerCatPath = await saveToPyodide(HerCatFile);
  

  // Ahora sí, usar dumpToExcel con los paths que acaban de entrar
  if (viaPath) await dumpToExcel("Via", viaPath, "VIA");
  if (cndPath) await dumpToExcel("Conductores", cndPath, "Conductores");
  if (seccPath) await dumpToExcel("Seccionamiento", seccPath, "Seccionamiento");
  if (trzPath) await dumpToExcel("Trazado", trzPath, "Trazado");
  if (DefMenPath) await dumpToExcel("Definición de Mensulas", DefMenPath, "Definición de Mensulas");
  if (HerMenPath) await dumpToExcel("Herrajes de Mensulas", HerMenPath, "Herrajes de Mensulas");
  if (HerCatPath) await dumpToExcel("Herrajes de Catenaria", HerCatPath, "Herrajes de Catenaria");
}); */



/* // Procesar archivo subido Seccionamientos 
async function processFileSecc() {
  const fileInput = document.getElementById("fileInputSecc");
  const file = fileInput.files[0];

  if (!file) {
    alert("Selecciona un archivo .secc");
    return;
  }
  if (!file.name.endsWith(".secc")) {
    alert("El archivo debe ser .secc");
    return;
  }

  // Leer el archivo en JS
  const arrayBuffer = await file.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);

  // Pasar archivo al FS virtual de Pyodide
  pyodide.FS.writeFile(file.name, uint8Array);

  // Ejecutar Python
  const code = `
import numpy as np
import pandas as pd
from scipy.io import loadmat
import math

fname = "${file.name}"
data = loadmat(fname)
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
`;
  const result = await pyodide.runPythonAsync(code);

  // Convertir JSON -> JS
  const df = JSON.parse(result);
  console.log("📊 DataFrame:", df);
  console.log("💔 DataFrame:", df.values);
  // Mostrar en HTML
  document.getElementById("output").textContent = JSON.stringify(df, null, 2);

  // Insertar en Excel
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();

    // Encabezados
    df.columns.forEach((col, j) => {
      const cell = sheet.getCell(0, j);
      cell.values = [[col]];
    });

    // Filas
    df.data.forEach((row, i) => {
      row.forEach((val, j) => {
        const cell = sheet.getCell(i + 1, j);
        cell.values = [[val]];
      });
    });

    await context.sync();
    });
} */



/* global console, document, Excel, Office */
import pipelineFileData from "./pipeline.py";

let pyodide;
let pipelineReady = false;

async function initPyodide() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
  });

  await pyodide.loadPackage(["numpy", "pandas", "scipy"]);
  console.log("✅ Pyodide y paquetes listos");
}

async function loadPipeline() {
  if (pipelineReady) return;
  if (!pipelineFileData) {
    console.error("❌ No se pudo cargar pipeline.py");
    return;
  }
  pyodide.FS.writeFile("pipeline.py", pipelineFileData);
  pipelineReady = true;
  console.log("✅ pipeline.py cargado en Pyodide");
}

// Guardar archivos en FS virtual
async function saveToFS(file) {
  if (!file) return null;
  const data = new Uint8Array(await file.arrayBuffer());
  pyodide.FS.writeFile("/tmp/" + file.name, data);
  console.log(`📂 Guardado ${file.name} (${data.length} bytes)`);
  return "/tmp/" + file.name;
}

// Convierte dict estilo {col: [..]} en array 2D
function proxyToValues(jsObj) {
  const columns = Object.keys(jsObj);
  const numRows = jsObj[columns[0]].length;
  const rows = [];
  for (let i = 0; i < numRows; i++) {
    rows.push(columns.map(col => jsObj[col][i]));
  }
  return [columns, ...rows];
}

// Escribir tabla en Excel
async function writeTableToExcel(pyDf, sheetName) {
  const values = proxyToValues(pyDf);
  await Excel.run(async (context) => {
    let sheet;
    try {
      sheet = context.workbook.worksheets.getItem(sheetName);
      await context.sync();
    } catch (e) {
      sheet = context.workbook.worksheets.add(sheetName);
    }
    const range = sheet.getRangeByIndexes(0, 0, values.length, values[0].length);
    range.values = values;
    await context.sync();
  });
}

// Ejecutar pipeline y volcar a Excel
async function runPipeline(paths) {
  await loadPipeline();
  const retorno = await pyodide.runPythonAsync(`
from pipeline import Pipeline
from pyodide.ffi import to_js
p = Pipeline(
    via="${paths.via || ""}",
    cond="${paths.cond || ""}",
    trz="${paths.trz || ""}",
    secc="${paths.secc || ""}",
    defmen="${paths.defmen || ""}",
    hermen="${paths.hermen || ""}",
    hercat="${paths.hercat || ""}"
)
to_js(p.run(), dict_converter=dict)
  `);
  console.log("📊 Resultados:", retorno);

  for (const [sheetName, data] of Object.entries(retorno)) {
    await writeTableToExcel(data, sheetName);
  }
}

Office.onReady(async (info) => {
  if (info.host === Office.HostType.Excel) {
    await initPyodide();
  }
});

document.getElementById("loadFiles").addEventListener("click", async () => {
  const paths = {
    via: await saveToFS(document.getElementById("fileVia").files[0]),
    cond: await saveToFS(document.getElementById("fileCond").files[0]),
    trz: await saveToFS(document.getElementById("fileTrz").files[0]),
    secc: await saveToFS(document.getElementById("fileSecc").files[0]),
    defmen: await saveToFS(document.getElementById("fileDefMen").files[0]),
    hermen: await saveToFS(document.getElementById("fileHerMen").files[0]),
    hercat: await saveToFS(document.getElementById("fileHerCat").files[0])
  };

  await runPipeline(paths);
});





// otra forma
// Función genérica para leer y escribir archivos en Pyodide
async function uploadFile(inputId) {
  const fileInput = document.getElementById(inputId);
  const file = fileInput.files[0];

  if (!file) {
    alert(`Selecciona un archivo para ${inputId}`);
    return;
  }

  // Aquí puedes controlar extensiones si quieres
  // if (!file.name.endsWith(".xyz")) { alert("Debe ser .xyz"); return; }

  const arrayBuffer = await file.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);

  pyodide.FS.writeFile(file.name, uint8Array);
}

// Usar la función para cada input
await uploadFile("fileInputDefmen");
await uploadFile("fileInputTrz");
await uploadFile("fileInputSecc");
