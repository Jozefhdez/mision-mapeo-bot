# Misión Mapeo Bot

Bot de Telegram para registro asistido de iniciativas socioambientales en Bekaab.

## Quick Start

### 1. Requisitos

- Docker y Docker Compose
- Bot de Telegram (obtener token de @BotFather)
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
CODE_SNIPPET_API_KEY=     # API key de Bekaab
```

### 3. Despliegue

```bash
# Iniciar Ollama primero
docker-compose up -d ollama

# Descargar modelo de Llama (solo primera vez)
docker exec -it mision-mapeo-ollama ollama pull llama3.1:8b

# Iniciar aplicación completa
docker-compose up -d

# Ver logs
docker-compose logs -f app
```

### 4. Uso

1. Inicia conversación con tu bot en Telegram
2. Envía `/start` para verificar que funciona
3. Envía una URL de una iniciativa
4. El bot procesará automáticamente:
   - Scraping del contenido
   - Extracción con IA
   - Validación y detección de duplicados
5. Revisa el preview y confirma o rechaza
6. ¡Listo! Se publica en Bekaab en modo draft

## Estructura del Proyecto

```
mision-mapeo-bot/
├── src/
│   ├── __init__.py
│   ├── models.py          # Modelos Pydantic
│   ├── database.py        # SQLite operations
│   ├── scraper.py         # Web scraping
│   ├── extractor.py       # LLM extraction
│   ├── validator.py       # Validation & duplicates
│   ├── bekaab_client.py   # Bekaab API client
│   └── bot.py             # Telegram bot
├── main.py                # Entry point
├── requirements.txt       # Dependencies
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Comandos Útiles

```bash
# Detener servicios
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar solo el bot
docker-compose restart app

# Acceder a la DB SQLite
docker exec -it mision-mapeo-bot sqlite3 /app/data/initiatives.db

# Limpiar todo (borra datos)
docker-compose down -v
rm -rf data/ logs/
```

## Base de Datos

SQLite con 3 tablas:

- **initiatives**: Iniciativas procesadas
- **sources**: URLs scrapeadas
- **extraction_logs**: Logs de llamadas al LLM