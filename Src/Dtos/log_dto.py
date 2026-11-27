from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator
from Src.Models.log_model import log_model


class log_dto(abstract_dto):
    """
    DTO модель для передачи и сериализации данных записи лога.
    """

    # Уникальный код записи
    __unique_code: str = ""

    # Период записи в строковом представлении
    __period: str = ""

    # Название подсистемы
    __subsystem: str = ""

    # Уровень сообщения (INFO, ERROR, DEBUG)
    __level: str = ""

    # Текст сообщения
    __message: str = ""

    @property
    def unique_code(self) -> str:
        """
        Уникальный код записи лога.
        """
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = str(value).strip() if value is not None else ""

    @property
    def period(self) -> str:
        """
        Период формирования записи в строковом формате.
        """
        return self.__period

    @period.setter
    def period(self, value: str) -> None:
        self.__period = str(value).strip() if value is not None else ""

    @property
    def subsystem(self) -> str:
        """
        Название подсистемы.
        """
        return self.__subsystem

    @subsystem.setter
    def subsystem(self, value: str) -> None:
        self.__subsystem = str(value).strip() if value is not None else ""

    @property
    def level(self) -> str:
        """
        Уровень сообщения.
        """
        return self.__level

    @level.setter
    def level(self, value: str) -> None:
        self.__level = str(value).strip() if value is not None else ""

    @property
    def message(self) -> str:
        """
        Текст сообщения.
        """
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = str(value).strip() if value is not None else ""

    def from_domain_model(self, source: log_model) -> "log_dto":
        """
        Фабричный метод формирования DTO из доменной модели лога.
        """
        validator.validate(source, log_model)
        dto = log_dto()
        dto.unique_code = source.unique_code
        dto.period = source.period.strftime("%Y-%m-%d %H:%M:%S") if source.period else ""
        dto.subsystem = source.subsystem
        dto.level = source.level
        dto.message = source.message
        return dto

    def mapping(self, cache: dict) -> log_model:
        """
        Сконвертировать DTO в доменную модель лога.
        """
        super().mapping(cache)
        domain = log_model()
        if self.unique_code:
            domain.unique_code = self.unique_code
        if self.period:
            domain.period = self.period
        domain.subsystem = self.subsystem
        domain.level = self.level
        domain.message = self.message
        cache[domain.unique_code] = domain
        return domain

    def from_dict(self, source: dict) -> "log_dto":
        """
        Заполнить DTO данными из словаря.
        """
        validator.validate(source, dict)
        dto = log_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.period = self.try_get_value("period", source)
        dto.subsystem = self.try_get_value("subsystem", source)
        dto.level = self.try_get_value("level", source)
        dto.message = self.try_get_value("message", source)
        return dto
