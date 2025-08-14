/* global clearInterval, console, setInterval */

/**
 * Add two numbers
 * @customfunction
 * @param {number} first First number
 * @param {number} second Second number
 * @returns {number} The sum of the two numbers.
 */
export function add(first, second) {
  return first + second;
}

/**
 * Displays the current time once a second
 * @customfunction
 * @param {CustomFunctions.StreamingInvocation<string>} invocation Custom function invocation
 */
export function clock(invocation) {
  const timer = setInterval(() => {
    const time = currentTime();
    invocation.setResult(time);
  }, 1000);

  invocation.onCanceled = () => {
    clearInterval(timer);
  };
}

/**
 * Returns the current time
 * @returns {string} String with the current time formatted for the current locale.
 */
export function currentTime() {
  return new Date().toLocaleTimeString();
}

/**
 * Increments a value once a second.
 * @customfunction
 * @param {number} incrementBy Amount to increment
 * @param {CustomFunctions.StreamingInvocation<number>} invocation
 */
export function increment(incrementBy, invocation) {
  let result = 0;
  const timer = setInterval(() => {
    result += incrementBy;
    invocation.setResult(result);
  }, 1000);

  invocation.onCanceled = () => {
    clearInterval(timer);
  };
}

/**
 * Writes a message to console.log().
 * @customfunction LOG
 * @param {string} message String to write.
 * @returns String to write.
 */
export function logMessage(message) {
  console.log(message);

  return message;
}



//funciones auxiliares para cargar Pyodide y leer datos de Excel

async function leerDatosExcel() {
    return await Excel.run(async (context) => {
        // Accede al libro y la hoja activa
        const sheet = context.workbook.worksheets.getActiveWorksheet();
        
        // Lee los datos de las celdas, por ejemplo, columnas de postes y descentramientos
        const range = sheet.getRange("A2:B12"); // Rango de celdas con los datos
        range.load(["values"]); // Cargar los valores de las celdas

        await context.sync(); // Sincroniza los datos de Excel con el contexto
        console.log("Datos leídos desde Excel:", range.values);
        // Extraer los datos de los postes y los descentramientos
        const coordDescentramientos = range.values.map(row => [row[0], row[1]]); // [Poste, Descentramiento]
        let pyodide=await loadPyodide();
        console.log("Pyodide cargado correctamente.")
        const result = await pyodide.runPythonAsync(pythonCode + `Fr_Calculo_f(${JSON.stringify(coordDescentramientos)}, ${t_hc})`);
        
    });
}

 /**
    * Returns the sum of input numbers.
    * @customfunction
*/
function calcularFr() {


    // Leer los datos desde Excel
    const coordDescentramientos = leerDatosExcel();
    const t_hc = 3150; // Tensión del hilo conductor (ejemplo)

    // El código Python que vamos a ejecutar
    const pythonCode = `
    import numpy as np

    def Fr_Calculo_f(Coord_descentramientos, t_hc):
        """
        Calcula las fuerzas radiales a partir de las coordenadas con descentramientos
        y la tensión del hilo conductor.
        """

        Coord_descentramientos = np.array(Coord_descentramientos)
        dx = np.diff(Coord_descentramientos[:, 0])  # Diferencia en X
        dy = np.diff(Coord_descentramientos[:, 1])  # Diferencia en Y
        m = dy / dx  # Pendientes

        # Cálculo de los ángulos alfa
        dm = m[1:] - m[:-1]
        denom = 1 + m[1:] * m[:-1]
        delta_theta = np.arctan(dm / denom)
        alfa = np.pi - delta_theta

        # Calcular las fuerzas radiales
        Fr_hc_core = np.sqrt(2 * t_hc**2 + 2 * t_hc**2 * np.cos(alfa)) * np.sign(delta_theta)

        # Añadir ceros en los extremos (anclajes)
        Fr_hc = np.concatenate(([0], Fr_hc_core, [0]))

        return Fr_hc.reshape(-1, 1)
    `;

    // Ejecutar código Python en Pyodide
    

    // Mostrar el resultado en la consola
    console.log("Fuerzas Radiales:", result);
}