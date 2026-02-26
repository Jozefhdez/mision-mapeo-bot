#!/bin/bash

# Script de setup inicial para Misión Mapeo Bot

set -e

echo "Misión Mapeo Bot - Setup Inicial"
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

echo "✅ Docker encontrado"
echo ""

# Verificar .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📝 Creando .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "🔑 IMPORTANTE: Edita el archivo .env con tus credenciales:"
    echo "   - TELEGRAM_BOT_TOKEN (de @BotFather)"
    echo "   - TELEGRAM_ADMIN_USER_ID (tu ID de Telegram)"
    echo "   - OPENROUTER_API_KEY (de https://openrouter.ai/keys)"
    echo "   - CODE_SNIPPET_API_KEY (de WordPress/Bekaab)"
    echo ""
    read -p "⏸️  Presiona Enter cuando hayas configurado .env..."
else
    echo "✅ Archivo .env encontrado"
fi

echo ""
echo "🔨 Construyendo e iniciando bot con Docker..."
echo ""

# Ejecutar script de Docker
./run-docker.sh

echo ""
echo "🎉 Setup completado!"
echo ""
echo "📋 Comandos útiles:"
echo "   - Ver logs:      docker logs -f mision-mapeo-bot"
echo "   - Detener bot:   docker stop mision-mapeo-bot"
echo "   - Reiniciar bot: docker restart mision-mapeo-bot"
echo ""
echo "✨ El bot está listo! Envíale un mensaje en Telegram."
