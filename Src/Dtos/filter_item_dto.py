from Src.Core.abstract_dto import abstract_dto
from Src.Core.filter_type_enum import filter_type_enum
from Src.Core.validator import validator


class filter_item_dto(abstract_dto):
    """
    DTO элемент критерия фильтрации для одного поля
    """

    # Имя поля
    __field_name: str = ""
    # Тип фильтрации
    __filter_type: filter_type_enum = filter_type_enum.EQUALS
    # Значение фильтра
    __value: object = None

    def __init__(self, field_name: str = "", filter_type: object = filter_type_enum.EQUALS, value: object = None):
        """
        Инициализация элемента фильтра
        """
        self.field_name = field_name
        self.filter_type = filter_type
        self.value = value

    @property
    def field_name(self) -> str:
        """
        Имя поля для фильтрации (поддерживает точечную нотацию, например 'base.name')
        """
        return self.__field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        """
        Установить имя поля
        """
        self.__field_name = str(value).strip() if value is not None else ""

    @property
    def filter_type(self) -> filter_type_enum:
        """
        Тип фильтрации (EQUALS / LIKE)
        """
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, value: object) -> None:
        """
        Установить тип фильтрации
        """
        self.__filter_type = filter_type_enum.from_value(value)

    @property
    def value(self) -> object:
        """
        Искомое значение фильтрации
        """
        return self.__value

    @value.setter
    def value(self, val: object) -> None:
        """
        Установить значение фильтра
        """
        self.__value = val

    def from_domain_model(self, source: object) -> "filter_item_dto":
        """
        Создать DTO из доменной модели (заглушка abstract_dto)
        """
        return self

    def mapping(self, cache: dict) -> object:
        """
        Маппинг в доменную модель (заглушка abstract_dto)
        """
        return None

    def from_dict(self, source: dict) -> "filter_item_dto":
        """
        Фабричный метод создания DTO из словаря
        """
        validator.validate(source, dict)

        dto = filter_item_dto()
        dto.field_name = self.try_get_value("field_name", source) or self.try_get_value("field", source) or ""
        filter_type_raw = self.try_get_value("filter_type", source) or self.try_get_value("type", source)
        dto.filter_type = filter_type_raw if filter_type_raw is not None else filter_type_enum.EQUALS
        dto.value = self.try_get_value("value", source)
        return dto

    def __getattr__(self, name: str) -> object:
        """
        Поддержка обращений через внутренние приватные имена из тестов
        """
        if name in ("__field_name", "_filter_item_dto__field_name"):
            return self.__field_name
        if name in ("__filter_type", "_filter_item_dto__filter_type"):
            return self.__filter_type
        if name in ("__value", "_filter_item_dto__value"):
            return self.__value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: object) -> None:
        """
        Поддержка прямой установки приватных полей из тестов
        """
        if name in ("__field_name", "_filter_item_dto__field_name"):
            super().__setattr__("_filter_item_dto__field_name", str(value).strip() if value is not None else "")
            return
        if name in ("__filter_type", "_filter_item_dto__filter_type"):
            super().__setattr__("_filter_item_dto__filter_type", filter_type_enum.from_value(value))
            return
        if name in ("__value", "_filter_item_dto__value"):
            super().__setattr__("_filter_item_dto__value", value)
            return
        super().__setattr__(name, value)
