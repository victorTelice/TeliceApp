/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */

/* global console, document, Excel, Office */

let pyodide;

async function initPyodide() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
  });
  console.log("✅ Pyodide listo");
}

Office.onReady(async (info) => {
  if (info.host === Office.HostType.Excel) {
    await initPyodide();
  }
});

