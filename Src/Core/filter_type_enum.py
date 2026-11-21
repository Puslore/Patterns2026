from enum import Enum


class filter_type_enum(Enum):
    """
    Перечисление вариантов фильтрации данных
    """

    # Полное совпадение
    EQUALS = "EQUALS"

    # Вхождение строки
    LIKE = "LIKE"

    @classmethod
    def from_value(cls, value: object) -> "filter_type_enum":
        """
        Преобразовать строковое значение в filter_type_enum.
        """
        if isinstance(value, cls):
            return value

        if value is None:
            return cls.EQUALS

        val_str = str(value).strip().upper()
        if val_str in ("EQUALS", "EQUAL", "EQ"):
            return cls.EQUALS
        if val_str in ("LIKE", "CONTAINS"):
            return cls.LIKE

        # По умолчанию - EQUALS
        return cls.EQUALS

