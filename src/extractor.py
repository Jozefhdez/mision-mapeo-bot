"""
Módulo de extracción de información con LLM via OpenRouter.
"""
import requests
import json
import logging
import time
from typing import Dict, Optional
from src.models import Initiative

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extractor de iniciativas usando OpenRouter API con Gemini."""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash-lite"):
        """
        Inicializa el extractor LLM.
        
        Args:
            api_key: API key de OpenRouter
            model: Nombre del modelo a usar
        """
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        
        # Precios por 1M tokens (Gemini 2.5 Flash Lite via OpenRouter)
        self.input_price = 0.10  # $0.10 per 1M tokens
        self.output_price = 0.40  # $0.40 per 1M tokens
    
    def extract(self, urls: list, max_retries: int = 1) -> tuple[Optional[Dict], Dict]:
        """
        Extrae información estructurada de una o más URLs de la misma iniciativa.

        Args:
            urls: URL o lista de URLs de la iniciativa a analizar
            max_retries: Número máximo de reintentos

        Returns:
            tuple: (initiative_data, log_data)
        """
        if isinstance(urls, str):
            urls = [urls]

        logger.info(f"Extracting initiative data from {len(urls)} URL(s) using {self.model}")

        # Construir prompt con URL(s)
        prompt = self._build_prompt(urls)
        
        # Intentar extracción
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                
                # Llamada a OpenRouter
                response = self._call_openrouter(prompt)
                
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Parse JSON response
                content = response['choices'][0]['message']['content']
                initiative_data = self._parse_response(content)
                
                # Calcular costo
                usage = response.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = prompt_tokens + completion_tokens
                
                cost_usd = (
                    (prompt_tokens / 1_000_000 * self.input_price) +
                    (completion_tokens / 1_000_000 * self.output_price)
                )
                
                # Log exitoso
                log_data = {
                    'provider': 'openrouter',
                    'model_name': self.model,
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens,
                    'cost_usd': round(cost_usd, 6),
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
                        'provider': 'openrouter',
                        'model_name': self.model,
                        'success': False,
                        'error_message': str(e),
                        'duration_ms': 0
                    }
                    return None, log_data
                
                time.sleep(2)  # Esperar antes de reintentar
        
        return None, {}
    
    def _build_prompt(self, urls: list) -> str:
        """Construye el prompt para el LLM."""

        if len(urls) == 1:
            urls_section = f"URL: {urls[0]}"
            source_instruction = "Tu tarea es visitar la siguiente URL y extraer información estructurada sobre la iniciativa:"
            access_instruction = "Por favor, accede a esta URL, analiza todo el contenido de la página y extrae la información disponible"
        else:
            urls_lines = "\n".join(f"URL {i + 1}: {url}" for i, url in enumerate(urls))
            urls_section = urls_lines
            source_instruction = (
                f"Tu tarea es visitar las siguientes {len(urls)} URLs, que corresponden todas a la misma iniciativa socioambiental, "
                f"y combinar la información de todas las fuentes para generar una extracción más completa y precisa:"
            )
            access_instruction = (
                "Por favor, accede a cada una de estas URLs, analiza todo el contenido disponible en cada página "
                "y sintetiza la información combinada. Si hay datos contradictorios entre fuentes, prioriza la información más detallada"
            )

        prompt = f"""Eres un asistente experto en análisis de iniciativas socioambientales.

{source_instruction}

{urls_section}

{access_instruction}

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
        1. Devuelve SOLO el JSON válido, sin texto adicional antes o después
        2. CAMPOS CRÍTICOS (intenta siempre extraer o inferir razonablemente):
           - nombre, descripcion, categoria, tipo_proyecto, tipo_enfoque, descripcion_enfoque
           - Si no hay ubicación exacta, infiere de pistas (ej: dominio .mx = Mexico, menciones de ciudades)
        3. CAMPOS OPCIONALES (usa null si no encuentras):
           - ubicacion, codigo_postal, telefono, email, redes sociales
        4. Para región y ciudad: Si no las encuentras explícitas pero hay pistas (dominio, texto), infiere razonablemente
        5. Las etiquetas deben ser 3-5 palabras clave en minúsculas relacionadas con la iniciativa
        6. La descripción debe ser detallada (mínimo 50 caracteres) - extrae del contenido principal
        7. La descripción del enfoque debe justificar por qué tiene ese enfoque (mínimo 200 caracteres)
        8. Si el sitio menciona México/ciudades mexicanas, usa "Mexico" como país

        JSON:"""
        
        return prompt
    
    def _call_openrouter(self, prompt: str, timeout: int = 60) -> Dict:
        """Llama al API de OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://misionmapeo.org",  # Opcional: para aparecer en leaderboards
            "X-Title": "Mision Mapeo Bot"  # Opcional
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "top_p": 0.9,
            "max_tokens": 2048
        }
        
        response = requests.post(
            self.endpoint,
            headers=headers,
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
            
            # Intentar validar con Pydantic
            try:
                initiative = Initiative(**data)
                validated_data = initiative.model_dump()
                validated_data['_validation_passed'] = True
                validated_data['_missing_fields'] = []
                return validated_data
            except Exception as validation_error:
                # Si falla validación, devolver datos con info de campos faltantes
                logger.warning(f"Partial validation failure: {validation_error}")
                data['_validation_passed'] = False
                data['_missing_fields'] = self._extract_missing_fields(validation_error)
                data['_validation_error'] = str(validation_error)
                return data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            raise ValueError(f"JSON inválido: {e}")
    
    def _extract_missing_fields(self, error) -> list:
        """Extrae nombres de campos faltantes del error de validación."""
        import re
        error_str = str(error)
        
        # Buscar patrones como "Field required [type=missing, input_value=..."
        missing = []
        for line in error_str.split('\n'):
            if 'Field required' in line or 'field required' in line:
                # Intentar extraer nombre del campo
                match = re.search(r"'(\w+)'|(\w+)\s*\n", line)
                if match:
                    field_name = match.group(1) or match.group(2)
                    if field_name and field_name not in missing:
                        missing.append(field_name)
        
        # Si no encontramos ninguno con regex, intentar con el error directo
        if not missing and hasattr(error, 'errors'):
            for err in error.errors():
                if err.get('type') == 'missing':
                    field = err.get('loc', [])[-1] if err.get('loc') else None
                    if field and field not in missing:
                        missing.append(field)
        
        return missing
