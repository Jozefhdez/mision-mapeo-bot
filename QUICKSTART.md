# Quick Start

Guía rápida para poner en marcha el bot en 5 minutos.

## Prerrequisitos

Docker instalado  
Bot de Telegram creado (@BotFather)  
API Key de Bekaab configurada

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
CODE_SNIPPET_API_KEY=tu-clave-aqui      # De WordPress
```

**¿Cómo obtener tu Telegram User ID?**  
Envía `/start` a [@userinfobot](https://t.me/userinfobot)

## Paso 2: Usar Script Automático

```bash
chmod +x setup.sh
./setup.sh
```

El script automáticamente:
- Inicia Ollama
- Descarga Llama 3.1 8B (~4.7GB)
- Construye la imagen Docker
- Inicia el bot

**Tiempo estimado:** 10-15 minutos (dependiendo de tu conexión)

## Paso 3: Verificar que Funciona

```bash
# Ver logs en tiempo real
docker-compose logs -f app
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

## Comandos Útiles

```bash
# Ver estado
docker-compose ps

# Detener todo
docker-compose down

# Reiniciar solo el bot
docker-compose restart app

# Ver la base de datos
docker exec -it mision-mapeo-bot sqlite3 /app/data/initiatives.db
sqlite> SELECT * FROM initiatives;
```