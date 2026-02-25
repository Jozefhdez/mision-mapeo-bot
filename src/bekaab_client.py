"""
Cliente para la API REST de Bekaab (WordPress + Code Snippet).
"""
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class BekaabClient:
    """Cliente para publicar iniciativas en Bekaab."""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Inicializa el cliente de Bekaab.
        
        Args:
            api_url: URL del endpoint de Bekaab
            api_key: API key para autenticación
        """
        self.api_url = api_url
        self.api_key = api_key
    
    def create_initiative(self, initiative_data: Dict) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Publica una iniciativa en Bekaab.
        
        Args:
            initiative_data: Datos de la iniciativa
            
        Returns:
            tuple: (success, post_id, error_message)
        """
        logger.info(f"Publishing initiative to Bekaab: {initiative_data.get('nombre')}")
        
        try:
            # Mapear datos al formato de Bekaab
            payload = self._map_to_bekaab_format(initiative_data)
            
            # Headers
            headers = {
                "Content-Type": "application/json",
                "X-API-KEY": self.api_key
            }
            
            # Request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                post_id = data.get('id')
                logger.info(f"Successfully published initiative - Post ID: {post_id}")
                return True, post_id, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Failed to publish initiative: {error_msg}")
                return False, None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Timeout al conectar con Bekaab"
            logger.error(error_msg)
            return False, None, error_msg
        
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(f"Unexpected error publishing to Bekaab: {e}")
            return False, None, error_msg
    
    def _map_to_bekaab_format(self, initiative_data: Dict) -> Dict:
        """
        Mapea los datos de Initiative al formato esperado por Bekaab.
        
        Args:
            initiative_data: Datos en formato Initiative
            
        Returns:
            Dict en formato Bekaab
        """
        # Mapear categoría a ID (esto debería venir de una tabla de mapeo)
        # Por ahora usamos un ID genérico
        categoria_id = self._get_categoria_id(initiative_data.get('categoria', ''))
        
        payload = {
            # Post base
            "titulo": initiative_data.get('nombre', ''),
            "contenido": initiative_data.get('descripcion', ''),
            
            # Clasificación
            "tipo_proyecto": initiative_data.get('tipo_proyecto', ''),
            "tipo_enfoque": initiative_data.get('tipo_enfoque', ''),
            "descripcion_enfoque": initiative_data.get('descripcion_enfoque', ''),
            "ods": initiative_data.get('ods', ''),
            
            # Características operativas
            "fuente_recursos": initiative_data.get('fuente_recursos', ''),
            "sector_economico": initiative_data.get('sector_economico', ''),
            "cobertura": initiative_data.get('cobertura', ''),
            "estatus_proyecto": initiative_data.get('estatus', ''),
            "tamano": initiative_data.get('tamano', ''),
            "institucion": initiative_data.get('institucion', ''),
            
            # Ubicación
            "direccion": initiative_data.get('ubicacion', ''),
            "ciudad": initiative_data.get('ciudad', ''),
            "estado": initiative_data.get('region', ''),
            "cp": initiative_data.get('codigo_postal', ''),
            
            # Contacto
            "email": initiative_data.get('email', ''),
            "facebook": initiative_data.get('facebook', ''),
            "web": initiative_data.get('sitio_web', ''),
            
            # Taxonomías
            "categorias": [categoria_id],
            "etiquetas": initiative_data.get('etiquetas', [])
        }
        
        # Remover valores None/vacíos para opcionales
        payload = {k: v for k, v in payload.items() if v}
        
        return payload
    
    def _get_categoria_id(self, categoria_nombre: str) -> int:
        """
        Mapea nombre de categoría a ID de GeoDirectory.
        
        TODO: Implementar mapeo completo desde DB o configuración.
        Por ahora retorna un ID genérico.
        """
        # Mapeo básico (expandir según la estructura real de Bekaab)
        categoria_map = {
            "Acción social": 160,
            "Acción en área natural": 161,
            "Educación y capacitación": 170,
            "Empresas": 180,
            "Instituciones": 190,
            "Productores": 200,
            "Tecnologías": 210,
            "Turismo y esparcimiento": 220,
        }
        
        return categoria_map.get(categoria_nombre, 162)  # 162 como default
