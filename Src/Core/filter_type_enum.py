from enum import Enum


class filter_type_enum(Enum):
    """
    Перечисление вариантов фильтрации данных
    """

    # Полное совпадение
    EQUALS = "EQUALS"

    # Вхождение строки
    LIKE = "LIKE"

    # Меньше указанного значения
    LESS = "LESS"

    # Меньше или равно указанному значению
    LESS_EQUAL = "LESS_EQUAL"

    # Больше указанного значения
    GREATER = "GREATER"

    # Больше или равно указанному значению
    GREATER_EQUAL = "GREATER_EQUAL"

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
        if val_str in ("EQUALS", "EQUAL", "EQ", "="):
            return cls.EQUALS
        if val_str in ("LIKE", "CONTAINS", "~"):
            return cls.LIKE
        if val_str in ("LESS", "LT", "<"):
            return cls.LESS
        if val_str in ("LESS_EQUAL", "LESS_OR_EQUAL", "LE", "LTE", "<="):
            return cls.LESS_EQUAL
        if val_str in ("GREATER", "GT", ">"):
            return cls.GREATER
        if val_str in ("GREATER_EQUAL", "GREATER_OR_EQUAL", "GE", "GTE", ">="):
            return cls.GREATER_EQUAL

        # По умолчанию - EQUALS
        return cls.EQUALS
