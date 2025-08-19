from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional
import numpy as np

class DatoVano(BaseModel):
    poste: Optional[str]
    tipo_mensula: Optional[str]
    pk_km: Optional[float]
    vanos_m: Optional[int]
    descentramiento_cm: Optional[int]
    altura_hhcc_cm: Optional[int]

    @validator('*', pre=True)
    def flatten_arrays(cls, v):
        # En tu datos algunos valores son arrays numpy, aquí los aplano:
        if isinstance(v, np.ndarray):
            if v.size == 0:
                return None
            if v.size == 1:
                return v.item()
            else:
                return v.tolist()
        return v