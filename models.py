from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Autor(BaseModel):
    id: int
    nombre: str
    nacionalidad: str
    fecha_nacimiento: date

class Libro(BaseModel):
    id: int
    titulo: str
    autor_id: int
    genero: str
    isbn: str
    publicado: bool = True

class Prestamo(BaseModel):
    id: int
    libro_id: int
    usuario: str  # Podría ser un ID si tuviéramos modelo Usuario
    fecha_prestamo: date
    fecha_devolucion: Optional[date] = None
    devuelto: bool = False