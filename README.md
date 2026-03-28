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

# Edita .env con tus credenciales
nano .env
```

Configura las siguientes variables:

```bash
TELEGRAM_BOT_TOKEN= # Token del bot de Telegram
ALLOWED_TELEGRAM_IDS= # IDs de usuarios permitidos separados por comas (Ej: 123456,7891011)
OPENROUTER_API_KEY= # API key de OpenRouter
CODE_SNIPPET_API_KEY= # API key de Bekaab
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
   - **DeepSeek accede directamente a la URL**
   - Extracción inteligente del contenido con IA
   - Validación y detección de duplicados
5. **Si faltan campos:** Presiona "Completar Ahora"
   - El bot te preguntará cada campo conversacionalmente
   - Responde con el texto correspondiente
   - Progreso visible (1/3, 2/3, etc.)
6. **Si deseas modifcar campos:** Presiona "Modificar Datos"
   - El bot te preguntará que campo deseas modificar
   - Responde con las modificaciones o selecciona entre las opciones
7. Revisa el preview final y presiona "Confirmar y Publicar"
8. Listo, se publica en Bekaab

## Estructura del Proyecto

```
mision-mapeo-bot/
├── src/
│   ├── __init__.py
│   ├── models.py          # Modelos Pydantic
│   ├── database.py        # SQLite operations
│   ├── extractor.py       # LLM extraction (Gemini directo)
│   ├── validator.py       # Validation & duplicates
│   ├── form_config.py     # "Source of Truth" de todos los campos del formulario permitidos
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
# Rebuildar imagen
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

## Despliegue en la Nube

El proyecto soporta interacción multi-usuario restringida mediante `ALLOWED_TELEGRAM_IDS` y está listo para producción en cualquier VPS Linux con SSH y Docker.

Los pasos base son los mismos para cualquier proveedor:
1. Conéctate al servidor vía SSH.
2. Instala Docker: `sudo apt install docker.io docker-compose-v2 -y`
3. Clona el repositorio y crea tu archivo `.env`.
4. Ejecuta `docker compose up -d --build`.

---

### Opción A — Oracle Cloud Always Free (gratuito)

- Crea una instancia **VM.Standard.E2.1.Micro** (x86_64) o **VM.Standard.A1.Flex** (ARM). OS recomendado: Ubuntu 22.04.
- Abre el puerto 22 (SSH) en la Security List del VCN y en `iptables` internamente si aplica.
- Sigue los pasos base arriba.

**Ideal si:** quieres costo cero. El bot consume muy pocos recursos.

---

### Opción B — GreenGeeks VPS ($69.95/mes en adelante)

GreenGeeks ofrece VPS administrados con cPanel. El bot puede correr ahí perfectamente via Docker, aunque cPanel no es necesario para este proyecto.

**Planes disponibles:**

| Plan | RAM | vCPU | SSD | Transferencia | Precio/mes |
|------|-----|------|-----|---------------|------------|
| Básico | 4 GB | 4 | 75 GB | 10 TB | $69.95 |
| Popular | 8 GB | 6 | 150 GB | 10 TB | $129.95 |
| Pro | 16 GB | 6 | 250 GB | 10 TB | $179.95 |

**Notas importantes:**
- Incluye cPanel (no necesario para este bot, pero disponible).
- GreenGeeks **no hace backups** del VPS — usa cPanel o un cron propio para respaldos.
- El soporte de GreenGeeks solo cubre infraestructura y cPanel; Docker y el bot son responsabilidad tuya.
- Compensa el 300% de su consumo energético con energía renovable.
- IP dedicada incluida en todos los planes.

**Pasos de configuración:**
1. Contrata un plan VPS en GreenGeeks y espera el email con credenciales SSH.
2. Conéctate: `ssh root@<tu-ip>`
3. Instala Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo apt install docker-compose-v2 -y
   ```
4. Sigue los pasos base arriba.
5. Para reiniciar el VPS puedes usar el dashboard de GreenGeeks sin abrir ticket.

**Ideal si:** ya tienes cuenta en GreenGeeks, prefieres soporte dedicado, o valoras el hosting eco-friendly.