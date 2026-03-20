# Misión Mapeo Bot

Bot de Telegram para registro asistido de iniciativas socioambientales en Bekaab.

## Quick Start

### 1. Requisitos

- Docker
- Bot de Telegram (obtener token de @BotFather)
- API Key de OpenRouter (https://openrouter.ai/keys)
- API Key configurada en Bekaab (Code Snippet)

### 2. Configuración

```bash
# Copiar ejemplo de variables de entorno
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

Configura las siguientes variables:

```bash
TELEGRAM_BOT_TOKEN=       # Token del bot de Telegram
TELEGRAM_ADMIN_USER_ID=   # Tu user ID de Telegram
OPENROUTER_API_KEY=       # API key de OpenRouter
CODE_SNIPPET_API_KEY=     # API key de Bekaab
LLM_MODEL=deepseek/deepseek-v3.2
```

### 3. Despliegue

```bash
# Construir imagen
docker build -t mision-mapeo-bot .

# Iniciar contenedor
docker run -d \
  --name mision-mapeo-bot \
  --restart unless-stopped \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  mision-mapeo-bot

# Ver logs
docker logs -f mision-mapeo-bot
```

### 4. Uso

1. Inicia conversación con tu bot en Telegram
2. Envía `/start` para verificar que funciona
3. Envía una URL de una iniciativa
4. El bot procesará automáticamente:
   - **DeepSeek accede directamente a la URL** (no necesita scraper)
   - Extracción inteligente del contenido con IA
   - Validación y detección de duplicados
5. **Si faltan campos:** Presiona "Completar Ahora"
   - El bot te preguntará cada campo conversacionalmente
   - Responde con el texto correspondiente
   - Progreso visible (1/3, 2/3, etc.)
6. Revisa el preview final y presiona "Confirmar y Publicar"
7. ¡Listo! Se publica en Bekaab en modo draft

## Estructura del Proyecto

```
mision-mapeo-bot/
├── src/
│   ├── __init__.py
│   ├── models.py          # Modelos Pydantic
│   ├── database.py        # SQLite operations
│   ├── extractor.py       # LLM extraction (Gemini directo)
│   ├── validator.py       # Validation & duplicates
│   ├── bekaab_client.py   # Bekaab API client
│   └── bot.py             # Telegram bot + editor conversacional
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── Dockerfile
└── .env.example
```

## Base de Datos

SQLite con 3 tablas:

- **initiatives**: Iniciativas procesadas
- **sources**: URLs scrapeadas
- **extraction_logs**: Logs de llamadas al LLM

## Comandos Útiles

```bash
# Rebuildar imagen (después de cambios en código)
docker stop mision-mapeo-bot
docker rm mision-mapeo-bot
docker build -t mision-mapeo-bot .
docker run -d --name mision-mapeo-bot --restart unless-stopped --env-file .env \
  -v "$(pwd)/data:/app/data" -v "$(pwd)/logs:/app/logs" mision-mapeo-bot

# Ver logs en tiempo real
docker logs -f mision-mapeo-bot

# Detener el bot
docker stop mision-mapeo-bot

# Reiniciar el bot
docker restart mision-mapeo-bot

# Ver estado del contenedor
docker ps

# Acceder a la DB SQLite
docker exec -it mision-mapeo-bot sqlite3 /app/data/initiatives.db

# Limpiar todo (borra datos)
docker stop mision-mapeo-bot
docker rm mision-mapeo-bot
rm -rf data/ logs/
```
