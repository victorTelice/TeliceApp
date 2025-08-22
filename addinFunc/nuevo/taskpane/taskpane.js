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


  // Subir archivos al FS de Pyodide
/* const kwargs = {};
for (const [key, file] of Object.entries(files)) {
  if (file) {
    const data = new Uint8Array(await file.arrayBuffer());
    pyodide.FS.writeFile(file.name, data);  // lo escribes en el FS de pyodide
    kwargs[key] = file.name;                // pasas solo el nombre a Python
  }
}
  pyodide.globals.set("kwargs", kwargs);
  console.log("📂 Archivos pasados a Pyodide:", kwargs); */

const pyCode = `
import json
from scipy.io import loadmat
import numpy as np

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



def native_type(val):
    if isinstance(val, np.generic):  # int32, float64, etc.
        return val.item()            # convierte a int/float nativo
    return val  



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
  "datos_tabla_tramos": datos_tabla_tramos.tolist(),
  "datos_tabla_vanos": datos_tabla_vanos.tolist()
  # "tabla_datos_topografía": datos_tabla_topografía.tolist()
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

// --- Función para volcar datos en Excel ---
async function insertIntoExcel(result) {
  await Excel.run(async (context) => {
    for (const [key, val] of Object.entries(result)) {
      // Crear nueva hoja para cada key
      let sheetName = key.substring(0, 31); // Excel limita nombres a 31 chars
      let sheet;

      // Si ya existe, la borramos
      try {
        context.workbook.worksheets.getItem(sheetName).delete();
      } catch (e) {
        // No existe, no pasa nada
      }

      sheet = context.workbook.worksheets.add(sheetName);

      let row = 0;
      if (Array.isArray(val)) {
        if (val.length > 0 && Array.isArray(val[0])) {
          // Caso array 2D → tabla
          val.forEach((subRow, i) => {
            subRow.forEach((subVal, j) => {
              sheet.getCell(row + i, j).values = [[subVal]];
            });
          });
        } else {
          // Caso array 1D → expandir en columnas
          val.forEach((subVal, j) => {
            sheet.getCell(row, j).values = [[subVal]];
          });
        }
      } else {
        // Escalar
        sheet.getCell(row, 0).values = [[val]];
      }
    }

    await context.sync();
  });
}

// --- Botón para ejecutar ---
document.getElementById("loadFiles").addEventListener("click", getFiles);
