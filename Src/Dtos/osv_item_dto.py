from Src.Core.abstract_dto import abstract_dto
from Src.Core.validator import validator


class osv_item_dto(abstract_dto):
    """
    DTO строка оборотно-сальдовой ведомости (ОСВ)
    """

    # Наименование склада
    __storage_name: str = ""
    # Уникальный код склада
    __storage_code: str = ""
    # Наименование номенклатуры
    __nomenclature_name: str = ""
    # Уникальный код номенклатуры
    __nomenclature_code: str = ""
    # Наименование единицы измерения
    __range_name: str = ""
    # Уникальный код единицы измерения
    __range_code: str = ""
    # Начальный остаток (сальдо на начало)
    __initial_balance: float = 0.0
    # Приход за период (оборот Дт)
    __turnover_in: float = 0.0
    # Расход за период (оборот Кт)
    __turnover_out: float = 0.0
    # Конечный остаток (сальдо на конец)
    __final_balance: float = 0.0

    @property
    def storage_name(self) -> str:
        """
        Наименование склада
        """
        return self.__storage_name

    @storage_name.setter
    def storage_name(self, value: str) -> None:
        self.__storage_name = str(value).strip() if value is not None else ""

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
    def nomenclature_name(self) -> str:
        """
        Наименование номенклатуры
        """
        return self.__nomenclature_name

    @nomenclature_name.setter
    def nomenclature_name(self, value: str) -> None:
        self.__nomenclature_name = str(value).strip() if value is not None else ""

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
    def range_name(self) -> str:
        """
        Наименование единицы измерения
        """
        return self.__range_name

    @range_name.setter
    def range_name(self, value: str) -> None:
        self.__range_name = str(value).strip() if value is not None else ""

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
    def initial_balance(self) -> float:
        """
        Начальный остаток
        """
        return self.__initial_balance

    @initial_balance.setter
    def initial_balance(self, value: float) -> None:
        self.__initial_balance = float(value) if value is not None else 0.0

    @property
    def turnover_in(self) -> float:
        """
        Приход за период
        """
        return self.__turnover_in

    @turnover_in.setter
    def turnover_in(self, value: float) -> None:
        self.__turnover_in = float(value) if value is not None else 0.0

    @property
    def turnover_out(self) -> float:
        """
        Расход за период
        """
        return self.__turnover_out

    @turnover_out.setter
    def turnover_out(self, value: float) -> None:
        self.__turnover_out = float(value) if value is not None else 0.0

    @property
    def final_balance(self) -> float:
        """
        Конечный остаток
        """
        return self.__final_balance

    @final_balance.setter
    def final_balance(self, value: float) -> None:
        self.__final_balance = float(value) if value is not None else 0.0

    def to_dict(self) -> dict:
        """
        Преобразовать объект ОСВ в словарь
        """
        return {
            "storage_name": self.storage_name,
            "storage_code": self.storage_code,
            "nomenclature_name": self.nomenclature_name,
            "nomenclature_code": self.nomenclature_code,
            "range_name": self.range_name,
            "range_code": self.range_code,
            "initial_balance": self.initial_balance,
            "turnover_in": self.turnover_in,
            "turnover_out": self.turnover_out,
            "final_balance": self.final_balance,
        }

    def from_domain_model(self, source: object) -> "osv_item_dto":
        """
        Создать DTO из доменной модели (заглушка abstract_dto)
        """
        return self

    def mapping(self, cache: dict) -> object:
        """
        Маппинг в доменную модель (заглушка abstract_dto)
        """
        return None

    def from_dict(self, source: dict) -> "osv_item_dto":
        """
        Фабричный метод создания DTO из словаря
        """
        validator.validate(source, dict)

        dto = osv_item_dto()
        dto.storage_name = str(self.try_get_value("storage_name", source) or "")
        dto.storage_code = str(self.try_get_value("storage_code", source) or "")
        dto.nomenclature_name = str(self.try_get_value("nomenclature_name", source) or "")
        dto.nomenclature_code = str(self.try_get_value("nomenclature_code", source) or "")
        dto.range_name = str(self.try_get_value("range_name", source) or "")
        dto.range_code = str(self.try_get_value("range_code", source) or "")
        dto.initial_balance = float(self.try_get_value("initial_balance", source) or 0.0)
        dto.turnover_in = float(self.try_get_value("turnover_in", source) or 0.0)
        dto.turnover_out = float(self.try_get_value("turnover_out", source) or 0.0)
        dto.final_balance = float(self.try_get_value("final_balance", source) or 0.0)
        return dto
