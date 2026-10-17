from enum import Enum

from Src.Core.validator import argument_exception


class response_format_enum(Enum):
    CSV = "CSV"
    MARKDOWN = "Markdown"
    XML = "XML"
    TXT = "TXT"
    HTML = "HTML"

    @classmethod
    def from_value(cls, value):
        """Найти формат без учета регистра или сообщить о неизвестном значении."""
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise argument_exception("Формат отчета должен быть строкой")

        formats = {item.value.casefold(): item for item in cls}
        result = formats.get(value.strip().casefold())
        if result is None:
            raise argument_exception(f"Неизвестный формат отчета: {value}")
        return result
