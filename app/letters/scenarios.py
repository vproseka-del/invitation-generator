from pathlib import Path

SCENARIOS = {
    "university": {
        "title": "Приглашение вуза или партнёра к участию в опросе",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "university",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "ministry": {
        "title": "Обращение в министерство",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "ministry",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "regional_authority": {
        "title": "Обращение к региональному органу власти",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "regional_authority",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "partner": {
        "title": "Приглашение партнёра",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "partner",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "sponsor": {
        "title": "Приглашение спонсора",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "sponsor",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "media": {
        "title": "Приглашение СМИ",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "media",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "cultural_leader": {
        "title": "Приглашение деятеля культуры",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "cultural_leader",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
    "youth_organization": {
        "title": "Приглашение молодёжной организации",
        "template_file": Path(__file__).parent / "content" / "university.txt",
        "project_id": "fiziki_i_liriki",
        "recipient_category": "youth_organization",
        "fields": {
            "organization": "Название организации",
            "city": "Город",
            "recipient_name": "ФИО получателя",
            "recipient_position": "Должность получателя",
        },
    },
}

CATEGORY_LABELS = {
    "university": "Университет / институт",
    "ministry": "Министерство",
    "regional_authority": "Региональный орган власти",
    "youth_organization": "Молодёжная организация",
    "partner": "Партнёр проекта",
    "sponsor": "Спонсор / меценат",
    "media": "СМИ",
    "cultural_leader": "Деятель культуры",
}

LETTER_GOALS = [
    "Приглашение к участию",
    "Просьба о поддержке",
    "Предложение партнёрства",
    "Благодарственное письмо",
    "Информационное письмо",
]


def resolve_category(value):
    value = (value or "").strip()
    if value in SCENARIOS:
        return value
    for category_id, label in CATEGORY_LABELS.items():
        if value.lower() == label.lower():
            return category_id
    return None
