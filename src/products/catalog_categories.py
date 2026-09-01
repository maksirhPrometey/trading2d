from dataclasses import dataclass, field

from django.utils.translation import gettext as _, gettext_noop

from src.products.models import Category


@dataclass
class CategoryNavGroup:
    label: str
    panel_id: str
    categories: list = field(default_factory=list)


ROOT_RULES = (
    (gettext_noop('Сад і город'), (
        'газонокос', 'ланцюгов', 'кущор', 'тример', 'сокир', 'подрібню',
        'мотокос', 'культиватор', 'дровокол', 'садов', 'ножиц', 'мультифунк',
        'мініпил', 'секатор', 'деревин',
    )),
    (gettext_noop('Генератори та енергія'), (
        'генератор', 'інвертор', 'дизель', 'електростан', 'станці', 'сонячн',
        'балконн', 'ats', 'розподільч', 'портативн', 'потужн', 'живлення',
    )),
    (gettext_noop('Акумулятори та зарядка'), (
        'акумулятор', 'зарядн', 'батаре', 'швидкого заряд',
    )),
    (gettext_noop('Інструменти'), (
        'шурупокрут', 'компресор', 'мийк', 'мотопомп', 'ручн', 'пилосос',
        'акумуляторні інструменти',
    )),
    (gettext_noop('Авто'), (
        'автомобіл', 'пусков',
    )),
    (gettext_noop('Аксесуари'), (
        'аксесуар', 'шини та ланцюг', 'комплектуюч',
    )),
)


def _slugify_panel_id(label: str) -> str:
    return label.lower().replace(' ', '-').replace('і', 'i')


def _match_root(name: str) -> str | None:
    lowered = name.lower()
    for label, keywords in ROOT_RULES:
        if any(keyword in lowered for keyword in keywords):
            return label
    return None


def _attach_children(categories):
    children_map = {}
    for category in categories:
        children_map.setdefault(category.parent_id, []).append(category)

    for category in categories:
        category.child_categories = sorted(
            children_map.get(category.pk, []),
            key=lambda item: item.name.lower(),
        )

    roots = sorted(children_map.get(None, []), key=lambda item: item.name.lower())
    return roots


def _build_virtual_groups(categories):
    grouped = {label: [] for label, _keywords in ROOT_RULES}
    grouped['Інше'] = []

    for category in sorted(categories, key=lambda item: item.name.lower()):
        root_label = _match_root(category.name) or 'Інше'
        grouped[root_label].append(category)

    nav_groups = []
    for label, _keywords in ROOT_RULES:
        items = grouped[label]
        if items:
            nav_groups.append(CategoryNavGroup(
                label=_(label),
                panel_id=_slugify_panel_id(label),
                categories=items,
            ))

    if grouped['Інше']:
        nav_groups.append(CategoryNavGroup(
            label=_('Інше'),
            panel_id='inshe',
            categories=grouped['Інше'],
        ))

    return nav_groups


def build_catalog_navigation(categories_queryset):
    categories = list(categories_queryset)
    has_hierarchy = any(category.parent_id for category in categories)

    if has_hierarchy:
        roots = _attach_children(categories)
        nav_groups = [
            CategoryNavGroup(
                label=root.loc('name'),
                panel_id=f'category-{root.pk}',
                categories=root.child_categories or [root],
            )
            for root in roots
        ]
        return nav_groups, 'hierarchy'

    return _build_virtual_groups(categories), 'virtual'


def resolve_active_nav_group(nav_groups, active_category):
    if not active_category:
        return nav_groups[0].panel_id if nav_groups else ''

    for group in nav_groups:
        if any(category.pk == active_category.pk for category in group.categories):
            return group.panel_id

    if active_category.parent_id:
        for group in nav_groups:
            if group.panel_id == f'category-{active_category.parent_id}':
                return group.panel_id

    return nav_groups[0].panel_id if nav_groups else ''
