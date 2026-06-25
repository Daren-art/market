# 🛍️ MarketPlace

Полноценный маркетплейс на **FastAPI** с регистрацией пользователей, корзиной, оформлением заказов и панелью администратора.

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| 👤 Регистрация / Вход | Авторизация с хешированием паролей (bcrypt) |
| 🏠 Каталог товаров | Главная страница с карточками товаров |
| 🛒 Корзина | Добавление, удаление, подсчёт суммы |
| 📋 История заказов | Пользователь видит все свои заказы и их статусы |
| 🔐 Панель администратора | Добавление и удаление товаров, управление заказами |
| ✅ Подтверждение заказов | Админ подтверждает или отменяет заказы |

---

## 🚀 Быстрый старт

### 1. Клонируй репозиторий

```bash
git clone https://github.com/твой-юзер/marketplace.git
cd marketplace
```

### 2. Создай виртуальное окружение

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Установи зависимости

```bash
pip install -r req.txt
```

### 4. Настрой переменные окружения

Создай файл `.env` в корне проекта:

```env
ADMIN_PASSWORD=твой_пароль
SECRET_KEY=твой_секретный_ключ
```

> ⚠️ Никогда не публикуй `.env` в открытый репозиторий!

### 5. Запусти сервер

```bash
uvicorn main:app --reload
```

Открой в браузере: [http://localhost:8000](http://localhost:8000)

---

## 📁 Структура проекта

```
marketplace/
├── main.py                  # Точка входа, настройка FastAPI
├── config.py                # Загрузка переменных из .env
├── req.txt                  # Зависимости
├── .env                     # Переменные окружения (не в git!)
│
├── database/
│   ├── database.py          # Подключение к SQLite
│   └── models.py            # Модели: User, Product, CartItem, Order, OrderItem
│
├── routers/
│   ├── auth.py              # Регистрация, вход, выход
│   ├── products.py          # Главная страница, история заказов
│   ├── cart.py              # Корзина, оформление заказа
│   ├── admin.py             # Управление товарами
│   └── admin_orders.py      # Управление заказами
│
├── templates/
│   ├── base.html            # Общий шаблон с навигацией
│   ├── index.html           # Каталог товаров
│   ├── cart.html            # Корзина
│   ├── orders.html          # История заказов пользователя
│   ├── register.html        # Регистрация
│   ├── login.html           # Вход
│   ├── admin.html           # Панель: товары
│   ├── admin_orders.html    # Панель: заказы
│   └── admin_login.html     # Вход в админку
│
└── static/
    ├── css/
    │   └── style.css
    └── uploads/             # Загружаемые изображения товаров
```

---

## 🔗 Страницы

| URL | Описание |
|---|---|
| `/` | Каталог товаров |
| `/register` | Регистрация |
| `/login` | Вход |
| `/cart` | Корзина |
| `/orders` | История заказов |
| `/admin` | Панель администратора — товары |
| `/admin/orders` | Панель администратора — заказы |

---

## 🛠️ Технологии

- **[FastAPI](https://fastapi.tiangolo.com/)** — веб-фреймворк
- **[SQLAlchemy](https://www.sqlalchemy.org/)** — ORM для работы с базой данных
- **[SQLite](https://www.sqlite.org/)** — база данных
- **[Jinja2](https://jinja.palletsprojects.com/)** — HTML-шаблоны
- **[Passlib + bcrypt](https://passlib.readthedocs.io/)** — хеширование паролей
- **[Starlette Sessions](https://www.starlette.io/middleware/#sessionmiddleware)** — сессии пользователей
- **[python-dotenv](https://pypi.org/project/python-dotenv/)** — переменные окружения
