from typing import List
from Src.Core.abstract_dto import abstract_dto
from Src.Core.filter_type_enum import filter_type_enum
from Src.Core.validator import validator
from Src.Dtos.filter_item_dto import filter_item_dto


class filter_dto(abstract_dto):
    """
    DTO модель параметров фильтрации доменных объектов
    """

    # Список критериев фильтрации
    __filters: List[filter_item_dto] = None
    # Имя целевой модели (опционально)
    __model_type: str = ""
    # Фильтр по наименованию (быстрый доступ)
    __name: str = ""
    # Фильтр по уникальному коду (быстрый доступ)
    __unique_code: str = ""
    # Тип фильтрации по умолчанию
    __filter_type: filter_type_enum = filter_type_enum.EQUALS

    def __init__(self):
        """
        Инициализация DTO фильтра
        """
        self.__filters = []
        self.__model_type = ""
        self.__name = ""
        self.__unique_code = ""
        self.__filter_type = filter_type_enum.EQUALS

    @property
    def filters(self) -> List[filter_item_dto]:
        """
        Получить список критериев фильтрации
        """
        return self.__filters

    @filters.setter
    def filters(self, value: list) -> None:
        """
        Установить список критериев фильтрации
        """
        validator.validate(value, list)
        items: List[filter_item_dto] = []
        for item in value:
            if isinstance(item, filter_item_dto):
                items.append(item)
            elif isinstance(item, dict):
                items.append(filter_item_dto().from_dict(item))
        self.__filters = items

    @property
    def model_type(self) -> str:
        """
        Наименование целевой доменной модели
        """
        return self.__model_type

    @model_type.setter
    def model_type(self, value: str) -> None:
        """
        Установить целевую модель
        """
        self.__model_type = str(value).strip() if value is not None else ""

    @property
    def name(self) -> str:
        """
        Значение фильтра по наименованию
        """
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        """
        Установить фильтр по наименованию
        """
        self.__name = str(value).strip() if value is not None else ""
        if self.__name:
            self.add_filter("name", self.__filter_type, self.__name)

    @property
    def unique_code(self) -> str:
        """
        Значение фильтра по уникальному коду
        """
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        """
        Установить фильтр по уникальному коду
        """
        self.__unique_code = str(value).strip() if value is not None else ""
        if self.__unique_code:
            self.add_filter("unique_code", self.__filter_type, self.__unique_code)

    @property
    def filter_type(self) -> filter_type_enum:
        """
        Тип фильтрации по умолчанию
        """
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, value: object) -> None:
        """
        Установить тип фильтрации по умолчанию
        """
        self.__filter_type = filter_type_enum.from_value(value)
        for f in self.__filters:
            if f.field_name in ("name", "unique_code"):
                f.filter_type = self.__filter_type

    def add_filter(self, field_name: str, filter_type: object, value: object) -> None:
        """
        Добавить критерий фильтрации
        """
        # Удаляем существующий фильтр по тому же полю, если уже был добавлен
        self.__filters = [f for f in self.__filters if f.field_name != field_name]
        item = filter_item_dto(field_name, filter_type, value)
        self.__filters.append(item)

    def from_domain_model(self, source: object) -> "filter_dto":
        """
        Создать DTO из доменной модели (заглушка abstract_dto)
        """
        return self

    def mapping(self, cache: dict) -> object:
        """
        Маппинг в доменную модель (заглушка abstract_dto)
        """
        return None

    def from_dict(self, source: dict) -> "filter_dto":
        """
        Фабричный метод создания DTO из словаря
        """
        validator.validate(source, dict)

        dto = filter_dto()
        dto.model_type = self.try_get_value("model_type", source) or self.try_get_value("entity", source) or ""

        ft_raw = self.try_get_value("filter_type", source)
        if ft_raw is not None:
            dto.filter_type = ft_raw

        filters_raw = self.try_get_value("filters", source)
        if filters_raw is not None and isinstance(filters_raw, list):
            items: List[filter_item_dto] = []
            for it in filters_raw:
                if isinstance(it, filter_item_dto):
                    items.append(it)
                elif isinstance(it, dict):
                    items.append(filter_item_dto().from_dict(it))
            dto.filters = items

        # Поддержка плоских полей name и unique_code в корне DTO
        name_val = self.try_get_value("name", source)
        if name_val is not None and str(name_val).strip() != "":
            dto.name = str(name_val).strip()

        code_val = self.try_get_value("unique_code", source)
        if code_val is not None and str(code_val).strip() != "":
            dto.unique_code = str(code_val).strip()

        return dto

    def __getattr__(self, name: str) -> object:
        """
        Поддержка обращений через внутренние приватные имена из тестов
        """
        if name in ("__filters", "_filter_dto__filters"):
            return self.__filters
        if name in ("__model_type", "_filter_dto__model_type"):
            return self.__model_type
        if name in ("__name", "_filter_dto__name"):
            return self.__name
        if name in ("__unique_code", "_filter_dto__unique_code"):
            return self.__unique_code
        if name in ("__filter_type", "_filter_dto__filter_type"):
            return self.__filter_type
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: object) -> None:
        """
        Поддержка прямой установки приватных полей из тестов
        """
        if name in ("__filters", "_filter_dto__filters"):
            if isinstance(value, list):
                items: List[filter_item_dto] = []
                for it in value:
                    if isinstance(it, filter_item_dto):
                        items.append(it)
                    elif isinstance(it, dict):
                        items.append(filter_item_dto().from_dict(it))
                super().__setattr__("_filter_dto__filters", items)
            else:
                super().__setattr__("_filter_dto__filters", value)
            return
        if name in ("__model_type", "_filter_dto__model_type"):
            super().__setattr__("_filter_dto__model_type", str(value).strip() if value is not None else "")
            return
        if name in ("__name", "_filter_dto__name"):
            val_str = str(value).strip() if value is not None else ""
            super().__setattr__("_filter_dto__name", val_str)
            if val_str:
                self.add_filter("name", self.filter_type, val_str)
            return
        if name in ("__unique_code", "_filter_dto__unique_code"):
            val_str = str(value).strip() if value is not None else ""
            super().__setattr__("_filter_dto__unique_code", val_str)
            if val_str:
                self.add_filter("unique_code", self.filter_type, val_str)
            return
        if name in ("__filter_type", "_filter_dto__filter_type"):
            super().__setattr__("_filter_dto__filter_type", filter_type_enum.from_value(value))
            return
        super().__setattr__(name, value)
