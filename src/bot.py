"""
Bot de Telegram para registro asistido de iniciativas.
"""
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from urllib.parse import urlparse

from src.scraper import Scraper
from src.extractor import LLMExtractor
from src.validator import Validator
from src.bekaab_client import BekaabClient
from src.database import Database

logger = logging.getLogger(__name__)


class InitiativeBot:
    """Bot de Telegram para procesar iniciativas."""
    
    def __init__(
        self,
        token: str,
        allowed_user_ids: list[int],
        db: Database,
        scraper: Scraper,
        extractor: LLMExtractor,
        validator: Validator,
        bekaab_client: BekaabClient
    ):
        """Inicializa el bot."""
        self.token = token
        self.allowed_user_ids = allowed_user_ids
        self.db = db
        self.scraper = scraper
        self.extractor = extractor
        self.validator = validator
        self.bekaab_client = bekaab_client
        
        # Storage temporal para contexto (en producción usar Redis o similar)
        self.pending_initiatives = {}
    
    def run(self):
        """Inicia el bot."""
        application = Application.builder().token(self.token).build()
        
        # Handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Bot started - polling for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler del comando /start."""
        user_id = update.effective_user.id
        
        if user_id not in self.allowed_user_ids:
            await update.message.reply_text("❌ No autorizado.")
            return
        
        await update.message.reply_text(
            "¡Hola! Soy el bot de Misión Mapeo.\n\n"
            "Envíame la URL de una iniciativa y la procesaré automáticamente.\n\n"
            "El proceso:\n"
            "1. Extraigo el contenido de la página\n"
            "2. Analizo con IA la información\n"
            "3. Te muestro un preview para confirmar\n"
            "4. Publico en Bekaab si apruebas\n\n"
            "¡Envía una URL para empezar!"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de mensajes de texto."""
        user_id = update.effective_user.id
        
        # Verificar autorización
        if user_id not in self.allowed_user_ids:
            await update.message.reply_text("❌ No autorizado.")
            return
        
        text = update.message.text
                # Verificar si el usuario está en modo edición
        if context.user_data.get('editing_mode'):
            await self._process_field_answer(update, context, text)
            return
                # Verificar si es una URL
        if not self._is_valid_url(text):
            await update.message.reply_text(
                "Por favor envía una URL válida."
            )
            return
        
        # Procesar URL
        await self._process_url(update, context, text)
    
    async def _process_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """Procesa una URL completa end-to-end."""
        chat_id = update.effective_chat.id
        
        # 1. Notificar inicio
        status_msg = await update.message.reply_text("Procesando iniciativa...")
        
        try:
            # 2. Crear registro de source en DB
            domain = urlparse(url).netloc
            source_id = self.db.create_source(url, domain)
            
            # 3. Extracción directa con IA (Gemini accede a la URL)
            await status_msg.edit_text("Analizando página con IA")
            initiative_data, log_data = self.extractor.extract(url)
            
            if not initiative_data:
                error_msg = log_data.get('error_message', 'Error desconocido')
                await status_msg.edit_text(f"Error en extracción: {error_msg}")
                self.db.update_source_status(source_id, 'failed', error_msg)
                return
            
            # Guardar log
            log_data['source_id'] = source_id
            self.db.create_extraction_log(log_data)
            
            # Actualizar status en DB
            self.db.update_source_status(source_id, 'extracted')
            
            # Agregar source_url
            initiative_data['source_url'] = url
            
            # Verificar si hay campos faltantes (validación de Pydantic)
            validation_passed = initiative_data.pop('_validation_passed', True)
            missing_fields = initiative_data.pop('_missing_fields', [])
            validation_error = initiative_data.pop('_validation_error', None)
            
            if not validation_passed and len(missing_fields) > 0:
                # Guardar datos parciales
                initiative_id = self.db.create_initiative(initiative_data, url)
                self.pending_initiatives[initiative_id] = initiative_data
                
                # Mostrar preview con campos faltantes
                await status_msg.delete()
                await self._send_incomplete_preview(
                    update, context, initiative_id, initiative_data, missing_fields
                )
                return
            
            # 4. Validación
            await status_msg.edit_text("Validando datos...")
            is_valid, errors, duplicates = self.validator.validate(initiative_data)
            
            if not is_valid:
                # Extraer campos faltantes de los errores
                missing_from_errors = []
                for error in errors:
                    if error.startswith("Campo requerido faltante: "):
                        field = error.replace("Campo requerido faltante: ", "")
                        missing_from_errors.append(field)
                
                # Si hay campos faltantes, mostrar interfaz de completar
                if missing_from_errors:
                    initiative_id = self.db.create_initiative(initiative_data, url)
                    self.pending_initiatives[initiative_id] = initiative_data
                    
                    await status_msg.delete()
                    await self._send_incomplete_preview(
                        update, context, initiative_id, initiative_data, missing_from_errors
                    )
                    return
                
                # Si son otros errores, mostrar mensaje simple
                error_text = "Errores de validación:\n\n" + "\n".join(f"• {e}" for e in errors)
                await status_msg.edit_text(error_text)
                return
            
            # 5. Guardar en DB como pending
            initiative_id = self.db.create_initiative(initiative_data, url)
            
            # Guardar en contexto temporal
            self.pending_initiatives[initiative_id] = initiative_data
            
            # 6. Mostrar preview
            await status_msg.delete()
            await self._send_preview(update, context, initiative_id, initiative_data, duplicates)
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            await status_msg.edit_text(f"Error inesperado: {str(e)}")
    
    async def _send_preview(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        initiative_id: int,
        data: dict,
        duplicates: list
    ):
        """Envía preview formateado con botones de confirmación."""
        
        # Construir mensaje
        preview_text = self._format_preview(data, duplicates)
        
        # Botones
        keyboard = [
            [
                InlineKeyboardButton("Confirmar y Publicar", callback_data=f"confirm_{initiative_id}"),
                InlineKeyboardButton("Rechazar", callback_data=f"reject_{initiative_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            preview_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def _send_incomplete_preview(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        initiative_id: int,
        data: dict,
        missing_fields: list
    ):
        """Envía preview de datos incompletos con instrucciones para completar."""
        
        # Mapeo de campos a nombres legibles en español
        field_names = {
            'nombre': 'Nombre de la iniciativa',
            'descripcion': 'Descripción',
            'categoria': 'Categoría',
            'etiquetas': 'Etiquetas',
            'tipo_proyecto': 'Tipo de Proyecto',
            'tipo_enfoque': 'Tipo de Enfoque',
            'descripcion_enfoque': 'Descripción del Enfoque',
            'ods': 'ODS (Objetivos de Desarrollo Sostenible)',
            'fuente_recursos': 'Fuente de Recursos',
            'sector_economico': 'Sector Económico',
            'cobertura': 'Cobertura',
            'estatus': 'Estatus',
            'tamano': 'Tamaño',
            'ubicacion': 'Dirección',
            'pais': 'País',
            'region': 'Región/Estado',
            'ciudad': 'Ciudad'
        }
        
        # Construir mensaje
        preview = f"⚠️ <b>Datos Incompletos - Requiere Completar</b>\n\n"
        preview += f"Gemini extrajo la información pero <b>faltan {len(missing_fields)} campos obligatorios</b>:\n\n"
        
        for field in missing_fields:
            field_label = field_names.get(field, field)
            preview += f"❌ <b>{field_label}</b>\n"
        
        preview += f"\n📋 <b>Datos Extraídos:</b>\n\n"
        
        # Mostrar datos que sí se extrajeron
        if data.get('nombre'):
            preview += f"<b>Nombre:</b> {data['nombre']}\n"
        if data.get('categoria'):
            preview += f"<b>Categoría:</b> {data['categoria']}\n"
        if data.get('ciudad'):
            preview += f"<b>Ciudad:</b> {data['ciudad']}\n"
        if data.get('region'):
            preview += f"<b>Región:</b> {data['region']}\n"
        
        preview += f"\n💡 <b>Opciones:</b>\n"
        preview += f"• <b>Completar ahora</b>: Te preguntaré cada campo faltante\n"
        preview += f"• <b>Rechazar</b>: Descartar esta iniciativa"
        
        # Guardar missing_fields en contexto
        context.user_data['pending_initiative_id'] = initiative_id
        context.user_data['missing_fields'] = missing_fields
        
        # Botones
        keyboard = [
            [
                InlineKeyboardButton("✏️ Completar Ahora", callback_data=f"edit_{initiative_id}"),
                InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{initiative_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_chat.send_message(
            preview,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    def _format_preview(self, data: dict, duplicates: list) -> str:
        """Formatea los datos para el preview."""
        
        preview = f"<b>Preview de Iniciativa</b>\n\n"
        
        # Warning de duplicados
        if duplicates:
            preview += "<b>POSIBLES DUPLICADOS:</b>\n"
            for dup in duplicates[:3]:
                preview += f"  • {dup['nombre']} ({dup['ciudad']}) - {dup['similarity']}% similar\n"
            preview += "\n"
        
        # Información básica
        preview += f"<b>Nombre:</b> {data.get('nombre', 'N/A')}\n"
        preview += f"<b>Categoría:</b> {data.get('categoria', 'N/A')}\n"
        preview += f"<b>Ciudad:</b> {data.get('ciudad', 'N/A')}, {data.get('region', 'N/A')}\n\n"
        
        # Descripción (truncada)
        desc = data.get('descripcion', '')
        if len(desc) > 200:
            desc = desc[:200] + "..."
        preview += f"<b>Descripción:</b>\n{desc}\n\n"
        
        # Clasificación
        preview += f"<b>Tipo:</b> {data.get('tipo_proyecto', 'N/A')}\n"
        preview += f"<b>Enfoque:</b> {data.get('tipo_enfoque', 'N/A')}\n"
        preview += f"<b>Estatus:</b> {data.get('estatus', 'N/A')}\n"
        preview += f"<b>Tamaño:</b> {data.get('tamano', 'N/A')}\n\n"
        
        # Tags
        tags = data.get('etiquetas', [])
        if tags:
            preview += f"<b>Etiquetas:</b> {', '.join(tags)}\n\n"
        
        # Contacto
        if data.get('email'):
            preview += f"<b>Email:</b> {data['email']}\n"
        if data.get('sitio_web'):
            preview += f"<b>Web:</b> {data['sitio_web']}\n"
        if data.get('facebook'):
            preview += f"<b>Facebook:</b> {data['facebook']}\n"
        
        return preview
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler de botones inline."""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data
        action, initiative_id = query.data.split('_')
        initiative_id = int(initiative_id)
        
        if action == "confirm":
            await self._confirm_initiative(query, initiative_id)
        elif action == "reject":
            await self._reject_initiative(query, initiative_id)
        elif action == "edit":
            await self._start_field_editing(query, context, initiative_id)
    
    async def _confirm_initiative(self, query, initiative_id: int):
        """Confirma y publica una iniciativa."""
        await query.edit_message_text("⏳ Publicando en Bekaab...")
        
        try:
            # Obtener datos
            initiative_data = self.pending_initiatives.get(initiative_id)
            if not initiative_data:
                # Intentar obtener desde DB
                record = self.db.get_initiative(initiative_id)
                if record:
                    initiative_data = record['data']
                else:
                    await query.edit_message_text("❌ Error: Iniciativa no encontrada")
                    return
            
            # Actualizar status en DB
            self.db.update_initiative_status(initiative_id, 'confirmed')
            
            # Publicar en Bekaab
            success, post_id, error = self.bekaab_client.create_initiative(initiative_data)
            
            if success:
                # Actualizar status
                self.db.update_initiative_status(initiative_id, 'published')
                
                # Limpiar contexto
                if initiative_id in self.pending_initiatives:
                    del self.pending_initiatives[initiative_id]
                
                await query.edit_message_text(
                    f"<b>¡Iniciativa publicada con éxito!</b>\n\n"
                    f"Post ID en Bekaab: {post_id}\n"
                    f"Initiative ID local: {initiative_id}\n\n"
                    f"La iniciativa se creó en estado 'draft' para revisión final.",
                    parse_mode='HTML'
                )
            else:
                self.db.update_initiative_status(initiative_id, 'failed')
                await query.edit_message_text(
                    f"❌ <b>Error al publicar:</b>\n\n{error}",
                    parse_mode='HTML'
                )
        
        except Exception as e:
            logger.error(f"Error confirming initiative: {e}")
            await query.edit_message_text(f"Error inesperado: {str(e)}")
    
    async def _reject_initiative(self, query, initiative_id: int):
        """Rechaza una iniciativa."""
        self.db.update_initiative_status(initiative_id, 'rejected')
        
        if initiative_id in self.pending_initiatives:
            del self.pending_initiatives[initiative_id]
        
        await query.edit_message_text(
            "Iniciativa rechazada.\n\n"
            "Envía otra URL para procesar una nueva iniciativa."
        )
    
    async def _start_field_editing(self, query, context: ContextTypes.DEFAULT_TYPE, initiative_id: int):
        """Inicia el flujo de edición interactiva de campos."""
        missing_fields = context.user_data.get('missing_fields', [])
        
        if not missing_fields:
            await query.edit_message_text("❌ No hay campos faltantes.")
            return
        
        # Configurar modo edición
        context.user_data['editing_mode'] = True
        context.user_data['current_field_index'] = 0
        context.user_data['editing_initiative_id'] = initiative_id
        
        # Preguntar primer campo
        field_labels = {
            'ubicacion': 'Ubicación/Dirección',
            'region': 'Región/Estado',
            'ciudad': 'Ciudad',
            'pais': 'País'
        }
        
        first_field = missing_fields[0]
        field_label = field_labels.get(first_field, first_field)
        
        message = f"📝 <b>Completando campos ({1}/{len(missing_fields)})</b>\n\n"
        message += f"<b>{field_label}:</b>\n"
        message += "Envía tu respuesta:"
        
        await query.edit_message_text(message, parse_mode='HTML')
    
    async def _process_field_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, answer: str):
        """Procesa la respuesta del usuario para un campo."""
        missing_fields = context.user_data.get('missing_fields', [])
        current_index = context.user_data.get('current_field_index', 0)
        initiative_id = context.user_data.get('editing_initiative_id')
        
        current_field = missing_fields[current_index]
        initiative_data = self.pending_initiatives.get(initiative_id, {})
        
        # Guardar respuesta
        if current_field == 'etiquetas':
            tags = [tag.strip().lower() for tag in answer.split(',')]
            initiative_data[current_field] = tags
        else:
            initiative_data[current_field] = answer.strip()
        
        self.pending_initiatives[initiative_id] = initiative_data
        current_index += 1
        context.user_data['current_field_index'] = current_index
        
        # Si ya completamos todos
        if current_index >= len(missing_fields):
            context.user_data['editing_mode'] = False
            await update.message.reply_text("✅ ¡Campos completados! Validando...")
            
            is_valid, errors, duplicates = self.validator.validate(initiative_data)
            
            if not is_valid:
                error_text = "❌ Errores:\n\n" + "\n".join(f"• {e}" for e in errors)
                await update.message.reply_text(error_text)
                context.user_data.clear()
                return
            
            # Mostrar preview final
            await self._send_final_preview(update, context, initiative_id, initiative_data, duplicates)
            context.user_data.clear()
            return
        
        # Preguntar siguiente campo
        field_labels = {
            'ubicacion': 'Ubicación/Dirección',
            'region': 'Región/Estado',
            'ciudad': 'Ciudad',
            'pais': 'País'
        }
        
        next_field = missing_fields[current_index]
        field_label = field_labels.get(next_field, next_field)
        
        message = f"✅ Guardado.\n\n📝 <b>Campo {current_index + 1}/{len(missing_fields)}</b>\n\n"
        message += f"<b>{field_label}:</b>\n"
        message += "Envía tu respuesta:"
        
        await update.message.reply_text(message, parse_mode='HTML')
    
    async def _send_final_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, initiative_id: int, data: dict, duplicates: list):
        """Envía preview final después de completar campos."""
        preview_text = self._format_preview(data, duplicates)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar y Publicar", callback_data=f"confirm_{initiative_id}"),
                InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{initiative_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            preview_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    def _is_valid_url(self, text: str) -> bool:
        """Valida que el texto sea una URL."""
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False
