from fastapi import FastAPI, HTTPException, status
from models import Autor, Libro, Prestamo
from gestor_archivos import GestorArchivos
from typing import List
from datetime import date

app = FastAPI(title="API de Biblioteca")

# Inicializar gestores de archivos
gestor_autores = GestorArchivos(Autor, "autores.json")
gestor_libros = GestorArchivos(Libro, "libros.json")
gestor_prestamos = GestorArchivos(Prestamo, "prestamos.json")

# Endpoints para Autores
@app.get("/autores", response_model=List[Autor], tags=["Autores"])
def listar_autores():
    return gestor_autores.get_all()

@app.get("/autores/{id}", response_model=Autor, tags=["Autores"])
def obtener_autor(id: int):
    autor = gestor_autores.get_by_id(id)
    if autor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )
    return autor

@app.post("/autores", response_model=Autor, status_code=status.HTTP_201_CREATED, tags=["Autores"])
def crear_autor(autor: Autor):
    if gestor_autores.get_by_id(autor.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de autor ya existe"
        )
    return gestor_autores.add(autor)

@app.put("/autores/{id}", response_model=Autor, tags=["Autores"])
def actualizar_autor(id: int, autor: Autor):
    if id != autor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID en URL no coincide con ID en cuerpo"
        )
    resultado = gestor_autores.update(id, autor.dict())
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )
    return resultado

@app.delete("/autores/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Autores"])
def eliminar_autor(id: int):
    # Verificar si el autor tiene libros asociados
    libros = gestor_libros.get_all()
    if any(libro.autor_id == id for libro in libros):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar autor con libros asociados"
        )
    
    if not gestor_autores.delete(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Autor no encontrado"
        )

# Endpoints para Libros
@app.get("/libros", response_model=List[Libro], tags=["Libros"])
def listar_libros(publicado: bool = None):
    libros = gestor_libros.get_all()
    if publicado is not None:
        libros = [libro for libro in libros if libro.publicado == publicado]
    return libros

@app.get("/libros/{id}", response_model=Libro, tags=["Libros"])
def obtener_libro(id: int):
    libro = gestor_libros.get_by_id(id)
    if libro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    return libro

@app.post("/libros", response_model=Libro, status_code=status.HTTP_201_CREATED, tags=["Libros"])
def crear_libro(libro: Libro):
    # Verificar que el autor existe
    if gestor_autores.get_by_id(libro.autor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El autor especificado no existe"
        )
    
    if gestor_libros.get_by_id(libro.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de libro ya existe"
        )
    return gestor_libros.add(libro)

@app.put("/libros/{id}", response_model=Libro, tags=["Libros"])
def actualizar_libro(id: int, libro: Libro):
    if id != libro.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID en URL no coincide con ID en cuerpo"
        )
    
    # Verificar que el autor existe
    if gestor_autores.get_by_id(libro.autor_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El autor especificado no existe"
        )
    
    resultado = gestor_libros.update(id, libro.dict())
    if resultado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )
    return resultado

@app.delete("/libros/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Libros"])
def eliminar_libro(id: int):
    # Verificar si el libro está prestado
    prestamos = gestor_prestamos.get_all()
    if any(prestamo.libro_id == id and not prestamo.devuelto for prestamo in prestamos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar libro con préstamos activos"
        )
    
    if not gestor_libros.delete(id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado"
        )

# Endpoints para Préstamos
@app.get("/prestamos", response_model=List[Prestamo], tags=["Prestamos"])
def listar_prestamos(devuelto: bool = None):
    prestamos = gestor_prestamos.get_all()
    if devuelto is not None:
        prestamos = [p for p in prestamos if p.devuelto == devuelto]
    return prestamos

@app.get("/prestamos/{id}", response_model=Prestamo, tags=["Prestamos"])
def obtener_prestamo(id: int):
    prestamo = gestor_prestamos.get_by_id(id)
    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    return prestamo

@app.post("/prestamos", response_model=Prestamo, status_code=status.HTTP_201_CREATED, tags=["Prestamos"])
def crear_prestamo(prestamo: Prestamo):
    # Verificar que el libro existe
    if gestor_libros.get_by_id(prestamo.libro_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro especificado no existe"
        )
    
    # Verificar que el libro no está ya prestado
    prestamos_activos = gestor_prestamos.get_all()
    if any(p.libro_id == prestamo.libro_id and not p.devuelto for p in prestamos_activos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El libro ya está prestado"
        )
    
    if gestor_prestamos.get_by_id(prestamo.id) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de préstamo ya existe"
        )
    return gestor_prestamos.add(prestamo)

@app.put("/prestamos/{id}/devolver", response_model=Prestamo, tags=["Prestamos"])
def devolver_prestamo(id: int):
    prestamo = gestor_prestamos.get_by_id(id)
    if prestamo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado"
        )
    
    if prestamo.devuelto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El préstamo ya estaba marcado como devuelto"
        )
    
    datos_actualizados = {
        "devuelto": True,
        "fecha_devolucion": date.today().isoformat()
    }
    
    resultado = gestor_prestamos.update(id, datos_actualizados)
    return resultado