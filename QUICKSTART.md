# 🚀 Quick Start - Misión Mapeo Bot

Guía rápida para poner en marcha el bot en 5 minutos.

## Prerrequisitos

✅ Docker instalado  
✅ Bot de Telegram creado (@BotFather)  
✅ API Key de Bekaab configurada

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
- ✅ Inicia Ollama
- ✅ Descarga Llama 3.1 8B (~4.7GB)
- ✅ Construye la imagen Docker
- ✅ Inicia el bot

**⏱️ Tiempo estimado:** 10-15 minutos (dependiendo de tu conexión)

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

## 🎯 Ejemplo de Uso

```
Tu: /start
Bot: 👋 ¡Hola! Soy el bot de Misión Mapeo...

Tu: https://ejemplo.com/iniciativa
Bot: ⏳ Procesando iniciativa...
Bot: 📄 Extrayendo contenido...
Bot: 🤖 Analizando con IA...
Bot: ✅ Validando datos...
Bot: [Muestra preview con botones]

Tu: [Presionas ✅ Confirmar]
Bot: ✅ ¡Iniciativa publicada con éxito!
```

## 📝 Comandos Útiles

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

## 🐛 Problemas Comunes

### El bot no responde

```bash
# Verificar logs
docker-compose logs app | tail -50
```

Posibles causas:
- Token de bot incorrecto
- User ID incorrecto
- Bot no tiene acceso a internet

### Error conectando a Ollama

```bash
# Verificar que Ollama está corriendo
docker-compose ps ollama

# Reiniciar Ollama
docker-compose restart ollama

# Verificar modelo descargado
docker exec -it mision-mapeo-ollama ollama list
```

### Error publicando en Bekaab

- Verificar API key en `.env`
- Verificar que Code Snippet esté activo en WordPress
- Verificar URL de Bekaab

## 📚 Siguiente Paso

Lee [README.md](README.md) para documentación completa.

## 💡 Tips

- Las iniciativas se crean en **draft** - revisa en WordPress antes de publicar
- El bot solo responde al user ID configurado (seguridad)
- Los datos se guardan en SQLite (`data/initiatives.db`)
- Los logs del LLM incluyen tokens usados

## 🆘 Soporte

Si algo no funciona:

1. Revisa logs: `docker-compose logs -f`
2. Verifica `.env` esté configurado correctamente
3. Asegúrate que Ollama descargó el modelo
4. Verifica conectividad a internet