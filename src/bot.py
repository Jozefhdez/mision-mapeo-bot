"""
Bot de Telegram para registro asistido de iniciativas.
"""
import os
import logging
import asyncio
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
from src.form_config import FORM_CONFIG
from src.models import Initiative
from pydantic import ValidationError

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
        self.pending_initiatives = {}
    
    def run(self):
        """Inicia el bot."""
        application = Application.builder().token(self.token).build()
        
        application.add_handler(CommandHandler("start", self.start_command))
        # Removemos las fotos agrupadas y otros tipos de media ajena a menos que sea el campo de imagenes.
        application.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        logger.info("Bot started...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.allowed_user_ids:
            await update.message.reply_text("❌ No autorizado.")
            return
        
        await update.message.reply_text("¡Hola! Envía una URL para procesar una iniciativa.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in self.allowed_user_ids:
            return

        if context.user_data.get('editing_mode') and update.message.photo and self._is_image_input_active(context):
            file_id = update.message.photo[-1].file_id
            buffer = context.user_data.setdefault('image_edit_buffer', [])

            if update.message.media_group_id:
                current_group = context.user_data.get('image_edit_media_group')
                if current_group != update.message.media_group_id:
                    buffer.clear()
                    context.user_data['image_edit_media_group'] = update.message.media_group_id

                if file_id not in buffer:
                    buffer.append(file_id)

                await self._schedule_image_input_finalize(update, context, update.message.media_group_id)
                return

            buffer.clear()
            buffer.append(file_id)
            await self._finalize_image_input(update, context)
            return

        if context.user_data.get('editing_mode'):
            if update.message.photo:
                answer = update.message.photo[-1].file_id
            else:
                answer = update.message.text
                
            await self._process_field_answer(update, context, answer)
            return
        
        if update.message.text and self._is_valid_url(update.message.text):
            await self._process_url(update, context, update.message.text)
        elif update.message.photo:
            return
        else:
            await update.message.reply_text("Envía una URL válida o procesa la actual.")

    def _is_image_input_active(self, context):
        mod_field = context.user_data.get('mod_field')
        if mod_field == 'imagenes':
            return True

        missing_fields = context.user_data.get('missing_fields', [])
        idx = context.user_data.get('current_field_index', 0)
        if missing_fields and idx < len(missing_fields):
            return missing_fields[idx] == 'imagenes'

        return False

    async def _schedule_image_input_finalize(self, update, context, media_group_id):
        existing_task = context.user_data.get('image_edit_finalize_task')
        if existing_task and not existing_task.done():
            existing_task.cancel()

        task = asyncio.create_task(
            self._finalize_image_input_after_delay(update, context, media_group_id)
        )
        context.user_data['image_edit_finalize_task'] = task

    async def _finalize_image_input_after_delay(self, update, context, media_group_id):
        try:
            await asyncio.sleep(1.2)
        except asyncio.CancelledError:
            return

        if context.user_data.get('image_edit_media_group') != media_group_id:
            return

        await self._finalize_image_input(update, context)

    async def _finalize_image_input(self, update, context):
        if not context.user_data.get('editing_mode'):
            return

        new_images = list(dict.fromkeys(context.user_data.get('image_edit_buffer', [])))
        if not new_images:
            return

        await self._process_field_answer(update, context, new_images)
            
    async def _process_url(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        status_msg = await update.message.reply_text("Procesando...")
        try:
            data, _ = self.extractor.extract(url)
            if not data:
                await status_msg.edit_text("Error en extracción.")
                return

            self._normalize_initiative_data(data)
            
            initiative_id = self.db.create_initiative(data, url)
            self.pending_initiatives[initiative_id] = data
            
            # Verificar campos faltantes (según form_config)
            missing = [f for f, conf in FORM_CONFIG.items() if conf.get('required') and not data.get(f)]
            
            await status_msg.delete()
            if missing:
                context.user_data.update({'pending_id': initiative_id, 'missing': missing})
                await self._send_incomplete_preview(update, context, initiative_id, data, missing)
            else:
                _, _, duplicates = self.validator.validate(data)
                await self._send_preview(update, context, initiative_id, data, duplicates)
        except Exception as e:
            await status_msg.edit_text(f"Error: {str(e)}")

    async def _send_preview(self, update, context, init_id, data, duplicates, edit=False, query=None):
        self._normalize_initiative_data(data)

        text = "<b>Preview de Iniciativa</b>\n\n"
        for f, conf in FORM_CONFIG.items():
            if data.get(f): 
                val = data[f]
                if isinstance(val, list):
                    val = ", ".join(val)
                text += f"<b>{conf['label']}:</b> {val}\n"
        
        # Pydantic validation
        pydantic_errors = []
        try:
            Initiative(**data)
        except ValidationError as e:
            for err in e.errors():
                field_raw = err["loc"][0] if err["loc"] else "Desconocido"
                # Intentamos obtener un nombre amigable desde FORM_CONFIG
                field_name = FORM_CONFIG.get(field_raw, {}).get("label", field_raw)
                
                err_type = err.get("type", "")
                ctx = err.get("ctx", {})
                
                if err_type == "missing":
                    msg = "Falta completar este campo obligatorio."
                elif err_type == "string_too_short":
                    min_len = ctx.get("min_length", "?")
                    msg = f"El texto es muy corto (mínimo {min_len} caracteres requeridos)."
                elif err_type == "string_too_long":
                    max_len = ctx.get("max_length", "?")
                    msg = f"El texto es muy largo (máximo {max_len} caracteres permitidos)."
                elif err_type == "too_short" and isinstance(data.get(field_raw), list):
                    min_len = ctx.get("min_length", "?")
                    msg = f"Debes elegir/escribir al menos {min_len} opciones."
                elif err_type == "too_long" and isinstance(data.get(field_raw), list):
                    max_len = ctx.get("max_length", "?")
                    msg = f"Debes elegir/escribir como máximo {max_len} opciones."
                elif err_type == "string_type":
                    msg = "Falta responder, o se esperaba un texto."
                else:
                    # Fallback si Pydantic regresa un error inesperado
                    msg = err.get("msg", "Error de validación.")
                    
                pydantic_errors.append(f"<b>{field_name}:</b> {msg}")

        if pydantic_errors:
            text += "\n⚠️ <b>Faltan datos o tienen errores:</b>\n"
            for err in pydantic_errors:
                text += f"• {err}\n"
        
        keyboard = []
        if not pydantic_errors:
            keyboard.append([InlineKeyboardButton("✅ Confirmar y Publicar", callback_data=f"confirm_{init_id}")])
            
        keyboard.append([InlineKeyboardButton("✏️ Modificar Datos", callback_data=f"modmenu_{init_id}")])
        keyboard.append([InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{init_id}")])
        markup = InlineKeyboardMarkup(keyboard)
        
        if edit and query: 
            await query.edit_message_text(text, reply_markup=markup, parse_mode='HTML')
        else: 
            await update.effective_message.reply_text(text, reply_markup=markup, parse_mode='HTML')

    async def _send_incomplete_preview(self, update, context, init_id, data, missing):
        text = "⚠️ <b>Datos Incompletos</b>. Campos faltantes:\n"
        for f in missing: text += f"• {FORM_CONFIG[f]['label']}\n"
        
        keyboard = [[InlineKeyboardButton("✏️ Completar Ahora", callback_data=f"edit_{init_id}")],
                    [InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{init_id}")]]
        await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

    async def _start_field_editing(self, query, context, initiative_id):
        """Inicia el flujo de edición interactiva de campos faltantes."""
        missing = context.user_data.get('missing', [])
        if not missing:
            await query.edit_message_text("❌ No hay campos faltantes.")
            return
        
        context.user_data.update({
            'init_id': initiative_id,
            'editing_mode': True,
            'current_field_index': 0,
            'missing_fields': missing,
            'mod_field': None
        })
        
        await self._ask_current_field(query.message, context, is_callback=True)

    async def _ask_current_field(self, message_or_query, context, is_callback=False):
        """Helper para preguntar el campo actual en el flujo de completado."""
        init_id = context.user_data['init_id']
        missing = context.user_data['missing_fields']
        idx = context.user_data['current_field_index']
        field = missing[idx]
        conf = FORM_CONFIG[field]
        
        msg = f"📝 <b>Completando campos ({idx + 1}/{len(missing)})</b>\n\n<b>{conf['label']}:</b>\n{conf['description']}"
        if conf.get('example'): 
            msg += f"\n\n💡 <i>{conf['example']}</i>"
            
        if conf['type'] == 'choice':
            keyboard = [[InlineKeyboardButton(opt, callback_data=f"setchoice_{init_id}_{field}_{i}")] for i, opt in enumerate(conf['options'])]
            markup = InlineKeyboardMarkup(keyboard)
            if is_callback:
                await message_or_query.edit_text(msg + "\n\nSelecciona una opción:", reply_markup=markup, parse_mode='HTML')
            else:
                await message_or_query.reply_text(msg + "\n\nSelecciona una opción:", reply_markup=markup, parse_mode='HTML')
        elif conf['type'] == 'multiselect':
            selected = context.user_data.setdefault('multiselect_selected', {})
            if field not in selected:
                selected[field] = []
            await self._send_multiselect_prompt(
                message_or_query=message_or_query,
                context=context,
                init_id=init_id,
                field=field,
                conf=conf,
                selected_values=selected[field],
                is_callback=is_callback,
                show_back=False
            )
        else:
            msg += "\n\nEnvía tu respuesta:"
            if is_callback:
                await message_or_query.edit_text(msg, parse_mode='HTML')
            else:
                await message_or_query.reply_text(msg, parse_mode='HTML')

    async def _send_multiselect_prompt(self, message_or_query, context, init_id, field, conf, selected_values, is_callback=False, show_back=False):
        selected_values = selected_values or []
        msg = f"📝 <b>{conf['label']}</b>\n\n{conf['description']}"
        if conf.get('example'):
            msg += f"\n\n💡 <i>{conf['example']}</i>"

        keyboard = []
        for i, opt in enumerate(conf['options']):
            prefix = "✅ " if opt in selected_values else "▫️ "
            keyboard.append([InlineKeyboardButton(f"{prefix}{opt}", callback_data=f"msel_{init_id}_{field}_{i}")])

        keyboard.append([InlineKeyboardButton("✅ Listo", callback_data=f"msdone_{init_id}_{field}")])
        if show_back:
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"back_{init_id}")])

        markup = InlineKeyboardMarkup(keyboard)
        if is_callback:
            if hasattr(message_or_query, 'edit_message_text'):
                await message_or_query.edit_message_text(msg + "\n\nSelecciona una o más opciones:", reply_markup=markup, parse_mode='HTML')
            else:
                await message_or_query.edit_text(msg + "\n\nSelecciona una o más opciones:", reply_markup=markup, parse_mode='HTML')
        else:
            await message_or_query.reply_text(msg + "\n\nSelecciona una o más opciones:", reply_markup=markup, parse_mode='HTML')

    async def handle_callback(self, update, context):
        query = update.callback_query
        await query.answer()
        action, _, payload = query.data.partition('_')

        if action in {"confirm", "reject", "edit", "modmenu", "back"}:
            init_id = int(payload)
            if action == "confirm":
                await self._confirm(query, init_id)
            elif action == "reject":
                await self._reject(query, init_id)
            elif action == "edit":
                await self._start_field_editing(query, context, init_id)
            elif action == "modmenu":
                await self._send_mod_menu(query, init_id)
            elif action == "back":
                await self._back_to_preview(query, context, init_id)
            return

        if action == "modfield":
            init_id_raw, field = payload.split('_', 1)
            await self._start_field_mod(query, context, int(init_id_raw), field)
            return

        if action == "setchoice":
            init_id_raw, rest = payload.split('_', 1)
            field, idx_raw = rest.rsplit('_', 1)
            val = FORM_CONFIG[field]['options'][int(idx_raw)]
            context.user_data['init_id'] = int(init_id_raw)
            await self._process_field_answer(update, context, val)
            return

        if action == "msel":
            init_id_raw, rest = payload.split('_', 1)
            field, idx_raw = rest.rsplit('_', 1)
            init_id = int(init_id_raw)
            option = FORM_CONFIG[field]['options'][int(idx_raw)]

            selected = context.user_data.setdefault('multiselect_selected', {})
            current = selected.setdefault(field, [])

            if option in current:
                current.remove(option)
            else:
                current.append(option)

            selected[field] = current
            await self._send_multiselect_prompt(
                message_or_query=query,
                context=context,
                init_id=init_id,
                field=field,
                conf=FORM_CONFIG[field],
                selected_values=current,
                is_callback=True,
                show_back=context.user_data.get('mod_field') is not None
            )
            return

        if action == "msdone":
            init_id_raw, field = payload.split('_', 1)
            init_id = int(init_id_raw)
            selected = context.user_data.get('multiselect_selected', {}).get(field, [])
            context.user_data['init_id'] = init_id
            await self._process_field_answer(update, context, selected)

    async def _send_mod_menu(self, query, init_id):
        keyboard = [[InlineKeyboardButton(conf['label'], callback_data=f"modfield_{init_id}_{f}")] for f, conf in FORM_CONFIG.items()]
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"back_{init_id}")])
        await query.edit_message_text("Selecciona campo a modificar:", reply_markup=InlineKeyboardMarkup(keyboard))

    async def _start_field_mod(self, query, context, init_id, field):
        context.user_data.update({
            'editing_mode': True, 
            'mod_field': field, 
            'init_id': init_id,
            'missing_fields': []
        })
        if field == 'imagenes':
            pending_task = context.user_data.pop('image_edit_finalize_task', None)
            if pending_task and not pending_task.done():
                pending_task.cancel()
            context.user_data.pop('image_edit_media_group', None)
            context.user_data.pop('image_edit_buffer', None)
        conf = FORM_CONFIG[field]
        msg = f"📝 Modificando <b>{conf['label']}</b>\n\n{conf['description']}"
        if conf.get('example'): msg += f"\n\n💡 <i>{conf['example']}</i>"
        
        if conf['type'] == 'choice':
            keyboard = [[InlineKeyboardButton(opt, callback_data=f"setchoice_{init_id}_{field}_{i}")] for i, opt in enumerate(conf['options'])]
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"back_{init_id}")])
            await query.edit_message_text(msg + "\n\nSelecciona una opción:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        elif conf['type'] == 'multiselect':
            data = self.pending_initiatives.get(init_id, {})
            initial = data.get(field, [])
            if isinstance(initial, str):
                initial = [e.strip() for e in initial.split(',') if e.strip()]
            context.user_data.setdefault('multiselect_selected', {})[field] = initial
            await self._send_multiselect_prompt(
                message_or_query=query,
                context=context,
                init_id=init_id,
                field=field,
                conf=conf,
                selected_values=initial,
                is_callback=True,
                show_back=True
            )
        else:
            keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"back_{init_id}")]]
            await query.edit_message_text(msg + "\n\nEnvía el nuevo valor:", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

    async def _process_field_answer(self, update, context, answer):
        init_id = context.user_data.get('init_id')
        if not init_id:
            await update.effective_message.reply_text("❌ Error de sesión: init_id perdido. Vuelve a enviar la URL.")
            context.user_data.clear()
            return
            
        is_callback = update.callback_query is not None
        message_to_edit = update.callback_query.message if is_callback else update.message
        
        mod_field = context.user_data.get('mod_field')
        missing_fields = context.user_data.get('missing_fields', [])
        
        data = self.pending_initiatives.get(init_id, {})
        
        if mod_field:
            if mod_field == 'imagenes':
                new_images = self._coerce_field_value(mod_field, answer)
                merged = []
                for image_id in new_images:
                    if image_id not in merged:
                        merged.append(image_id)
                data['imagenes'] = merged
            else:
                data[mod_field] = self._coerce_field_value(mod_field, answer)
            self._normalize_initiative_data(data)

            self.pending_initiatives[init_id] = data

            self._clear_editing_state(context)
            
            # Show preview
            _, _, dups = self.validator.validate(data)
            # if is_callback, we can edit the message, else reply
            await self._send_preview(update, context, init_id, data, dups, edit=is_callback, query=update.callback_query)
            
        elif missing_fields:
            # Sequencing through missing fields
            idx = context.user_data.get('current_field_index', 0)
            field = missing_fields[idx]

            data[field] = self._coerce_field_value(field, answer)
            self._normalize_initiative_data(data)
                
            self.pending_initiatives[init_id] = data
            
            idx += 1
            if idx < len(missing_fields):
                context.user_data['current_field_index'] = idx
                await self._ask_current_field(message_to_edit, context, is_callback=is_callback)
            else:
                self._clear_editing_state(context)
                _, _, dups = self.validator.validate(data)
                
                # Check Pydantic model for complete validation if needed, or Validator does it.
                # Right now falling back to Validator because user wants Pydantic validation 
                # but models.py handles strict Pydantic which we should invoke
                
                await self._send_preview(update, context, init_id, data, dups, edit=is_callback, query=update.callback_query)

    def _coerce_field_value(self, field, answer):
        if answer is None:
            return ""

        if field in ('etiquetas', 'imagenes'):
            if isinstance(answer, list):
                return [str(e).strip() for e in answer if str(e).strip()]
            if isinstance(answer, str):
                return [e.strip() for e in answer.split(',') if e.strip()]
            return [str(answer).strip()]

        if field in ('ods', 'certificaciones'):
            if isinstance(answer, list):
                return ', '.join([str(e).strip() for e in answer if str(e).strip()])
            return str(answer).strip()

        if field == 'institucion' and str(answer).strip() == '(No seleccionar)':
            return ''

        return str(answer).strip()

    def _normalize_initiative_data(self, data):
        if not isinstance(data, dict):
            return data

        for list_field in ('etiquetas', 'imagenes'):
            if list_field not in data:
                continue
            data[list_field] = self._coerce_field_value(list_field, data.get(list_field))

        return data

    def _clear_editing_state(self, context):
        pending_task = context.user_data.pop('image_edit_finalize_task', None)
        current_task = asyncio.current_task()
        if pending_task and not pending_task.done() and pending_task is not current_task:
            pending_task.cancel()

        keys_to_remove = ['editing_mode', 'mod_field', 'missing_fields', 'current_field_index', 'image_edit_media_group', 'image_edit_buffer']
        for k in keys_to_remove:
            context.user_data.pop(k, None)

    def _is_valid_url(self, text):
        try: result = urlparse(text); return all([result.scheme, result.netloc])
        except: return False

    async def _confirm(self, query, init_id): await query.edit_message_text("Publicado!")
    async def _reject(self, query, init_id): await query.edit_message_text("Descartado.")
    async def _back_to_preview(self, query, context, init_id):
        data = self.pending_initiatives.get(init_id)
        if not data:
            await query.edit_message_text("❌ No se encontró la iniciativa.")
            return

        mod_field = context.user_data.get('mod_field')
        if mod_field and FORM_CONFIG.get(mod_field, {}).get('type') == 'multiselect':
            selected = context.user_data.get('multiselect_selected', {}).get(mod_field)
            if selected is not None:
                data[mod_field] = self._coerce_field_value(mod_field, selected)
                self.pending_initiatives[init_id] = data

        self._clear_editing_state(context)
        context.user_data.pop('multiselect_selected', None)

        _, _, dups = self.validator.validate(data)
        await self._send_preview(None, context, init_id, data, dups, edit=True, query=query)
    async def _start_editing(self, query, context, init_id): pass
