# Quick Start

Guía rápida para poner en marcha el bot en 5 minutos.

## Prerrequisitos

- Docker instalado  
- Bot de Telegram creado (@BotFather)  
- API Key de OpenRouter (https://openrouter.ai/keys)
- API Key de Bekaab configurada

## Paso 1: Configurar Variables de Entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tus datos
nano .env
```

**Variables CRÍTICAS a configurar:**

```bash
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...    # De @BotFather
TELEGRAM_ADMIN_USER_ID=12345678         # Tu user ID
OPENROUTER_API_KEY=sk-or-v1-...         # De OpenRouter
CODE_SNIPPET_API_KEY=tu-clave-aqui      # De WordPress
LLM_MODEL=google/gemini-2.5-flash-lite  # Modelo recomendado (ultra rápido, económico)
```

**¿Cómo obtener tu Telegram User ID?**  
Envía `/start` a [@userinfobot](https://t.me/userinfobot)

## Paso 2: Iniciar el Bot

```bash
# Construir e iniciar con Docker
./run-docker.sh
```

El script automáticamente:
- Construye la imagen Docker
- Detiene contenedores previos
- Inicia el bot con reinicio automático

## Paso 3: Verificar que Funciona

```bash
# Ver logs en tiempo real
docker logs -f mision-mapeo-bot
```

Deberías ver:
```
Bot started - polling for messages...
```

## Paso 4: Probar el Bot

1. Abre Telegram
2. Busca tu bot
3. Envía: `/start`
4. Envía una URL de prueba
5. **Si faltan campos:** Presiona "Completar Ahora" y el bot te preguntará cada campo uno por uno
6. Revisa el preview y presiona "Confirmar y Publicar"

## Comandos Útiles

```bash
# Iniciar/Rebuildar el bot
./run-docker.sh

# Ver logs en tiempo real
docker logs -f mision-mapeo-bot

# Detener el bot
docker stop mision-mapeo-bot

# Reiniciar el bot
docker restart mision-mapeo-bot

# Ver estado del contenedor
docker ps

# Ver la base de datos
docker exec -it mision-mapeo-bot sqlite3 /app/data/initiatives.db
sqlite> SELECT * FROM initiatives;
```