"""
Cliente para la API REST de Bekaab (WordPress + Code Snippet).
"""
import base64
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
    
    def authenticate(self, token: str) -> tuple[bool, Optional[Dict], Optional[str]]:
        """
        Valida un código de vinculación generado en bekaab.org/vincular-bot.

        Returns:
            tuple: (success, user_data, error_message)
            user_data contains: user_id, display_name, email
        """
        auth_url = self.api_url.replace('/crear-iniciativa', '/auth')
        try:
            response = requests.post(
                auth_url,
                json={'token': token.strip().upper()},
                headers={"Content-Type": "application/json", "X-API-KEY": self.api_key},
                timeout=15
            )
            if response.status_code == 200:
                return True, response.json(), None
            elif response.status_code == 401:
                return False, None, "Código inválido o expirado."
            else:
                return False, None, f"Error {response.status_code}: {response.text}"
        except requests.exceptions.Timeout:
            return False, None, "Timeout al conectar con Bekaab."
        except Exception as e:
            return False, None, str(e)

    def create_initiative(self, initiative_data: Dict, post_author: Optional[int] = None) -> tuple[bool, Optional[int], Optional[str], Optional[str]]:
        """
        Publica una iniciativa en Bekaab.
        
        Args:
            initiative_data: Datos de la iniciativa
            
        Returns:
            tuple: (success, post_id, error_message)
        """
        logger.info(f"Publishing initiative to Bekaab: {initiative_data.get('nombre')}")

        payload = self._map_to_bekaab_format(initiative_data)
        if post_author:
            payload['post_author'] = post_author

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.api_key
        }

        for attempt in range(2):  # 1 automatic retry on connection errors
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    post_id = data.get('id')
                    post_url = data.get('url')
                    logger.info(f"Successfully published initiative - Post ID: {post_id}")
                    return True, post_id, None, post_url
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"Failed to publish initiative: {error_msg}")
                    return False, None, error_msg, None

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                logger.warning(f"Publish attempt {attempt + 1} failed: {e}")
                if attempt == 1:
                    return False, None, f"No se pudo conectar con Bekaab tras 2 intentos: {str(e)}", None

        return False, None, "Error inesperado al publicar.", None
    
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
            "certificaciones": initiative_data.get('certificaciones', []),

            # Ubicación
            "direccion": initiative_data.get('ubicacion', ''),
            "ciudad": initiative_data.get('ciudad', ''),
            "estado": initiative_data.get('region', ''),
            "cp": initiative_data.get('codigo_postal', ''),
            "latitud": initiative_data.get('latitud', ''),
            "longitud": initiative_data.get('longitud', ''),

            # Contacto
            "email": initiative_data.get('email_contacto', '') or initiative_data.get('email', ''),
            "telefono": initiative_data.get('telefono', ''),
            "facebook": initiative_data.get('facebook', ''),
            "twitter": initiative_data.get('twitter', ''),
            "instagram": initiative_data.get('instagram', ''),
            "web": initiative_data.get('sitio_web', ''),

            # Metadata de registro
            "registrado_por": initiative_data.get('registrado_por', ''),
            "recomendado_por": initiative_data.get('recomendado_por', ''),
            "comentarios_registro": initiative_data.get('comentarios_registro', ''),

            # Taxonomías
            "categorias": [categoria_id],
            "etiquetas": initiative_data.get('etiquetas', []),
        }
        
        # Remover valores None/vacíos para opcionales
        payload = {k: v for k, v in payload.items() if v}
        
        return payload
    
    def _get_categoria_id(self, categoria_nombre: str) -> int:
        """Mapea nombre de subcategoría a ID de GeoDirectory en Bekaab."""
        categoria_map = {
            # Acción social
            "Acción en área natural": 162,
            "Acción en Casa": 158,
            "Acción en el trabajo": 160,
            "Acción en escuela": 159,
            "Acción en localidad": 161,
            "Otra acción": 163,
            # Educación y capacitación
            "Centro de investigación": 144,
            "Cursos o talleres": 145,
            "Educación básica": 189,
            "Educación media": 142,
            "Educación superior": 143,
            "Otra iniciativa educativa": 146,
            # Empresas
            "Agricultura o Jardinería": 164,
            "Alimentos o Bebidas": 165,
            "Aparatos Electrónicos": 166,
            "Artículos Desechables": 167,
            "Belleza o Cuidado": 168,
            "Bolsas": 169,
            "Certificadoras": 170,
            "Comercio, Finanzas e Inversión": 171,
            "Consultoría o Servicios": 172,
            "Decoración de Interiores": 173,
            "Emprendimiento": 186,
            "Hogar": 174,
            "Limpieza": 175,
            "Madera": 176,
            "Mascotas": 177,
            "Medios de Comunicación": 178,
            "Mercadotecnia o Publicidad": 179,
            "Niños y bebés": 180,
            "Otro producto o servicio": 187,
            "Papelería y oficina": 181,
            "Reciclaje o desechos": 182,
            "Ropa y accesorios": 183,
            "Salud": 184,
            "Servicios y artículos funerarios": 185,
            # Instituciones
            "Centro de acopio": 156,
            "Organizacion gubernamental": 153,
            "Organización internacional": 155,
            "Organización No Gubernamental": 154,
            "Otra institución": 157,
            # Productores
            "Agricultura o ganadería": 128,
            "Apicultura": 129,
            "Aprovechamiento forestal": 131,
            "Artesanía": 132,
            "Caza, pesca o recolección": 130,
            "Otra producción": 133,
            # Puntos de intercambio
            "Centro comercial": 125,
            "Otro punto de intercambio": 127,
            "Tianguis o mercado": 126,
            "Tienda": 188,
            # Tecnologías
            "Agua": 134,
            "Aire": 136,
            "Arquitectura o Construcción": 139,
            "Energía": 137,
            "Otra tecnologia": 140,
            "Suelo": 135,
            "Transporte": 138,
            # Turismo y esparcimiento
            "Balneario": 147,
            "Hotel": 148,
            "Otro turismo": 152,
            "Parque": 150,
            "Restaurante": 149,
            "Transporte (servicio)": 151,
        }

        return categoria_map.get(categoria_nombre, 162)

    def upload_images(self, post_id: int, telegram_file_ids: list, bot_token: str) -> tuple[int, list]:
        """
        Descarga imágenes de Telegram y las sube a Bekaab vía endpoint personalizado.

        Returns:
            tuple: (success_count, errors)
        """
        if not telegram_file_ids:
            return 0, []

        upload_url = self.api_url.replace('/crear-iniciativa', '/subir-imagen')
        headers = {"Content-Type": "application/json", "X-API-KEY": self.api_key}
        success_count = 0
        errors = []

        for i, file_id in enumerate(telegram_file_ids):
            try:
                # 1. Obtener ruta del archivo en Telegram
                tg_resp = requests.get(
                    f"https://api.telegram.org/bot{bot_token}/getFile",
                    params={"file_id": file_id},
                    timeout=15
                )
                tg_resp.raise_for_status()
                file_path = tg_resp.json()['result']['file_path']

                # 2. Descargar archivo de Telegram
                file_resp = requests.get(
                    f"https://api.telegram.org/file/bot{bot_token}/{file_path}",
                    timeout=30
                )
                file_resp.raise_for_status()

                # 3. Codificar en base64 y subir a Bekaab
                ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else 'jpg'
                filename = f"iniciativa_{post_id}_{i + 1}.{ext}"
                image_b64 = base64.b64encode(file_resp.content).decode('utf-8')

                resp = requests.post(
                    upload_url,
                    json={
                        "post_id": post_id,
                        "imagen_base64": image_b64,
                        "filename": filename,
                        "is_featured": i == 0,
                    },
                    headers=headers,
                    timeout=30
                )
                resp.raise_for_status()
                media_id = resp.json().get('media_id')
                success_count += 1
                logger.info(f"Uploaded image {i + 1}/{len(telegram_file_ids)} - Media ID: {media_id}")

            except Exception as e:
                errors.append(f"Imagen {i + 1}: {str(e)}")
                logger.error(f"Failed to upload image {file_id}: {e}")

        return success_count, errors
