from django.shortcuts import render

from src.website.models import ContactPage, MainPage, Page


def home(request):
    main_page = MainPage.load()
    if main_page.hero_image_id:
        main_page = MainPage.objects.select_related('hero_image').get(pk=main_page.pk)
    showcase = list(
        main_page.showcase_items.select_related(
            'product',
            'product__category',
            'product__brand',
        )
        .prefetch_related('product__images')
        .order_by('order', 'pk')
    )
    bestsellers = [
        item.product
        for item in showcase
        if item.slot == item.Slot.BESTSELLER
    ]
    new_arrivals = [
        item.product
        for item in showcase
        if item.slot == item.Slot.NEW_ARRIVAL
    ]

    # banner_image — це фон усього hero-блоку (окрема сутність).
    # Фото товару праворуч (hero_image) — незалежний вибір: якщо в адмінці
    # не обрано конкретне фото з галереї, підбираємо автоматично серед
    # хітів/новинок.
    hero_product = None
    if not main_page.hero_image_id:
        for product in bestsellers + new_arrivals:
            image = product.primary_image
            if image and image.image:
                hero_product = product
                break

    return render(
        request,
        'website/home.html',
        {
            'main_page': main_page,
            'bestsellers': bestsellers,
            'new_arrivals': new_arrivals,
            'hero_product': hero_product,
        },
    )


def contact(request):
    return render(
        request,
        'website/contact.html',
        {'contact_page': ContactPage.load()},
    )


def _info_page(request, slug):
    page = Page.load(slug)
    return render(request, 'website/info_page.html', {'page': page})


def about_us(request):
    return _info_page(request, 'about')


def delivery_and_payment(request):
    return _info_page(request, 'delivery')


def privacy_policy(request):
    return _info_page(request, 'privacy')


def terms_and_conditions(request):
    return _info_page(request, 'terms')
