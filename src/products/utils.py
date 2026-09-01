from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.text import slugify

MAX_UPLOAD_SIZE_BYTES = 8 * 1024 * 1024  # 8 МБ


def validate_max_file_size(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            'Файл занадто великий (%(size)s). Максимум — %(max)s.',
            params={
                'size': filesizeformat(uploaded_file.size),
                'max': filesizeformat(MAX_UPLOAD_SIZE_BYTES),
            },
        )

_CYRILLIC_TO_LATIN = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
    'є': 'ye', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'y',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
    'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'yu', 'я': 'ya',
}


def transliterate_uk(value: str) -> str:
    result = []
    for char in value:
        lower = char.lower()
        if lower in _CYRILLIC_TO_LATIN:
            mapped = _CYRILLIC_TO_LATIN[lower]
            result.append(mapped.upper() if char.isupper() else mapped)
        else:
            result.append(char)
    return ''.join(result)


def ukrainian_slugify(value: str, fallback: str = 'product') -> str:
    transliterated = transliterate_uk(value)
    slug = slugify(transliterated, allow_unicode=False)
    return slug or fallback
