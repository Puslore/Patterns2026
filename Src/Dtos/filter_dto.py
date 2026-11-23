from datetime import date, datetime, time
from typing import List

from Src.Core.abstract_dto import abstract_dto
from Src.Core.filter_type_enum import filter_type_enum
from Src.Core.validator import argument_exception, validator
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
    # Начало периода (для отчетов)
    __start_date: datetime = None
    # Окончание периода (для отчетов)
    __end_date: datetime = None

    def __init__(self):
        """
        Инициализация DTO фильтра
        """
        self.__filters = []
        self.__model_type = ""
        self.__name = ""
        self.__unique_code = ""
        self.__filter_type = filter_type_enum.EQUALS
        self.__start_date = None
        self.__end_date = None

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

    @property
    def start_date(self) -> datetime:
        """
        Начало периода отчета
        """
        return self.__start_date

    @start_date.setter
    def start_date(self, value: object) -> None:
        """
        Установить начало периода отчета
        """
        self.__start_date = self._parse_date(value, "start_date")

    @property
    def end_date(self) -> datetime:
        """
        Окончание периода отчета
        """
        return self.__end_date

    @end_date.setter
    def end_date(self, value: object) -> None:
        """
        Установить окончание периода отчета
        """
        self.__end_date = self._parse_date(value, "end_date")

    @staticmethod
    def _parse_date(value: object, field_name: str) -> datetime:
        """
        Преобразовать дату из строки, date или datetime в datetime
        """
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime.combine(value, time.max)

        if isinstance(value, str):
            text = value.strip()
            if text == "":
                return None

            has_time = "T" in text or ":" in text

            try:
                parsed = datetime.fromisoformat(text)
                if has_time:
                    return parsed
                # Дата без времени включает весь указанный день
                return datetime.combine(parsed.date(), time.max)
            except ValueError:
                pass

            for fmt in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M", "%d.%m.%Y"):
                try:
                    parsed = datetime.strptime(text, fmt)
                    if fmt == "%d.%m.%Y":
                        # Дата без времени включает весь указанный день
                        return datetime.combine(parsed.date(), time.max)
                    return parsed
                except ValueError:
                    continue

        raise argument_exception(
            f"Некорректное значение поля {field_name}: {value}"
        )

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

        # Период отчета
        start_value = self.try_get_value("start_date", source)
        if start_value is None:
            start_value = self.try_get_value("date_from", source)
        if start_value is None:
            start_value = self.try_get_value("period_from", source)
        if start_value is None:
            start_value = self.try_get_value("from_date", source)
        dto.start_date = start_value

        end_value = self.try_get_value("end_date", source)
        if end_value is None:
            end_value = self.try_get_value("date_to", source)
        if end_value is None:
            end_value = self.try_get_value("period_to", source)
        if end_value is None:
            end_value = self.try_get_value("to_date", source)
        dto.end_date = end_value

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
        if name in ("__start_date", "_filter_dto__start_date"):
            return self.__start_date
        if name in ("__end_date", "_filter_dto__end_date"):
            return self.__end_date
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
        if name in ("__start_date", "_filter_dto__start_date"):
            super().__setattr__(
                "_filter_dto__start_date",
                self._parse_date(value, "start_date"),
            )
            return
        if name in ("__end_date", "_filter_dto__end_date"):
            super().__setattr__(
                "_filter_dto__end_date",
                self._parse_date(value, "end_date"),
            )
            return
        super().__setattr__(name, value)
