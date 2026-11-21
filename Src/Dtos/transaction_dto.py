from datetime import datetime
from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator, operation_exception
from Src.Models.transaction_model import transaction_model


class transaction_dto(abstract_dto):
    """
    DTO модель для передачи данных складской транзакции
    """

    __unique_code: str = ""
    __storage_code: str = ""
    __nomenclature_code: str = ""
    __range_code: str = ""
    __value: float = 0.0
    __period: str = ""

    @property
    def unique_code(self) -> str:
        """
        Уникальный код транзакции
        """
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = str(value).strip() if value is not None else ""

    @property
    def storage_code(self) -> str:
        """
        Уникальный код склада
        """
        return self.__storage_code

    @storage_code.setter
    def storage_code(self, value: str) -> None:
        self.__storage_code = str(value).strip() if value is not None else ""

    @property
    def nomenclature_code(self) -> str:
        """
        Уникальный код номенклатуры
        """
        return self.__nomenclature_code

    @nomenclature_code.setter
    def nomenclature_code(self, value: str) -> None:
        self.__nomenclature_code = str(value).strip() if value is not None else ""

    @property
    def range_code(self) -> str:
        """
        Уникальный код единицы измерения
        """
        return self.__range_code

    @range_code.setter
    def range_code(self, value: str) -> None:
        self.__range_code = str(value).strip() if value is not None else ""

    @property
    def value(self) -> float:
        """
        Количество
        """
        return self.__value

    @value.setter
    def value(self, val: float) -> None:
        self.__value = float(val) if val is not None else 0.0

    @property
    def period(self) -> str:
        """
        Дата и время в строковом формате
        """
        return self.__period

    @period.setter
    def period(self, val: str) -> None:
        self.__period = str(val).strip() if val is not None else ""

    def from_domain_model(self, source: transaction_model) -> "transaction_dto":
        """
        Создать DTO из доменной модели
        """
        validator.validate(source, transaction_model)

        dto = transaction_dto()
        dto.unique_code = source.unique_code
        dto.value = source.value
        if source.period:
            dto.period = source.period.isoformat() if isinstance(source.period, datetime) else str(source.period)
        if source.storage:
            dto.storage_code = source.storage.unique_code
        if source.nomenclature:
            dto.nomenclature_code = source.nomenclature.unique_code
        if source.range:
            dto.range_code = source.range.unique_code
        return dto

    def mapping(self, cache: dict) -> transaction_model:
        """
        Выполнить маппинг в доменную модель
        """
        super().mapping(cache)

        domain = transaction_model()
        if self.unique_code:
            domain.unique_code = self.unique_code
        domain.value = self.value

        if self.period:
            try:
                domain.period = datetime.fromisoformat(self.period)
            except Exception:
                pass

        if self.storage_code:
            if self.storage_code not in cache:
                raise operation_exception(f"Не найден склад с кодом {self.storage_code}")
            domain.storage = cache[self.storage_code]

        if self.nomenclature_code:
            if self.nomenclature_code not in cache:
                raise operation_exception(f"Не найдена номенклатура с кодом {self.nomenclature_code}")
            domain.nomenclature = cache[self.nomenclature_code]

        if self.range_code:
            if self.range_code not in cache:
                raise operation_exception(f"Не найдена единица измерения с кодом {self.range_code}")
            domain.range = cache[self.range_code]

        cache[domain.unique_code] = domain
        return domain

    def from_dict(self, source: dict) -> "transaction_dto":
        """
        Создать DTO из словаря
        """
        validator.validate(source, dict)

        dto = transaction_dto()
        dto.unique_code = str(self.try_get_value("unique_code", source) or "")
        dto.storage_code = str(self.try_get_value("storage_code", source) or "")
        dto.nomenclature_code = str(self.try_get_value("nomenclature_code", source) or "")
        dto.range_code = str(self.try_get_value("range_code", source) or "")
        val = self.try_get_value("value", source)
        dto.value = float(val) if val is not None else 0.0
        dto.period = str(self.try_get_value("period", source) or "")
        return dto
