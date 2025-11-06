#!/bin/bash

# Тестовый скрипт для проверки запросов

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}Тест запросов установщика${NC}"
echo ""

# Перенаправляем ввод с терминала
exec < /dev/tty

# Тест 1: Домен
echo -e "${BLUE}Тест 1: Запрос домена${NC}"
read -p "Введите домен: " DOMAIN_NAME
echo "Получено: '$DOMAIN_NAME'"
echo ""

# Тест 2: Учетные данные
echo -e "${BLUE}Тест 2: Запрос учетных данных${NC}"
echo ""

read -p "Логин 4tochki API: " FOURTHCHKI_LOGIN
echo "Получено: '$FOURTHCHKI_LOGIN'"

read -p "Пароль 4tochki API: " FOURTHCHKI_PASSWORD
echo "Получено: '$FOURTHCHKI_PASSWORD'"

read -p "Telegram Bot Token: " TELEGRAM_BOT_TOKEN
echo "Получено: '$TELEGRAM_BOT_TOKEN'"

read -p "Admin Telegram ID: " ADMIN_TELEGRAM_ID
echo "Получено: '$ADMIN_TELEGRAM_ID'"

echo ""
echo -e "${GREEN}Тест завершен!${NC}"
echo ""
echo "Результаты:"
echo "  DOMAIN_NAME: ${DOMAIN_NAME:-'(пусто)'}"
echo "  FOURTHCHKI_LOGIN: ${FOURTHCHKI_LOGIN:-'(пусто)'}"
echo "  FOURTHCHKI_PASSWORD: ${FOURTHCHKI_PASSWORD:-'(пусто)'}"
echo "  TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:-'(пусто)'}"
echo "  ADMIN_TELEGRAM_ID: ${ADMIN_TELEGRAM_ID:-'(пусто)'}"
