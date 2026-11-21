import datetime

from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator, argument_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.storage_model import storage_model


class transaction_model(abstact_model):
    """
    Модель складской транзакции (движение номенклатуры).

    Положительное значение означает поступление, отрицательное — списание.
    """

    __range: range_model = None
    __storage: storage_model = None
    __nomenclature: nomenclature_model = None
    __value: float = 0.0
    __period: datetime.datetime = None

    def __init__(self):
        """
        Инициализировать модель складской транзакции.
        """
        super().__init__()
        self.__range = None
        self.__storage = None
        self.__nomenclature = None
        self.__value = 0.0
        self.__period = datetime.datetime.now()

    @property
    def range(self) -> range_model:
        """
        Единица измерения транзакции.
        """
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        """
        Установить единицу измерения транзакции.
        """
        validator.validate(value, range_model)
        self.__range = value

    @property
    def storage(self) -> storage_model:
        """
        Склад транзакции.
        """
        return self.__storage

    @storage.setter
    def storage(self, value: storage_model) -> None:
        """
        Установить склад транзакции.
        """
        validator.validate(value, storage_model)
        self.__storage = value

    @property
    def nomenclature(self) -> nomenclature_model:
        """
        Номенклатура транзакции.
        """
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        """
        Установить номенклатуру транзакции.
        """
        validator.validate(value, nomenclature_model)
        self.__nomenclature = value

    @property
    def value(self) -> float:
        """
        Количество (+ поступление, - списание).
        """
        return self.__value

    @value.setter
    def value(self, source: float) -> None:
        """
        Установить ненулевое количество.
        """
        validator.validate(source, (int, float))
        result = float(source)
        if result == 0:
            raise argument_exception("Значение = 0 !")
        self.__value = result

    @property
    def period(self) -> datetime.datetime:
        """
        Дата и время совершения транзакции.
        """
        return self.__period

    @period.setter
    def period(self, value: datetime.datetime) -> None:
        """
        Установить дату и время совершения транзакции.
        """
        validator.validate(value, (datetime.datetime, datetime.date))
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.__period = datetime.datetime.combine(value, datetime.time.min)
        else:
            self.__period = value

    def get_references(self) -> list:
        """
        Получить список ссылок на связанные сущности для индекса зависимостей.
        """
        refs = []
        if self.range is not None:
            refs.append(self.range)
        if self.storage is not None:
            refs.append(self.storage)
        if self.nomenclature is not None:
            refs.append(self.nomenclature)
        return refs
