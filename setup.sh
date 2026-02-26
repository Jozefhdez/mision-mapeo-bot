#!/bin/bash

# Script de setup inicial para Misión Mapeo Bot

set -e

echo "Misión Mapeo Bot - Setup Inicial"
echo ""

if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

echo "Docker y Docker Compose encontrados"
echo ""

# Verificar .env
if [ ! -f .env ]; then
    echo "Archivo .env no encontrado"
    echo "Creando .env desde .env.example..."
    cp .env.example .env
    echo "Archivo .env creado"
    echo ""
    echo "IMPORTANTE: Edita el archivo .env con tus credenciales:"
    echo " - TELEGRAM_BOT_TOKEN"
    echo " - TELEGRAM_ADMIN_USER_ID"
    echo " - CODE_SNIPPET_API_KEY"
    echo ""
    read -p "Presiona Enter cuando hayas configurado .env..."
else
    echo "Archivo .env encontrado"
fi

echo ""
echo "Iniciando contenedor de Ollama..."
docker-compose up -d ollama

echo "Esperando que Ollama esté listo..."
sleep 5

echo "Descargando modelo Llama 3.1 8B"
docker exec -it mision-mapeo-ollama ollama pull llama3.1:8b

echo ""
echo "Construyendo imagen del bot..."
docker-compose build

echo ""
echo "Iniciando bot..."
docker-compose up -d

echo ""
echo "Setup completado!"
echo ""
echo "Estado de los contenedores:"
docker-compose ps

echo ""
echo "Para ver los logs:"
echo " docker-compose logs -f app"
echo ""
echo "El bot está listo! Envíale un mensaje en Telegram."
