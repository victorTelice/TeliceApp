from pydantic import BaseModel
from typing import  Literal


###Archivo con los modelos pydantic para la entrada de datos
##TODOS LOS NUMEROS ESTAN PUESTOS EN FLOAT PORQUE NO ESTOY SEGURO SI PUEDEN SER INT --> HABRIA QUE ASEGURARSE CUALES TIENEN QUE SER INT Y CUALES FLOAT

##clase para datos_via, se obtienen del fichero .via
class Via(BaseModel):
    ancho_via: float
    ancho_carril: float

##clase para datos_conductores, se obtienen del fichero .cnd
class Conductores(BaseModel):
    s_hc: float
    t_hc: float
    ro_hc: float
    s_hs: float
    t_hs: float
    ro_hs: float
    tipo_pendolado: str
    n_hhcc: int

##clase para la tabla de tramos de trazado, se obtiene del fichero .tar
class Datos_Tabla_Tramos(BaseModel):
    tipo_tramo: Literal['Recta','Clotoide (Recta-Círculo)','Círculo','Clotoide (Círculo-Recta)','Clotoide (R1>R2)', 'Clotoide (R2>1)']
    pk_i: float
    pk_f: float
    parametro_radio: float
    giro: Literal['Izquierda','Derecha']
    peralte_tramo: float

##clase para la tabla de vanos de seccionamiento, se obtiene del fichero .secc
class Datos_Tabla_Vanos(BaseModel):
    poste: str
    tipo_mensula: Literal['Anclaje', 'Elevación', 'Vía General']
    pk_km: float
    vanos_m: float | None
    descentramiento_cm: float #he visto enteros pero por si acaso en otro ejemplo que no sea monf-lugo usan floats
    altura_hhcc_mm: float #he visto enteros pero por si acaso en otro ejemplo que no sea monf-lugo usan floats

##clase para la tabla de datos topografia, se coge del excel en mensulas, se obtiene del excel
class Tabla_Datos_Topografía(BaseModel):
    n_perfil: str
    tipo_de_poste: str
    tipologia: Literal['Anclaje', 'Elevación', 'Vía General']
    lado_poste: Literal['Derecha', 'Izquierda']
    giros_de_mensula: str
    desc_mm: float
    alt_hc_mm: float
    tipo_de_catenaria: float
    tipo_de_mensula: str
    galibo_mm: float
    ht_mm: float
    peralte_mm: float
    altura_gm_mm: float
    distancia_entre_giros_mm: float
    desplome_mm_m: float
    tipo_de_brazo: str
    posicion_brazo_supsa_mm: float
    angulo_brazo: float
