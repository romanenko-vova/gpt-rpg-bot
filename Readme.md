# GPT RPG Bot

Telegram-бот на [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) для RPG-игры с GPT.

## Быстрый старт

### 1. Создай виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 2. Создай файл `.env`

В корне проекта добавь переменные окружения:

```env
TOKEN=твой_токен_от_BotFather
```

> Токен берётся у [@BotFather](https://t.me/BotFather) в Telegram.

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Запусти бота

```bash
python main.py
```

## Форматирование кода (Ruff)

Перед коммитом и после работы с файлом — обязательно отформатируй код.

| Действие | Как |
|----------|-----|
| Форматировать текущий файл | `Alt + Shift + F` |
| Исправить автофиксы | `Ctrl + Shift + P` → **Ruff: Fix all autofixable problems** |
| Отсортировать импорты | `Ctrl + Shift + P` → **Ruff: Format imports** |
