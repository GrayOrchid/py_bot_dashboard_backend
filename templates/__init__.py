from .mail_templates_ru import OTP_SUBJECT as SUBJECT_RU, OTP_TEXT_TEMPLATE as TEMPLATE_RU
from .mail_templates_eng import OTP_SUBJECT as SUBJECT_EN, OTP_TEXT_TEMPLATE as TEMPLATE_EN

MAIL_TEMPLATES = {
    "ru": {
        "subject": SUBJECT_RU,
        "template": TEMPLATE_RU
    },
    "en": {
        "subject": SUBJECT_EN,
        "template": TEMPLATE_EN
    }
}

__all__ = ["MAIL_TEMPLATES"]