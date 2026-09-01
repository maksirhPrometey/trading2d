# Інструкція по інтеграції Layout в Django

## 🚀 Крок 1: Скопіювати CSS

```bash
# Перейти до папки static
cd src/core/static/

# Створити папку css (якщо не існує)
mkdir -p css

# Скопіювати CSS файли з layout
cp ../../../layout/css/*.css css/
```

**Результат:**
```
src/core/static/css/
├── variables.css
├── reset.css
├── typography.css
├── components.css
├── layout.css
└── responsive.css
```

---

## 🚀 Крок 2: Скопіювати HTML компоненти

```bash
cd templates/components/

# Скопіювати компоненти
cp ../../../layout/html/header.html .
cp ../../../layout/html/footer.html .
```

**Результат:**
```
templates/components/
├── header.html
└── footer.html
```

---

## 🚀 Крок 3: Оновити base.html

Замінити вміст `templates/base.html` на:

```django
{% load static %}
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="description" content="TRADING 2D – Інтернет-магазин">
  <meta name="theme-color" content="#FAFAFA">
  
  <title>{% block title %}TRADING 2D{% endblock %}</title>
  
  <!-- CSS -->
  <link rel="stylesheet" href="{% static 'css/variables.css' %}">
  <link rel="stylesheet" href="{% static 'css/reset.css' %}">
  <link rel="stylesheet" href="{% static 'css/typography.css' %}">
  <link rel="stylesheet" href="{% static 'css/components.css' %}">
  <link rel="stylesheet" href="{% static 'css/layout.css' %}">
  <link rel="stylesheet" href="{% static 'css/responsive.css' %}">
  
  {% block extra_css %}{% endblock %}
</head>
<body>
  <!-- Header -->
  {% include 'components/header.html' %}
  
  <!-- Main Content -->
  <main class="main">
    {% block content %}{% endblock %}
  </main>
  
  <!-- Footer -->
  {% include 'components/footer.html' %}
  
  <!-- Scripts -->
  <script src="{% static 'js/main.js' %}"></script>
  {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 🚀 Крок 4: Перевірити settings.py

```python
# settings.py

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'src/core/static'),
]
```

---

## 🚀 Крок 5: Колекціонування статичних файлів

```bash
python manage.py collectstatic --noinput
```

---

## 🚀 Крок 6: Запуск сервера

```bash
python manage.py runserver
```

Відкрити браузер: **http://localhost:8000/**

---

## ✅ Перевіркова лист

- [ ] CSS файли скопійовані в `src/core/static/css/`
- [ ] HTML компоненти в `templates/components/`
- [ ] base.html оновлений
- [ ] Django сервер запущений без помилок
- [ ] На сторінці видна шапка та подвал
- [ ] Кольори відповідають дизайну (бежевий фон, золотистий акцент)
- [ ] Шрифти завантажені (Google Fonts)
- [ ] На мобільному (480px) меню колапсується

---

## 🔧 Налаштування (опціонально)

### Помінювати кольори
Редагувати `src/core/static/css/variables.css`:

```css
:root {
  --color-accent: #NEW_COLOR;      /* Новий акцентний колір */
  --color-bg: #NEW_BG_COLOR;       /* Новий фон */
}
```

### Додати логотип
У шапці (`components/header.html`):

```html
<div class="header-logo">
  <a href="/" class="logo-link">
    <img src="{% static 'images/logo.svg' %}" alt="TRADING 2D">
  </a>
</div>
```

### Додати контактну інформацію в шапку
Відредагувати `header.html`:

```html
<div class="header-contact">
  <a href="tel:+380441234567">+38 (044) 123-45-67</a>
  <a href="mailto:info@trading2d.com">info@trading2d.com</a>
</div>
```

---

## 📦 Структура після інтеграції

```
trading2d/
├── src/
│   ├── core/
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   ├── variables.css ✅
│   │   │   │   ├── reset.css ✅
│   │   │   │   ├── typography.css ✅
│   │   │   │   ├── components.css ✅
│   │   │   │   ├── layout.css ✅
│   │   │   │   └── responsive.css ✅
│   │   │   ├── js/
│   │   │   └── images/
│   │   └── ...
│   └── ...
├── templates/
│   ├── base.html ✅
│   ├── components/
│   │   ├── header.html ✅
│   │   └── footer.html ✅
│   └── ...
├── layout/ (оригіналь для огляду)
│   ├── css/
│   ├── html/
│   └── design-system.md
└── ...
```

---

## 🎯 Наступні кроки

1. Створити сторінку каталогу (`catalog.html`)
2. Реалізувати картку товару (`product.html`)
3. Додати фільтрацію та сортування
4. Створити сторінку оформлення замовлення (`checkout.html`)
5. Налаштувати JavaScript для інтерактивних елементів
6. Протестувати на всіх пристроях (мобільний, планшет, десктоп)

---

**Готово до використання! 🚀**
