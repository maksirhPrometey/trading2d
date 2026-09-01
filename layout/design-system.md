# TRADING 2D – Design System

## 📋 Структура проекту

```
layout/
├── css/
│   ├── variables.css       – Змінні кольорів, типографії, spacing
│   ├── reset.css           – Нормалізація та базові стилі
│   ├── typography.css      – Система заголовків та тексту
│   ├── components.css      – Кнопки, картки, форми, іконки
│   ├── layout.css          – Контейнер, сітка, шапка, подвал
│   └── responsive.css      – Мобільна адаптація та iOS Safari
├── html/
│   ├── base.html           – Базовий шаблон Django
│   ├── header.html         – Компонент шапки з мобільним меню
│   ├── footer.html         – Компонент подвалу
│   ├── home.html           – Головна сторінка
│   ├── catalog.html        – Каталог товарів (планується)
│   ├── product.html        – Картка товару (планується)
│   └── checkout.html       – Оформлення замовлення (планується)
└── design-system.md        – Цей файл
```

---

## 🎨 Колірна палітра

### Монохром (базова)
| Назва | Змінна | Hex | Завдання |
|-------|--------|-----|----------|
| White | `--color-white` | `#FFFFFF` | Фон кнопок, текст на темному |
| Background | `--color-bg` | `#FAFAFA` | Основний фон сайту |
| Background Alt | `--color-bg-alt` | `#F5F5F0` | Альтернативний фон блоків |
| Text Dark | `--color-text-dark` | `#1A1A1A` | Глибокий чорний для основного тексту |
| Text Primary | `--color-text-primary` | `#222222` | Основний колір тексту |
| Text Secondary | `--color-text-secondary` | `#666666` | Вторинний текст |
| Text Light | `--color-text-light` | `#999999` | Легкий текст, підказки |
| Border | `--color-border` | `#E0E0E0` | Лінії картки |
| Border Dark | `--color-border-dark` | `#CCCCCC` | Темніші лінії |

### Акцент (преміум бронза/золото)
| Назва | Змінна | Hex | Завдання |
|-------|--------|-----|----------|
| Accent | `--color-accent` | `#C5A059` | Кнопки, посилання, акценти |
| Accent Hover | `--color-accent-hover` | `#B8933D` | Навіс на кнопках |
| Accent Light | `--color-accent-light` | `#D4B896` | Легкий фон для бейджів |

### Статус
| Назва | Змінна | Hex | Завдання |
|-------|--------|-----|----------|
| Success | `--color-success` | `#2E7D32` | Успішні дії, в наявності |
| Error | `--color-error` | `#C62828` | Помилки, недоступно |
| Warning | `--color-warning` | `#F57C00` | Попередження |
| Info | `--color-info` | `#1565C0` | Інформаційні повідомлення |

---

## 🔤 Типографія

### Сім'ї шрифтів
- **Serif (заголовки)**: `Playfair Display`, `Cinzel`, `Merriweather` – класичні, премальні
- **Sans-serif (тіло)**: `Lato`, `Montserrat`, `Open Sans` – сучасні, читабельні

### Масштаб шрифтів

| Клас | Розмір | Використання |
|------|--------|--------------|
| H1 | 48px (3rem) | Основні заголовки сторінок |
| H2 | 36px (2.25rem) | Заголовки розділів |
| H3 | 30px (1.875rem) | Підзаголовки |
| H4 | 24px (1.5rem) | Подальші підзаголовки |
| H5 | 20px (1.25rem) | Назви товарів |
| H6 | 18px (1.125rem) | Малі заголовки |
| Body | 16px (1rem) | Основний текст |
| Small | 14px (0.875rem) | Вторинний текст |
| XS | 12px (0.75rem) | Ярлики, підказки |

### Вага шрифту
| Назва | Значення | Використання |
|-------|----------|--------------|
| Light | 300 | Декоративні елементи |
| Regular | 400 | Основний текст, тіло |
| Medium | 500 | Виділені елементи |
| Semibold | 600 | Напівжирні заголовки |
| Bold | 700 | Жирні заголовки |

### Висота рядка (Line Height)
- **Tight** (1.2): Компактні заголовки
- **Normal** (1.5): Стандартний текст
- **Relaxed** (1.75): Довгі текстові блоки

---

## 🧩 Компоненти

### Кнопки

#### Типи

1. **Primary Button** (`.btn-primary`)
   - Фон: `--color-accent`
   - Колір: білий
   - Завдання: Основні дії (купити, відправити)

2. **Secondary Button** (`.btn-secondary`)
   - Фон: прозорий
   - Рамка: `--color-text-primary`
   - Завдання: Вторинні дії

3. **Ghost Button** (`.btn-ghost`)
   - Фон: прозорий
   - Рамка: `--color-accent`
   - Завдання: Дії на вторинному плані (додати в обране)

4. **Dark Button** (`.btn-dark`)
   - Фон: `--color-text-primary`
   - Колір: білий
   - Завдання: Контрастні дії

#### Розміри
- **Small** (`.btn-sm`): 12px × 16px × 8px
- **Base** (стандартно): 16px × 32px × 16px
- **Large** (`.btn-lg`): 18px × 64px × 32px

#### Приклад HTML
```html
<button class="btn btn-primary">Додати в кошик</button>
<button class="btn btn-ghost">Обране</button>
<a href="/catalog/" class="btn btn-secondary btn-lg">Перейти</a>
```

### Картки товарів (`.card-product`)

Структура:
```html
<article class="card card-product">
  <img class="card-product-image" src="..." alt="...">
  <div class="card-body">
    <h5 class="card-product-name">Назва товару</h5>
    <div class="card-product-price">
      <span class="card-product-price-old">1500 грн</span>
      <span>1200 грн</span>
    </div>
    <p class="card-product-info">
      <span class="badge badge-success">В наявності</span>
    </p>
  </div>
  <div class="card-product-actions">
    <button class="btn btn-primary flex-1">До кошика</button>
    <button class="btn btn-ghost flex-1">❤️</button>
  </div>
</article>
```

**Особливості:**
- Рамка: 1px solid `--color-border`
- При наведенні: рамка темніє, тінь з'являється
- Зображення: квадратна форма (aspect-ratio 1:1), заокруглені кути
- Дисконт: бейдж у верхньому кутку зображення

### Форми

#### Input
```html
<div class="form-group">
  <label class="form-label">Email</label>
  <input type="email" class="form-input" placeholder="your@email.com">
</div>
```

**Особливості:**
- Рамка: 1px solid `--color-border`
- Фокус: рамка змінює колір на `--color-accent`, з'являється легкий фон
- Padding: 16px (для мобільної зручності)
- Шрифт: 16px (запобігає зумуванню на iOS)

#### Checkbox/Radio
```html
<div class="form-checkbox-item">
  <input type="checkbox" class="form-checkbox" id="terms">
  <label for="terms">Я погоджуюсь з умовами</label>
</div>
```

### Бейджи

```html
<span class="badge badge-accent">-25%</span>
<span class="badge badge-success">В наявності</span>
<span class="badge badge-error">Недоступно</span>
```

### Іконки

Усі іконки — **лінійні** (контурні), без заливки:

```html
<button class="btn-icon">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
    <!-- SVG path -->
  </svg>
</button>
```

**Властивості:**
- Stroke-width: 1-1.5px (тонкі лінії)
- Заливка: `none`
- Колір: спадкує від контейнера
- Розміри: 16px (small), 24px (base), 32px (large)

---

## 📐 Сітка та макет

### Container
```css
.container        /* max-width: 1200px (desktop) */
.container-sm     /* max-width: 800px */
.container-lg     /* max-width: 1400px */
.container-fluid  /* 100% width */
```

### Grid System

#### Fixed columns
```html
<div class="grid grid-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <div>Item 4</div>
</div>
```

#### Auto-responsive
```html
<div class="grid grid-auto">
  <!-- Автоматично перелаштовується: 280px min-width per item -->
</div>
```

#### Брейкпойнти
| Назва | Ширина | Додаток |
|-------|--------|---------|
| Desktop | > 1200px | 4-6 колон |
| Tablet | 768-1199px | 2-3 колони |
| Mobile | < 768px | 1-2 колони |
| Small Mobile | < 480px | 1 колона |

### Flexbox Utilities
```html
<div class="flex flex-between">         <!-- space-between -->
<div class="flex flex-center">          <!-- center align -->
<div class="flex flex-gap-lg">          <!-- gap: 24px -->
<div class="flex flex-wrap">            <!-- flex-wrap -->
```

### Spacing (Margins & Padding)

```css
--sp-xs: 4px    /* .mt-xs, .mb-xs, .px-xs, .py-xs */
--sp-sm: 8px    /* .mt-sm, .mb-sm, .px-sm, .py-sm */
--sp-md: 16px   /* .mt-md, .mb-md, .px-md, .py-md */
--sp-lg: 24px   /* .mt-lg, .mb-lg, .px-lg, .py-lg */
--sp-xl: 32px   /* .mt-xl, .mb-xl */
--sp-2xl: 48px
--sp-3xl: 64px
```

Приклад:
```html
<section class="section">              <!-- padding: 48px 0 -->
  <div class="container">
    <h2 class="mb-lg">Заголовок</h2>   <!-- margin-bottom: 24px -->
  </div>
</section>
```

---

## 📱 Мобільна адаптація

### Основні принципи

1. **Mobile-first approach** – CSS спочатку для мобільної, потім медіа-запити для більших
2. **Єдина колірна палітра** – одна система кольорів для всіх пристроїв
3. **Адаптивна типографія** – шрифти масштабуються плавно
4. **iOS Safari дружба** – спеціальні фікси для iPhone/iPad

### Брейкпойнти
```css
@media (max-width: 1200px)   /* Планшет горизонтально */
@media (max-width: 768px)    /* Планшет вертикально */
@media (max-width: 480px)    /* Мобільний */
```

### Мобільні адаптації

**Сітка товарів:**
- Desktop: 4 колони → Tablet: 2 колони → Mobile: 1 колона

**Шапка:**
- Desktop: повна з логотипом, пошуком, іконками
- Mobile: логотип + іконки, пошук у меню

**Меню:**
- Mobile: кнопка меню (гамбургер) → спливаюче меню

**Форми:**
- Input: 16px шрифт (запобігає зумуванню iOS)
- Кнопка: мінімум 44px × 44px (для зручного натиснення)

### iOS Safari Фікси

1. **Запобіжки зумуванню:**
   ```css
   input, button, select, textarea {
     font-size: 16px; /* > 16px не зумує */
   }
   ```

2. **Safe Area Insets:**
   ```css
   @supports (padding: max(0px)) {
     body {
       padding-left: max(0, env(safe-area-inset-left));
       padding-right: max(0, env(safe-area-inset-right));
     }
   }
   ```

3. **Прибрати стандартні стилі:**
   ```css
   input, button, select {
     -webkit-appearance: none;
     appearance: none;
   }
   ```

4. **Rubber band effect:**
   ```css
   body {
     overscroll-behavior-y: none;
   }
   ```

---

## ⚙️ Використання CSS змінних

Усі значення — змінні, легко змінювати в `variables.css`:

```css
/* Змінювання кольорів */
:root {
  --color-accent: #C5A059;        /* Основний колір */
  --color-text-primary: #222222;   /* Текст */
  --color-bg: #FAFAFA;             /* Фон */
}

/* Використання в компонентах */
.btn-primary {
  background-color: var(--color-accent);
  color: var(--color-white);
}

.card {
  border: var(--border-thin) solid var(--color-border);
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-md);
}
```

---

## 🔗 Інтеграція з Django

### Структура папок
```
project/
├── layout/                 (цей каталог)
├── src/core/static/
│   ├── css/               (копіювати з layout/css/)
│   ├── js/
│   └── images/
└── templates/
    ├── base.html          (копіювати з layout/html/base.html)
    └── components/
        ├── header.html    (з layout/html/)
        └── footer.html    (з layout/html/)
```

### В Django шаблоні
```django
{% load static %}

<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="{% static 'css/variables.css' %}">
  <link rel="stylesheet" href="{% static 'css/reset.css' %}">
  <link rel="stylesheet" href="{% static 'css/typography.css' %}">
  <link rel="stylesheet" href="{% static 'css/components.css' %}">
  <link rel="stylesheet" href="{% static 'css/layout.css' %}">
  <link rel="stylesheet" href="{% static 'css/responsive.css' %}">
</head>
<body>
  {% include 'components/header.html' %}
  {% block content %}{% endblock %}
  {% include 'components/footer.html' %}
</body>
</html>
```

---

## 📋 Чек-лист для реалізації

- [ ] Копіювати CSS файли в `src/core/static/css/`
- [ ] Копіювати HTML компоненти в `templates/components/`
- [ ] Налаштувати Django `STATIC_URL` та `STATIC_ROOT`
- [ ] Запустити `python manage.py collectstatic`
- [ ] Протестувати на мобільному (iOS Safari, Chrome)
- [ ] Перевірити Lighthouse performance score
- [ ] Налаштувати шрифти (Google Fonts CDN)
- [ ] Додати favicon та метатеги
- [ ] Настроїти SEO метатеги в base.html

---

## 📝 Примітки

- **Немає !important** – все будується на специфічності
- **БЕМ-подібна система** – логічна назва класів (`.card-product`, `.btn-primary`)
- **CSS змінні** – легко змінювати дизайн без редагування кожного класу
- **Доступність** – використовуються semantic HTML та aria атрибути
- **Performance** – мінімум CSS, оптимізовано для мобільної
- **iOS Safari** – спеціальні фікси для коректного відображення на iPhone/iPad

---

**Остання оновлення:** 26 серпня 2024

Готово до використання! 🚀
