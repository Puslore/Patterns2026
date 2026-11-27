from datetime import datetime
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator, argument_exception
from Src.Core.log_level_enum import log_level_enum


class log_model(abstact_model):
    """
    Доменная модель записи журнала логирования.
    """

    # Период формирования записи лога
    __period: datetime = None

    # Название подсистемы, сформировавшей запись
    __subsystem: str = ""

    # Уровень сообщения (INFO, ERROR, DEBUG)
    __level: str = log_level_enum.INFO.value

    # Текст сообщения лога
    __message: str = ""

    def __init__(self):
        """
        Инициализировать модель записи лога значениями по умолчанию.
        """
        super().__init__()
        self.__period = datetime.now()
        self.__subsystem = ""
        self.__level = log_level_enum.INFO.value
        self.__message = ""

    @property
    def period(self) -> datetime:
        """
        Период формирования записи.
        """
        return self.__period

    @period.setter
    def period(self, value: object) -> None:
        """
        Установить период формирования записи.
        """
        if isinstance(value, datetime):
            self.__period = value
            return

        if isinstance(value, str):
            text = value.strip()
            try:
                self.__period = datetime.fromisoformat(text)
                return
            except ValueError:
                pass
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
                try:
                    self.__period = datetime.strptime(text, fmt)
                    return
                except ValueError:
                    continue

        raise argument_exception(f"Некорректный формат даты периода: {value}")

    @property
    def subsystem(self) -> str:
        """
        Название подсистемы.
        """
        return self.__subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        """
        Установить название подсистемы.
        """
        validator.validate(value, str)
        self.__subsystem = value.strip()

    @property
    def level(self) -> str:
        """
        Тип (уровень) сообщения: INFO, ERROR, DEBUG.
        """
        return self.__level

    @level.setter
    def level(self, value: object) -> None:
        """
        Установить уровень сообщения.
        """
        if isinstance(value, log_level_enum):
            self.__level = value.value
            return

        validator.validate(value, str)
        self.__level = log_level_enum.from_value(value).value

    @property
    def message(self) -> str:
        """
        Текст сообщения.
        """
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        """
        Установить текст сообщения.
        """
        validator.validate(value, str)
        self.__message = value.strip()

    @staticmethod
    def create(subsystem: str, level: object, message: str) -> "log_model":
        """
        Фабричный метод создания записи лога.
        """
        item = log_model()
        item.period = datetime.now()
        item.subsystem = subsystem
        item.level = level
        item.message = message
        return item
