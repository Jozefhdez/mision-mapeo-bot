# Modelo de Datos

Este documento define las estructuras de datos principales del sistema de mapeo de iniciativas sustentables.

---

## 1. Entidad: Initiative

Representa una iniciativa de impacto social, ambiental o sustentable.

### Información General

| Campo | Tipo | Requerido | Descripción / Opciones |
|-------|------|-----------|------------------------|
| **Nombre de la Iniciativa** | `string` | Sí | Nombre distintivo de la iniciativa |
| **Descripción** | `text` | Sí | Descripción detallada del proyecto |
| **Categoría** | `enum` | Sí | Clasificación principal de la iniciativa. **Solo se puede elegir una:**<br><br>**Acción social**<br>• Acción en área natural<br>• Acción en Casa<br>• Acción en el trabajo<br>• Acción en escuela<br>• Acción en localidad<br>• Otra acción<br><br>**Educación y capacitación**<br>• Centro de investigación<br>• Cursos o talleres<br>• Educación básica<br>• Educación media<br>• Educación superior<br>• Otra iniciativa educativa<br><br>**Empresas**<br>• Agricultura o Jardinería<br>• Alimentos o Bebidas<br>• Aparatos Electrónicos<br>• Artículos Desechables<br>• Belleza o Cuidado<br>• Bolsas<br>• Certificadoras<br>• Comercio, Finanzas e Inversión<br>• Consultoría o Servicios<br>• Decoración de Interiores<br>• Emprendimiento<br>• Hogar<br>• Limpieza<br>• Madera<br>• Mascotas<br>• Medios de Comunicación<br>• Mercadotecnia o Publicidad<br>• Niños y bebés<br>• Otro producto o servicio<br>• Papelería y oficina<br>• Reciclaje o desechos<br>• Ropa y accesorios<br>• Salud<br>• Servicios y artículos funerarios<br><br>**Instituciones**<br>• Centro de acopio<br>• Organizacion gubernamental<br>• Organización internacional<br>• Organización No Gubernamental<br>• Otra institución<br><br>**Productores**<br>• Agricultura o ganadería<br>• Apicultura<br>• Aprovechamiento forestal<br>• Artesanía<br>• Caza, pesca o recolección<br>• Otra producción<br><br>**Puntos de intercambio**<br>• Centro comercial<br>• Otro punto de intercambio<br>• Tianguis o mercado<br>• Tienda<br><br>**Tecnologías**<br>• Agua<br>• Aire<br>• Arquitectura o Construcción<br>• Energía<br>• Otra tecnologia<br>• Suelo<br>• Transporte<br><br>**Turismo y esparcimiento**<br>• Balneario<br>• Hotel<br>• Otro turismo<br>• Parque<br>• Restaurante<br>• Transporte (servicio) |
| **Etiquetas** | `array[string]` | Sí | Entre 3 y 5 palabras clave.<br>**Formato:** minúsculas separadas por coma<br>**Ejemplo:** `"biodegradable, derecho ambiental, consumo consciente"` |

### Clasificación del Proyecto

| Campo | Tipo | Requerido | Opciones |
|-------|------|-----------|----------|
| **Tipo de Proyecto** | `enum` | Sí | • En el Hogar<br>• En el Trabajo<br>• Sin Fines de Lucro<br>• Empresarial<br>• Institución u Organización<br>• *(por definir)* |
| **Tipo de Enfoque** | `enum` | Sí | • Social<br>• Ambiental<br>• Sustentable<br>• Regenerativo<br>• Economía Circular |
| **Descripción del Enfoque** | `text` | Sí | Explicación detallada del enfoque seleccionado.<br>**Requisito:** Mínimo 3 párrafos justificando por qué la iniciativa corresponde al enfoque elegido |
| **ODS** | `array[enum]` | Sí | Objetivos de Desarrollo Sostenible que atiende el proyecto.<br>*Se pueden seleccionar múltiples opciones* |

### Características Operativas

| Campo | Tipo | Requerido | Opciones |
|-------|------|-----------|----------|
| **Fuente de los Recursos** | `enum` | Sí | • Particular<br>• Privada<br>• Pública<br>• Mixta<br>• *(por definir)* |
| **Sector Económico** | `enum` | Sí | • Agropecuario<br>• Industrial<br>• De infraestructura pública<br>• De infraestructura económica<br>• De servicios<br>• No aplica<br>• *(por definir)* |
| **Área de Cobertura** | `enum` | Sí | • Local<br>• Regional<br>• Nacional<br>• Multinacional<br>• Global<br>• *(por definir)* |
| **Estatus** | `enum` | Sí | • Idea<br>• En diseño o construcción<br>• Reciente<br>• Consolidado<br>• Completado<br>• *(por definir)* |
| **Tamaño** | `enum` | Sí | • De 1 a 2 colaboradores<br>• De 3 a 10 colaboradores<br>• De 11 a 50 colaboradores<br>• De 51 a 100 colaboradores<br>• De 101 a 500 colaboradores<br>• Más de 500 colaboradores<br>• *(por definir)* |

### Ubicación Geográfica

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| **Ubicación** | `string` | Sí | Dirección completa |
| **País** | `string` | Sí | País donde opera la iniciativa |
| **Región** | `string` | Sí | Estado, provincia o región |
| **Ciudad** | `string` | Sí | Ciudad principal |
| **Código postal** | `string` | No | Código postal de la ubicación |

### Información de Contacto

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| **Teléfono** | `string` | No | Número de contacto |
| **Email de contacto** | `email` | No | Correo electrónico principal |
| **Sitio Web** | `url` | No | Sitio web oficial |

### Redes Sociales

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| **Facebook** | `url` | No | Perfil de Facebook |
| **Twitter** | `url` | No | Perfil de Twitter/X |
| **Instagram** | `url` | No | Perfil de Instagram |

### Medios y Metadata

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| **Imágenes** | `array[file]` | No | Imágenes representativas de la iniciativa |
| **Registrado por** | `string` | Sí | Usuario que registró la iniciativa.<br>*Será asignado por una cuenta especial del proyecto* |

---

## 2. Entidad: Source

Representa las fuentes de información utilizadas para extraer datos de iniciativas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **id** | `uuid` | Identificador único de la fuente |
| **url** | `string` | URL completa de la fuente |
| **domain** | `string` | Dominio principal (ej: `ejemplo.com`) |
| **first_scraped_at** | `timestamp` | Primera vez que se procesó |
| **last_scraped_at** | `timestamp` | Fecha y hora del último scraping |
| **scrape_count** | `integer` | Número de veces procesada |
| **status** | `enum` | Estado actual: `success`, `failed`, `pending` |
| **error_message** | `text` | Mensaje de error si status=failed |
| **initiative_id** | `uuid` | Referencia a la iniciativa extraída (nullable) |

---

## 3. Entidad: ExtractionLog

Registro de actividades de extracción usando modelos de IA.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **id** | `uuid` | Identificador único del log |
| **source_id** | `uuid` | Referencia a la fuente procesada |
| **initiative_id** | `uuid` | Referencia a la iniciativa extraída (nullable) |
| **provider** | `enum` | Proveedor: `local`, `openai` |
| **model_name** | `string` | Nombre del modelo (ej: `llama3.1:8b`, `gpt-4`) |
| **prompt_tokens** | `integer` | Tokens en el prompt |
| **completion_tokens** | `integer` | Tokens en la respuesta |
| **total_tokens** | `integer` | Total de tokens consumidos |
| **cost_usd** | `decimal` | Costo estimado en USD (0 para local) |
| **duration_ms** | `integer` | Duración de la llamada en milisegundos |
| **success** | `boolean` | Si la extracción fue exitosa |
| **error_message** | `text` | Mensaje de error si falló |
| **raw_response** | `jsonb` | Respuesta completa del LLM |
| **timestamp** | `timestamp` | Fecha y hora de la extracción |

---

## 4. Entidad: User (Milestone 2+)

Usuarios autorizados para usar el sistema.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| **id** | `uuid` | Identificador único |
| **telegram_user_id** | `bigint` | ID de usuario de Telegram (único) |
| **telegram_username** | `string` | Username de Telegram |
| **full_name** | `string` | Nombre completo |
| **role** | `enum` | Rol: `admin`, `contributor` |
| **is_active** | `boolean` | Si el usuario está activo |
| **created_at** | `timestamp` | Fecha de registro |
| **last_activity** | `timestamp` | Última interacción con el bot |

---

## 5. Estados de Initiative

| Estado | Descripción |
|--------|-------------|
| `pending` | Extraída pero no confirmada por usuario |
| `confirmed` | Confirmada por usuario, lista para publicar |
| `published` | Registrada exitosamente en Bekaab |
| `failed` | Falló al publicar en Bekaab |
| `rejected` | Usuario rechazó la iniciativa |

---

## Notas

- Los campos marcados con "Sí" son **obligatorios**
- Los campos marcados con "No" son **opcionales**
- `*` indica campo requerido en el formulario original
- Los valores `(por definir)` indican opciones que se añadirán posteriormente