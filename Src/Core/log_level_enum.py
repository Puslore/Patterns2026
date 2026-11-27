from enum import Enum


class log_level_enum(Enum):
    """
    Перечисление уровней сообщений логирования.
    """

    # Информационное сообщение
    INFO = "INFO"

    # Сообщение об ошибке
    ERROR = "ERROR"

    # Отладочное сообщение
    DEBUG = "DEBUG"

    @classmethod
    def from_value(cls, value: object) -> "log_level_enum":
        """
        Преобразовать строковое значение в log_level_enum.
        """
        if isinstance(value, cls):
            return value

        if value is None:
            return cls.INFO

        val_str = str(value).strip().upper()
        if val_str in ("INFO", "INFORMATION"):
            return cls.INFO
        if val_str in ("ERROR", "ERR", "EXCEPTION"):
            return cls.ERROR
        if val_str in ("DEBUG", "DBG"):
            return cls.DEBUG

        return cls.INFO
