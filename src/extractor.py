"""
Módulo de extracción de información con LLM Ollama.
"""
import requests
import json
import logging
import time
from typing import Dict, Optional
from src.models import Initiative

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extractor de iniciativas usando Ollama local."""
    
    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llama3.1:8b"):
        """
        Inicializa el extractor LLM.
        
        Args:
            base_url: URL del servidor Ollama
            model: Nombre del modelo a usar
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.endpoint = f"{self.base_url}/api/generate"
    
    def extract(self, scraped_data: Dict[str, str], max_retries: int = 1) -> tuple[Optional[Dict], Dict]:
        """
        Extrae información estructurada del contenido scrapeado.
        
        Args:
            scraped_data: Datos del scraper (title, content, etc)
            max_retries: Número máximo de reintentos
            
        Returns:
            tuple: (initiative_data, log_data)
        """
        logger.info(f"Extracting initiative data using {self.model}")
        
        # Construir prompt
        prompt = self._build_prompt(scraped_data)
        
        # Intentar extracción
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Llamada a Ollama
                response = self._call_ollama(prompt)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Parse JSON response
                initiative_data = self._parse_response(response['response'])
                
                # Log exitoso
                log_data = {
                    'provider': 'local',
                    'model_name': self.model,
                    'prompt_tokens': response.get('prompt_eval_count', 0),
                    'completion_tokens': response.get('eval_count', 0),
                    'total_tokens': response.get('prompt_eval_count', 0) + response.get('eval_count', 0),
                    'cost_usd': 0.0,
                    'duration_ms': duration_ms,
                    'success': True,
                    'raw_response': json.dumps(response, ensure_ascii=False)
                }
                
                logger.info(f"Successfully extracted initiative in {duration_ms}ms")
                return initiative_data, log_data
                
            except Exception as e:
                logger.warning(f"Extraction attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries:
                    # Log de fallo
                    log_data = {
                        'provider': 'local',
                        'model_name': self.model,
                        'success': False,
                        'error_message': str(e),
                        'duration_ms': 0
                    }
                    return None, log_data
                
                time.sleep(2)  # Esperar antes de reintentar
        
        return None, {}
    
    def _build_prompt(self, scraped_data: Dict[str, str]) -> str:
        """Construye el prompt para el LLM."""
        
        # Truncar contenido si es muy largo (~6000 tokens)
        content = scraped_data.get('content', '')[:24000]  # ~6k tokens aprox
        
        prompt = f"""Eres un asistente experto en análisis de iniciativas socioambientales. 

Tu tarea es extraer información estructurada de una página web sobre una iniciativa.

DATOS DE LA PÁGINA:
Título: {scraped_data.get('title', 'N/A')}
Descripción: {scraped_data.get('description', 'N/A')}
URL: {scraped_data.get('url', 'N/A')}

CONTENIDO:
{content}

INSTRUCCIONES:
Extrae TODA la información disponible y devuelve un JSON con la siguiente estructura EXACTA:

{{
  "nombre": "Nombre de la iniciativa",
  "descripcion": "Descripción detallada (mínimo 50 caracteres)",
  "categoria": "Una de: Acción social, Educación y capacitación, Empresas, Instituciones, Productores, Puntos de intercambio, Tecnologías, Turismo y esparcimiento",
  "etiquetas": ["palabra1", "palabra2", "palabra3"],
  "tipo_proyecto": "Uno de: En el Hogar, En el Trabajo, Sin Fines de Lucro, Empresarial, Institución u Organización",
  "tipo_enfoque": "Uno de: Social, Ambiental, Sustentable, Regenerativo, Economía Circular",
  "descripcion_enfoque": "Explicación detallada de por qué tiene este enfoque (mínimo 200 caracteres)",
  "ods": "Objetivo(s) de Desarrollo Sostenible, ej: '15: Vida en tierra'",
  "fuente_recursos": "Uno de: Particular, Privada, Pública, Mixta",
  "sector_economico": "Uno de: Agropecuario, Industrial, De infraestructura pública, De infraestructura económica, De servicios, No aplica",
  "cobertura": "Uno de: Local, Regional, Nacional, Multinacional, Global",
  "estatus": "Uno de: Idea, En diseño o construcción, Reciente, Consolidado, Completado",
  "tamano": "Uno de: De 1 a 2 colaboradores, De 3 a 10 colaboradores, De 11 a 50 colaboradores, De 51 a 100 colaboradores, De 101 a 500 colaboradores, Más de 500 colaboradores",
  "ubicacion": "Dirección completa si está disponible",
  "pais": "País (preferir 'Mexico' si es de México)",
  "region": "Estado o región",
  "ciudad": "Ciudad",
  "codigo_postal": "CP si está disponible o null",
  "telefono": "Teléfono si está disponible o null",
  "email": "Email si está disponible o null",
  "sitio_web": "URL del sitio web o null",
  "facebook": "URL de Facebook o null",
  "twitter": "URL de Twitter/X o null",
  "instagram": "URL de Instagram o null",
  "institucion": "Nombre de institución relacionada o null"
}}

REGLAS IMPORTANTES:
1. Devuelve SOLO el JSON, sin texto adicional
2. Si no encuentras un dato, usa null para opcionales o infiere razonablemente
3. Las etiquetas deben ser 3-5 palabras clave en minúsculas
4. La descripción debe ser detallada (mínimo 50 caracteres)
5. La descripción del enfoque debe justificar por qué la iniciativa corresponde a ese enfoque (mínimo 200 caracteres)

JSON:"""
        
        return prompt
    
    def _call_ollama(self, prompt: str, timeout: int = 120) -> Dict:
        """Llama al API de Ollama."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9
            }
        }
        
        response = requests.post(
            self.endpoint,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        
        return response.json()
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse la respuesta del LLM y extrae el JSON."""
        # Intentar encontrar JSON en la respuesta
        response_text = response_text.strip()
        
        # Buscar inicio y fin de JSON
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        
        if start == -1 or end == 0:
            raise ValueError("No se encontró JSON en la respuesta")
        
        json_text = response_text[start:end]
        
        try:
            data = json.loads(json_text)
            
            # Validar con Pydantic
            initiative = Initiative(**data)
            
            return initiative.model_dump()
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            raise ValueError(f"JSON inválido: {e}")
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            raise ValueError(f"Datos inválidos: {e}")
