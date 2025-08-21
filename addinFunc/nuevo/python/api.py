from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/calculochorra/")
def calculo_chorra(pk_km: float = Query(...), vanos_m: float = Query(...)):
    if vanos_m == 0:
        return {"error": "No se puede dividir por cero"}
    resultado = pk_km / vanos_m
    return {"resultado": resultado}

@app.get("/ping")
def ping():
    return {"status": "ok"}