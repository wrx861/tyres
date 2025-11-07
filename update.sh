#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Параметры по умолчанию
CREATE_BACKUP=true
SKIP_BACKUP=false

# Обработка аргументов командной строки
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        *)
            echo "Неизвестный параметр: $1"
            echo "Использование: sudo bash update.sh [--no-backup]"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Обновление 4tochki Tyres App${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Проверка прав root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Этот скрипт должен быть запущен с правами root${NC}"
   echo "Используйте: sudo bash update.sh [--no-backup]"
   exit 1
fi

# Определяем директорию приложения
APP_DIR="/opt/tyres-app"
BACKUP_DIR=""

# Проверяем что директория существует
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}Директория $APP_DIR не найдена!${NC}"
    echo "Убедитесь что приложение установлено."
    exit 1
fi

cd $APP_DIR

# Создание backup
if [ "$SKIP_BACKUP" = false ]; then
    echo -e "${BLUE}[1/9] Создание backup текущей версии...${NC}"
    BACKUP_DIR="/opt/tyres-app-backup-$(date +%Y%m%d_%H%M%S)"
    cp -r $APP_DIR $BACKUP_DIR
    echo -e "${GREEN}✓ Backup создан: $BACKUP_DIR${NC}"
    
    # Удаляем старые backup (оставляем только последние 3)
    echo -e "${YELLOW}→ Очистка старых backup...${NC}"
    BACKUP_COUNT=$(ls -d /opt/tyres-app-backup-* 2>/dev/null | wc -l)
    if [ $BACKUP_COUNT -gt 3 ]; then
        ls -dt /opt/tyres-app-backup-* | tail -n +4 | xargs rm -rf
        REMOVED=$((BACKUP_COUNT - 3))
        echo -e "${GREEN}✓ Удалено старых backup: $REMOVED${NC}"
    else
        echo -e "${GREEN}✓ Старых backup нет (всего: $BACKUP_COUNT)${NC}"
    fi
else
    echo -e "${YELLOW}[1/9] Backup пропущен (--no-backup)${NC}"
fi
echo ""

echo -e "${BLUE}[2/9] Получение обновлений из GitHub...${NC}"
git fetch origin
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Ошибка при git fetch${NC}"
    exit 1
fi

# Показываем что изменилось
echo -e "${YELLOW}Изменения:${NC}"
git log HEAD..origin/main --oneline | head -5
echo ""

echo -e "${BLUE}[3/9] Применение обновлений...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Ошибка при git pull${NC}"
    echo -e "${YELLOW}Откат к backup...${NC}"
    rm -rf $APP_DIR
    cp -r $BACKUP_DIR $APP_DIR
    exit 1
fi
echo -e "${GREEN}✓ Код обновлен${NC}"
echo ""

echo -e "${BLUE}[4/9] Проверка изменений в зависимостях...${NC}"

# Проверяем изменения в requirements.txt
if git diff HEAD@{1} HEAD --name-only | grep -q "backend/requirements.txt"; then
    echo -e "${YELLOW}→ Обнаружены изменения в requirements.txt${NC}"
    
    # Ищем виртуальное окружение
    if [ -d "$APP_DIR/backend/venv" ]; then
        echo -e "${YELLOW}→ Обновление Python зависимостей...${NC}"
        $APP_DIR/backend/venv/bin/pip install -r $APP_DIR/backend/requirements.txt
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Python зависимости обновлены${NC}"
        else
            echo -e "${RED}✗ Ошибка обновления зависимостей${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ Виртуальное окружение не найдено, пропуск...${NC}"
    fi
else
    echo -e "${GREEN}✓ Изменений в requirements.txt нет${NC}"
fi

# Проверяем изменения в package.json
if git diff HEAD@{1} HEAD --name-only | grep -q "frontend/package.json"; then
    echo -e "${YELLOW}→ Обнаружены изменения в package.json${NC}"
    if command -v yarn &> /dev/null; then
        echo -e "${YELLOW}→ Обновление Node.js зависимостей...${NC}"
        cd $APP_DIR/frontend
        yarn install
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Node.js зависимости обновлены${NC}"
        else
            echo -e "${RED}✗ Ошибка обновления зависимостей${NC}"
        fi
        cd $APP_DIR
    fi
else
    echo -e "${GREEN}✓ Изменений в package.json нет${NC}"
fi
echo ""

echo -e "${BLUE}[5/9] Пересборка frontend (если изменился)...${NC}"
# Проверяем изменения в frontend/src
if git diff HEAD@{1} HEAD --name-only | grep -q "frontend/src"; then
    echo -e "${YELLOW}→ Обнаружены изменения в frontend/src${NC}"
    if command -v yarn &> /dev/null; then
        echo -e "${YELLOW}→ Пересборка frontend...${NC}"
        cd $APP_DIR/frontend
        yarn build
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Frontend пересобран${NC}"
        else
            echo -e "${RED}✗ Ошибка пересборки frontend${NC}"
        fi
        cd $APP_DIR
    fi
else
    echo -e "${GREEN}✓ Изменений в frontend/src нет${NC}"
fi
echo ""

echo -e "${BLUE}[6/9] Проверка конфигурации supervisor...${NC}"
# Проверяем наличие старого процесса telegram-bot
if supervisorctl status | grep -q "tyres-telegram-bot"; then
    echo -e "${YELLOW}→ Обнаружен старый процесс tyres-telegram-bot, удаление...${NC}"
    supervisorctl stop tyres-telegram-bot 2>/dev/null
    rm -f /etc/supervisor/conf.d/tyres-telegram-bot.conf
    supervisorctl reread
    supervisorctl update
    echo -e "${GREEN}✓ Старый процесс удален${NC}"
else
    echo -e "${GREEN}✓ Конфигурация актуальна${NC}"
fi
echo ""

echo -e "${BLUE}[7/9] Перезапуск сервисов...${NC}"
# Определяем имена процессов
if supervisorctl status | grep -q "tyres-backend"; then
    BACKEND_NAME="tyres-backend"
else
    BACKEND_NAME="backend"
fi

echo -e "${YELLOW}→ Перезапуск $BACKEND_NAME...${NC}"
supervisorctl restart $BACKEND_NAME
sleep 3

# Проверяем статус
if supervisorctl status $BACKEND_NAME | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ Backend успешно запущен${NC}"
else
    echo -e "${RED}✗ Backend не запустился!${NC}"
    echo -e "${YELLOW}Проверьте логи: tail -50 /var/log/tyres-backend.err.log${NC}"
    
    # Предлагаем откат
    echo -e "${YELLOW}Выполнить откат к предыдущей версии? (y/n)${NC}"
    read -t 10 -n 1 rollback
    if [ "$rollback" = "y" ]; then
        echo -e "${YELLOW}Откат к backup...${NC}"
        supervisorctl stop all
        rm -rf $APP_DIR
        cp -r $BACKUP_DIR $APP_DIR
        supervisorctl start all
        echo -e "${GREEN}✓ Откат выполнен${NC}"
        exit 1
    fi
fi
echo ""

echo -e "${BLUE}[8/9] Проверка работоспособности...${NC}"

# Проверяем что backend отвечает
sleep 2
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend API работает${NC}"
else
    echo -e "${YELLOW}⚠ Backend API не отвечает (возможно еще запускается)${NC}"
fi

# Проверяем Telegram бота
if tail -20 /var/log/tyres-backend.err.log | grep -q "Telegram bot polling started successfully"; then
    echo -e "${GREEN}✓ Telegram бот запущен${NC}"
else
    echo -e "${YELLOW}⚠ Telegram бот возможно не запустился${NC}"
fi

# Проверяем новые endpoints
if curl -s http://localhost:8001/api/products/brands/tires | grep -q "success"; then
    BRANDS_COUNT=$(curl -s http://localhost:8001/api/products/brands/tires | grep -o '"total":[0-9]*' | cut -d: -f2)
    echo -e "${GREEN}✓ Новые endpoints работают (брендов: $BRANDS_COUNT)${NC}"
else
    echo -e "${YELLOW}⚠ Новые endpoints не отвечают${NC}"
fi
echo ""

echo -e "${BLUE}[9/9] Финальная проверка...${NC}"
supervisorctl status

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  Обновление завершено!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${YELLOW}Информация:${NC}"
echo -e "  Backup: ${BACKUP_DIR}"
echo -e "  Логи backend: tail -f /var/log/tyres-backend.err.log"
echo -e "  Статус: supervisorctl status"
echo ""
echo -e "${YELLOW}Проверьте работу приложения:${NC}"
echo -e "  1. Откройте Telegram бот: @shoptyresbot"
echo -e "  2. Отправьте /start"
echo -e "  3. Проверьте меню 'Шиномонтаж'"
echo -e "  4. Проверьте работу поиска шин"
echo ""
echo -e "${BLUE}Если что-то не работает:${NC}"
echo -e "  Откат: sudo rm -rf $APP_DIR && sudo cp -r $BACKUP_DIR $APP_DIR"
echo -e "  Затем: sudo supervisorctl restart all"
echo ""
