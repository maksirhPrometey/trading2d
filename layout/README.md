# TRADING 2D – Layout & Design System

Повна система дизайну для інтернет-магазину, побудована на принципах монохрому + преміум акцент, з готовністю до мобільної адаптації та iOS Safari.

## 📦 Вміст

```
layout/
├── css/                      # Стилі (модульна система)
│   ├── variables.css         # CSS змінні (кольори, шрифти, spacing)
│   ├── reset.css             # Нормалізація браузера
│   ├── typography.css        # Система шрифтів та заголовків
│   ├── components.css        # Кнопки, картки, форми
│   ├── layout.css            # Сітка, шапка, подвал
│   └── responsive.css        # Мобільна адаптація + iOS Safari
├── html/                     # HTML компоненти для Django
│   ├── base.html             # Базовий шаблон
│   ├── header.html           # Шапка з мобільним меню
│   ├── footer.html           # Подвал
│   └── home.html             # Головна сторінка (приклад)
├── components-demo.html      # Демо-сторінка всіх компонентів
├── design-system.md          # Повна документація дизайн-системи
└── INTEGRATION_GUIDE.md      # Інструкція по інтеграції в Django
```

## 🎨 Дизайн принципи

### Палітра
- **Основа**: Монохром (білий, сірий, чорний)
- **Акцент**: Преміум золото/бронза (#C5A059)
- **Фон**: М'який бежевий (#FAFAFA) замість білого
- **Текст**: Темно-графітовий (#1A1A1A)

### Типографія
- **Заголовки**: Serif (Playfair Display, Cinzel) – класичні
- **Тіло**: Sans-serif (Lato, Montserrat) – сучасні

### Компоненти
- **Кнопки**: Прямокутні, мінімалізм, 4 типи (Primary, Secondary, Ghost, Dark)
- **Картки**: Тонкі лінії замість тіней, 1px border
- **Іконки**: Лінійні (контурні), не залиті
- **Форми**: Великі таргети (44px), безопасні для мобільної

## 🚀 Швидкий старт

### 1. Копіювання файлів
```bash
# CSS
cp layout/css/* src/core/static/css/

# HTML компоненти
cp layout/html/header.html templates/components/
cp layout/html/footer.html templates/components/
```

### 2. Оновлення Django base.html
Див. `INTEGRATION_GUIDE.md` за детальними інструкціями.

### 3. Запуск
```bash
python manage.py collectstatic
python manage.py runserver
```

**Детальнішу інструкцію див. в файлі `INTEGRATION_GUIDE.md`**

## 📱 Адаптація

### Брейкпойнти
- **Desktop**: > 1200px (4 колони)
- **Tablet**: 768-1199px (2-3 колони)
- **Mobile**: < 768px (1-2 колони)
- **Small Mobile**: < 480px (1 колона)

### iOS Safari фікси
- Запобіжка зумуванню на focus (`font-size: 16px`)
- Safe area insets (`env(safe-area-inset-*)`)
- Прибрання стандартних стилів (`-webkit-appearance: none`)
- Rubber band effect (`overscroll-behavior-y: none`)

## 🎯 Використання

### CSS змінні
Всі значення можна легко змінити в одному місці:

```css
:root {
  --color-accent: #C5A059;        /* Зміни тут */
  --color-text-primary: #222222;
  --fs-lg: 1.125rem;
}
```

### Grid система
```html
<div class="grid grid-3">        <!-- 3 колони -->
<div class="grid grid-auto">     <!-- Авто-респонсив -->
<div class="grid grid-auto-lg">  <!-- Авто з 350px мін -->
```

### Spacing
```html
<h2 class="mb-lg">Заголовок</h2>      <!-- margin-bottom: 24px -->
<section class="section">             <!-- padding: 48px 0 -->
  <div class="container">
    <div class="py-lg">               <!-- padding: 24px 0 -->
```

### Компоненти
```html
<!-- Кнопка -->
<button class="btn btn-primary">Додати в кошик</button>

<!-- Картка товару -->
<article class="card card-product">...</article>

<!-- Форма -->
<input type="email" class="form-input" placeholder="Email">

<!-- Бейдж -->
<span class="badge badge-accent">-25%</span>
```

## 📖 Документація

| Файл | Призначення |
|------|-------------|
| `design-system.md` | Повна документація дизайн-системи, параметри кожного компонента |
| `INTEGRATION_GUIDE.md` | Крок-за-кроком інструкція по інтеграції в Django |
| `components-demo.html` | Демо-сторінка з прикладами всіх компонентів |

## ✨ Особливості

✅ **Монохромний дизайн** з елегантним акцентом
✅ **CSS змінні** для легкої кастомізації
✅ **Модульна структура** – копіюй тільки те, що потрібно
✅ **Мобільна-перша** адаптація для всіх пристроїв
✅ **iOS Safari оптимізація** з безопасними zone інсетами
✅ **Доступність** – semantic HTML, aria атрибути
✅ **Performance** – мінімум CSS, без фреймворків
✅ **Готові компоненти** – кнопки, картки, форми, таблиці
✅ **Django інтеграція** – готові шаблони

## 🛠 Налаштування

### Помінювати кольори
Відредагуй `css/variables.css`:
```css
--color-accent: #NEW_COLOR;      /* Новий акцент */
--color-bg: #NEW_BG;             /* Новий фон */
--color-text-primary: #NEW_TEXT; /* Новий текст */
```

### Змінити фонти
```css
--font-serif: 'Your Font', serif;
--font-sans: 'Your Font', sans-serif;
```

### Додати контактну інформацію
Відредагуй `html/header.html` та `html/footer.html`

## 📱 Тестування

Протестувати на:
- ✅ Desktop (1920px, 1440px, 1200px)
- ✅ Tablet (768px, 1024px)
- ✅ Mobile (480px, 375px)
- ✅ iPhone (Safari, Chrome)
- ✅ Android (Chrome, Firefox)

## 🔗 Структура файлів у Django

Після інтеграції:
```
project/
├── src/core/static/
│   └── css/
│       ├── variables.css ✅
│       ├── reset.css ✅
│       ├── typography.css ✅
│       ├── components.css ✅
│       ├── layout.css ✅
│       └── responsive.css ✅
└── templates/
    ├── base.html ✅
    └── components/
        ├── header.html ✅
        └── footer.html ✅
```

## 📝 Чек-лист перед продакшеном

- [ ] CSS файли скопійовані та підключені
- [ ] HTML компоненти в `templates/components/`
- [ ] Django `STATIC_URL` та `STATIC_ROOT` налаштовані
- [ ] `collectstatic` виконаний
- [ ] Logo та favicon додані
- [ ] Meta теги в head налаштовані
- [ ] Тестування на мобільному (особливо iOS)
- [ ] Lighthouse score > 90
- [ ] Всі посилання перевірені
- [ ] Форми тестовані (особливо на мобільній)

## 💡 Підтримка та оновлення

Усе побудовано на CSS змінних, тому легко зміняти:
1. Кольори → змініть в `variables.css`
2. Типографія → змініть масштаб шрифтів
3. Spacing → змініть `--sp-*` змінні
4. Компоненти → відредагуйте відповідний CSS файл

Не потрібно переписувати весь проект!

---

**Готово до продакшену! 🚀**

Для детальної інформації дивіться `design-system.md` та `INTEGRATION_GUIDE.md`
