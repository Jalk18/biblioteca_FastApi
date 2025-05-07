import json
from typing import Optional, Type, TypeVar, Generic, List, Dict, Any
from pathlib import Path
from models import Autor, Libro, Prestamo

T = TypeVar('T', Autor, Libro, Prestamo)

class GestorArchivos(Generic[T]):
    def __init__(self, model_class: Type[T], filename: str):
        self.model_class = model_class
        self.filename = filename
        Path(filename).touch(exist_ok=True)  
        
    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
            
    def _write_data(self, data: List[Dict[str, Any]]):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, default=str)  
    
    
    def get_all(self) -> List[T]:
        data = self._read_data()
        return [self.model_class(**item) for item in data]
    
    def get_by_id(self, id: int) -> Optional[T]:
        data = self._read_data()
        for item in data:
            if item['id'] == id:
                return self.model_class(**item)
        return None
    
    def add(self, objeto: T) -> T:
        data = self._read_data()
        data.append(objeto.dict())
        self._write_data(data)
        return objeto
    
    def update(self, id: int, datos: Dict[str, Any]) -> Optional[T]:
        data = self._read_data()
        updated = False
        
        for item in data:
            if item['id'] == id:
                item.update(datos)
                updated = True
                break
                
        if updated:
            self._write_data(data)
            return self.get_by_id(id)
        return None
    
    def delete(self, id: int) -> bool:
        data = self._read_data()
        initial_length = len(data)
        data = [item for item in data if item['id'] != id]
        
        if len(data) < initial_length:
            self._write_data(data)
            return True
        return False