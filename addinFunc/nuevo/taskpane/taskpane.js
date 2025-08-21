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


async function runPipeline() {
  // Recoger archivos de los inputs HTML
  const files = {
    via: document.getElementById("fileInputVia")?.files[0],
    cond: document.getElementById("fileInputCond")?.files[0],
    trz: document.getElementById("fileInputTrz")?.files[0],
    secc: document.getElementById("fileInputSecc")?.files[0],
    defmen: document.getElementById("fileInputDefMen")?.files[0],
    hermen: document.getElementById("fileInputHerMen")?.files[0],
    hercat: document.getElementById("fileInputHerCat")?.files[0],
  };

  // Subir archivos al FS de Pyodide
  const kwargs = {};
  for (const [key, file] of Object.entries(files)) {
    if (file) {
      const data = new Uint8Array(await file.arrayBuffer());
      pyodide.FS.writeFile(file.name, data);
      kwargs[key] = file.name; // pasamos el path al pipeline
    }
  }

  console.log("📂 Archivos pasados a Pyodide:", kwargs);
  const kwargsJSON = JSON.stringify(kwargs);
  // Construir llamada a pipeline
  const pyCode = `
import json
from scipy.io import loadmat
import js

# recoger kwargs de JS
kwargs = json.loads('${JSON.stringify(kwargs)}')
resultados = {}

# Conductores
if "cond" in kwargs:
    cond_data = loadmat(kwargs["cond"])
    resultados["conductores"] = {
        "s_hc": cond_data.get("s_hc", []),
        "t_hc": cond_data.get("t_hc", []),
        "ro_hc": cond_data.get("ro_hc", []),
        "s_hs": cond_data.get("s_hs", []),
        "t_hs": cond_data.get("t_hs", []),
        "ro_hs": cond_data.get("ro_hs", []),
        "tipo_pendolado": cond_data.get("tipo_pendolado", []),
        "n_hhcc": cond_data.get("n_hhcc", []),
    }

# Herrajes ménsula
if "hermen" in kwargs:
    her_men = loadmat(kwargs["hermen"])
    resultados["herrajes_mensula"] = {
        "herrajes_mensula": her_men.get("herrajes_mensula", []),
        "medidas": her_men.get("medidas_herrajes_mensula", []),
        "matriz": her_men.get("matriz_herrajes_mensula", []),
    }

# Herrajes catenaria
if "hercat" in kwargs:
    her_cat = loadmat(kwargs["hercat"])
    resultados["herrajes_catenaria"] = {
        "herrajes_catenaria": her_cat.get("herrajes_catenaria", []),
        "medidas": her_cat.get("medidas_herrajes_catenaria", []),
        "matriz": her_cat.get("matriz_herrajes_catenaria", []),
    }

# Definiciones de ménsula
if "defmen" in kwargs:
    def_men = loadmat(kwargs["defmen"])
    resultados["def_mesula"] = {
        "elegir_mensula_valor": def_men.get("elegir_mensula_valor", []),
        "biblioteca_escogida": def_men.get("biblioteca_escogida", []),
        "grapas_b1": def_men.get("grapas_b1", []),
        "terminales_b1": def_men.get("terminales_b1", []),
        "parametros_b1": def_men.get("parametros_b1", []),
        "otrosherrajes_b1": def_men.get("otrosherrajes_b1", []),
        "grapas_b2": def_men.get("grapas_b2", []),
        "terminales_b2": def_men.get("terminales_b2", []),
        "parametros_b2": def_men.get("parametros_b2", []),
        "otrosherrajes_b2": def_men.get("otrosherrajes_b2", []),
        "grapas_cola": def_men.get("grapas_cola", []),
        "terminales_cola": def_men.get("terminales_cola", []),
        "parametros_cola": def_men.get("parametros_cola", []),
        "otrosherrajes_cola": def_men.get("otrosherrajes_cola", []),
        "grapas_vertical": def_men.get("grapas_vertical", []),
        "terminales_vertical": def_men.get("terminales_vertical", []),
        "parametros_vertical": def_men.get("parametros_vertical", []),
        "otrosherrajes_vertical": def_men.get("otrosherrajes_vertical", []),
        "matriz_herrajes_mensula": def_men.get("matriz_herrajes_mensula", []),
        "herrajes_mensula": def_men.get("herrajes_mensula", []),
        "medidas_herrajes_mensula": def_men.get("medidas_herrajes_mensula", []),
    }

# Trazado
if "trz" in kwargs:
    trazado_data = loadmat(kwargs["trz"])
    resultados["trazado"] = {
        "Coord3D": trazado_data.get("Coord3D", []),
        "Coord_trazado": trazado_data.get("Coord_trazado", []),
        "datos_in": trazado_data.get("datos_in", []),
        "np": trazado_data.get("np", []),
        "datos_tabla_tramos": trazado_data.get("datos_tabla_tramos", []),
    }

# Seccionamientos
if "secc" in kwargs:
    secc_data = loadmat(kwargs["secc"])
    resultados["seccionamientos"] = {
        "Coord_seccionamientos_eje": secc_data.get("Coord_seccionamientos_eje", []),
        "vectores_normal": secc_data.get("vectores_normal", []),
        "datos_tabla_vanos": secc_data.get("datos_tabla_vanos", []),
        "p_tabla_tipo": secc_data.get("p_tabla_tipo", []),
        "Coord_descentramientos": secc_data.get("Coord_descentramientos", []),
        "Fhc_Calculo": secc_data.get("Fhc_Calculo", []),
        "rel_comp": secc_data.get("rel_comp", []),
    }


# devolver JSON
json.dumps(resultados, default=lambda x: x.tolist() if hasattr(x, "tolist") else x)
  `;

  const resultJson = await pyodide.runPythonAsync(pyCode);
  const result = JSON.parse(resultJson);
  console.log("📊 Variables desde Pyodide (JSON):", result);


  // Mostrar en HTML
  document.getElementById("output").textContent = JSON.stringify(result, null, 2);

  // Insertar en Excel
  await insertIntoExcel(result);
}

// --- Función para volcar datos en Excel ---
async function insertIntoExcel(result) {
  await Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();

    let row = 0;
    for (const [key, val] of Object.entries(result)) {
      // Nombre de variable en primera columna
      sheet.getCell(row, 0).values = [[key]];

      if (Array.isArray(val)) {
        if (val.length > 0 && Array.isArray(val[0])) {
          // Caso array 2D → tabla
          val.forEach((subRow, i) => {
            subRow.forEach((subVal, j) => {
              sheet.getCell(row + i, j + 1).values = [[subVal]];
            });
          });
          row += val.length;
        } else {
          // Caso array 1D → expandir en columnas
          val.forEach((subVal, j) => {
            sheet.getCell(row, j + 1).values = [[subVal]];
          });
          row++;
        }
      } else {
        // Escalar
        sheet.getCell(row, 1).values = [[val]];
        row++;
      }
    }

    await context.sync();
  });
}

// --- Botón para ejecutar ---
document.getElementById("loadFiles").addEventListener("click", runPipeline);
