# 📦 Инструкция по загрузке в GitHub

## Шаг 1: Создайте репозиторий на GitHub

1. Перейдите на https://github.com
2. Нажмите кнопку **"New repository"**
3. Заполните:
   - **Repository name**: `tyres-shop` (или любое другое имя)
   - **Description**: Telegram Mini App для продажи шин и дисков
   - **Visibility**: Private (рекомендуется) или Public
   - ❌ **НЕ** создавайте README, .gitignore, license (у нас уже есть)
4. Нажмите **"Create repository"**

## Шаг 2: Загрузите проект в GitHub

### Из директории `/app` на вашем текущем сервере:

```bash
cd /app

# Инициализируем git (если еще не инициализирован)
git init

# Добавляем все файлы
git add .

# Делаем первый коммит
git commit -m "Initial commit: Telegram Mini App - Tyres Shop"

# Добавляем remote (замените YOUR-USERNAME и YOUR-REPO на ваши)
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git

# Переименовываем ветку в main (если нужно)
git branch -M main

# Пушим в GitHub
git push -u origin main
```

**Пример с реальными данными:**
```bash
cd /app
git init
git add .
git commit -m "Initial commit: Telegram Mini App - Tyres Shop"
git remote add origin https://github.com/username/tyres-shop.git
git branch -M main
git push -u origin main
```

### Если GitHub запрашивает аутентификацию:

#### Вариант 1: Personal Access Token (рекомендуется)

1. Перейдите в GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Дайте имя: `tyres-shop-deployment`
4. Выберите срок действия: 90 days (или No expiration)
5. Выберите scope: **repo** (полный доступ к приватным репозиториям)
6. Нажмите **"Generate token"**
7. **СКОПИРУЙТЕ ТОКЕН** (он больше не появится!)

Используйте токен вместо пароля:
```bash
git push -u origin main
# Username: ваш-username
# Password: вставьте-скопированный-токен
```

#### Вариант 2: SSH ключ

```bash
# Генерация SSH ключа
ssh-keygen -t ed25519 -C "your-email@example.com"

# Копирование публичного ключа
cat ~/.ssh/id_ed25519.pub

# Добавьте ключ в GitHub:
# Settings → SSH and GPG keys → New SSH key
# Вставьте содержимое публичного ключа

# Измените remote на SSH
git remote set-url origin git@github.com:YOUR-USERNAME/YOUR-REPO.git

# Пуш
git push -u origin main
```

## Шаг 3: Проверьте что всё загрузилось

Откройте https://github.com/YOUR-USERNAME/YOUR-REPO

Должны быть видны все файлы:
```
├── backend/
├── frontend/
├── README.md
├── DEPLOYMENT.md
├── QUICK_INSTALL.md
├── TEST_COMMANDS.md
├── install.sh
└── .gitignore
```

## Шаг 4: Настройте .env файлы в .gitignore (проверка)

Убедитесь что `.env` файлы НЕ попали в GitHub:

```bash
# Проверяем что .gitignore работает
git status

# Если видите .env в списке файлов - удалите их из git
git rm --cached backend/.env
git rm --cached frontend/.env
git commit -m "Remove .env files from tracking"
git push
```

## Шаг 5: Добавьте README для GitHub

Создайте красивое README для GitHub (опционально):

```bash
cd /app

cat > GITHUB_README.md << 'EOF'
# 🚗 Telegram Mini App - Магазин Шин и Дисков

Полнофункциональное Telegram Mini App для продажи шин и дисков с интеграцией API поставщика 4tochki.ru

## ⚡ Быстрая установка

```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh
chmod +x install.sh
sudo bash install.sh
```

## 🎯 Возможности

- 🔍 Поиск шин и дисков по параметрам
- 🚗 Подбор по автомобилю
- 🛒 Корзина и оформление заказа
- ✅ Система подтверждения заказов админом
- 📱 Telegram уведомления
- 📊 Админ-панель с статистикой
- 💰 Динамическая наценка

## 📚 Документация

- [Быстрая установка](QUICK_INSTALL.md)
- [Полная инструкция деплоя](DEPLOYMENT.md)
- [Команды для тестирования](TEST_COMMANDS.md)

## 🏗️ Технологии

**Backend:** FastAPI, MongoDB, SOAP (Zeep), python-telegram-bot  
**Frontend:** React, TailwindCSS, Telegram WebApp SDK

## 📞 Поддержка

При возникновении проблем создайте Issue в этом репозитории.

## 📝 Лицензия

Proprietary
EOF

# Коммитим
git add GITHUB_README.md
git commit -m "Add GitHub README"
git push
```

## Шаг 6: Установка на новом сервере

Теперь на любом новом сервере можно установить одной командой:

```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh
chmod +x install.sh
sudo bash install.sh
```

Скрипт запросит все необходимые параметры и автоматически развернет приложение!

## 🔒 Безопасность

### Что НЕ должно попасть в GitHub:

❌ `.env` файлы  
❌ `node_modules/`  
❌ Логи  
❌ Базы данных  
❌ SSL сертификаты  
❌ Пароли и токены  

### Что должно быть в GitHub:

✅ Исходный код  
✅ `requirements.txt` и `package.json`  
✅ Конфигурационные файлы (без секретов)  
✅ Документация  
✅ Скрипты установки  
✅ `.gitignore`  

## 📊 GitHub Actions (опционально)

Можно настроить автоматический деплой при push:

Создайте `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /app
            git pull
            sudo supervisorctl restart all
```

Добавьте секреты в GitHub:
- Settings → Secrets and variables → Actions
- Добавьте: `SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`

## 🎉 Готово!

Теперь:
1. ✅ Проект загружен в GitHub
2. ✅ Скрипт автоматической установки готов
3. ✅ Можно развернуть на любом сервере одной командой
4. ✅ Документация доступна всем

### Ссылка для быстрой установки:

```
https://github.com/YOUR-USERNAME/YOUR-REPO
```

Команда для установки:
```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/YOUR-REPO/main/install.sh && chmod +x install.sh && sudo bash install.sh
```

---

**Успешного деплоя! 🚀**
