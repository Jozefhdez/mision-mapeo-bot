"""
Módulo de validación de iniciativas.
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class Validator:
    """Valida campos requeridos y formatos básicos de una iniciativa."""

    def validate(self, initiative_data: Dict) -> tuple[bool, List[str], List[Dict]]:
        """
        Valida una iniciativa.

        Returns:
            tuple: (is_valid, errors, duplicates)
            duplicates is always [] — deduplication is Bekaab's responsibility.
        """
        errors = []

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

        descripcion = initiative_data.get('descripcion', '')
        if len(descripcion) < 50:
            errors.append(f"Descripción muy corta ({len(descripcion)} chars, mínimo 50)")

        desc_enfoque = initiative_data.get('descripcion_enfoque', '')
        if len(desc_enfoque) < 200:
            errors.append(f"Descripción del enfoque muy corta ({len(desc_enfoque)} chars, mínimo 200)")

        etiquetas = initiative_data.get('etiquetas', [])
        if not isinstance(etiquetas, list) or len(etiquetas) < 3 or len(etiquetas) > 5:
            errors.append(f"Etiquetas deben ser entre 3 y 5 (encontradas: {len(etiquetas)})")

        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Validation failed: {errors}")

        return is_valid, errors, []
