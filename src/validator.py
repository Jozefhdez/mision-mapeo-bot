"""
Módulo de validación de iniciativas.
"""
import logging
from typing import List, Dict
from fuzzywuzzy import fuzz
from src.database import Database

logger = logging.getLogger(__name__)


class Validator:
    """Validador de iniciativas con detección de duplicados."""
    
    def __init__(self, db: Database, similarity_threshold: int = 85):
        """
        Inicializa el validador.
        
        Args:
            db: Instancia de Database
            similarity_threshold: Umbral de similaridad para duplicados (0-100)
        """
        self.db = db
        self.similarity_threshold = similarity_threshold
    
    def validate(self, initiative_data: Dict) -> tuple[bool, List[str], List[Dict]]:
        """
        Valida una iniciativa y busca duplicados.
        
        Args:
            initiative_data: Datos de la iniciativa
            
        Returns:
            tuple: (is_valid, errors, duplicates)
        """
        errors = []
        duplicates = []
        
        # 1. Validar campos requeridos
        required_fields = [
            'nombre', 'descripcion', 'categoria', 'etiquetas',
            'tipo_proyecto', 'tipo_enfoque', 'descripcion_enfoque', 'ods',
            'fuente_recursos', 'sector_economico', 'cobertura', 'estatus', 'tamano',
            'ubicacion', 'pais', 'region', 'ciudad'
        ]
        
        for field in required_fields:
            value = initiative_data.get(field)
            if value is None or value == '' or (isinstance(value, list) and len(value) == 0):
                errors.append(f"Campo requerido faltante: {field}")
        
        # 2. Validar longitud de descripción
        descripcion = initiative_data.get('descripcion', '')
        if len(descripcion) < 50:
            errors.append(f"Descripción muy corta ({len(descripcion)} chars, mínimo 50)")
        
        # 3. Validar longitud de descripción del enfoque
        desc_enfoque = initiative_data.get('descripcion_enfoque', '')
        if len(desc_enfoque) < 200:
            errors.append(f"Descripción del enfoque muy corta ({len(desc_enfoque)} chars, mínimo 200)")
        
        # 4. Validar etiquetas (3-5)
        etiquetas = initiative_data.get('etiquetas', [])
        if not isinstance(etiquetas, list) or len(etiquetas) < 3 or len(etiquetas) > 5:
            errors.append(f"Etiquetas deben ser entre 3 y 5 (encontradas: {len(etiquetas)})")
        
        # 5. Buscar duplicados
        if initiative_data.get('nombre') and initiative_data.get('ciudad'):
            duplicates = self._find_duplicates(
                initiative_data['nombre'],
                initiative_data['ciudad']
            )
        
        is_valid = len(errors) == 0
        
        if duplicates:
            logger.warning(f"Found {len(duplicates)} potential duplicates")
        
        if not is_valid:
            logger.warning(f"Validation failed with {len(errors)} errors")
        
        return is_valid, errors, duplicates
    
    def _find_duplicates(self, name: str, city: str) -> List[Dict]:
        """
        Busca iniciativas duplicadas usando fuzzy matching.
        
        Args:
            name: Nombre de la iniciativa
            city: Ciudad
            
        Returns:
            Lista de posibles duplicados con score de similaridad
        """
        # Buscar candidatos en DB
        candidates = self.db.search_duplicates(name, city)
        
        duplicates = []
        
        for candidate in candidates:
            # Validar que el candidato tenga los campos necesarios
            if not candidate.get('nombre') or not candidate.get('ciudad'):
                continue
            
            # Calcular similaridad del nombre
            name_similarity = fuzz.ratio(
                name.lower(),
                candidate['nombre'].lower()
            )
            
            # Calcular similaridad de ciudad
            city_similarity = fuzz.ratio(
                city.lower(),
                candidate['ciudad'].lower()
            )
            
            # Promedio ponderado (nombre tiene más peso)
            overall_similarity = (name_similarity * 0.7) + (city_similarity * 0.3)
            
            if overall_similarity >= self.similarity_threshold:
                duplicates.append({
                    'id': candidate['id'],
                    'nombre': candidate['nombre'],
                    'ciudad': candidate['ciudad'],
                    'similarity': round(overall_similarity, 1)
                })
        
        # Ordenar por similaridad
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
        return duplicates
