from typing import Any, List, Set

from Src.Core.abstract_model import abstact_model
from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.common import common
from Src.Core.filter_type_enum import filter_type_enum
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.filter_item_dto import filter_item_dto


class prototype(abstract_prototype):
    """
    Универсальная реализация шаблона Прототип для фильтрации доменных моделей.

    Один и тот же прототип используется для номенклатуры, групп, единиц
    измерения, рецептов и складских транзакций. Поиск выполняется как по
    собственным полям объекта, так и по вложенным доменным структурам
    (например, единица измерения -> базовая единица, группа -> группа-владелец).
    """

    # Признак отсутствующего значения при обходе свойств
    _MISSING = object()

    # Коллекция исходных данных
    __data: list = None

    def __init__(self, data: list = None):
        """
        Инициализировать прототип переданным набором данных.
        """
        self.__data = list(data) if data is not None else []

    @property
    def data(self) -> list:
        """
        Получить набор данных, хранящийся в прототипе.
        """
        return self.__data

    def clone(self, filter: filter_dto = None) -> "prototype":
        """
        Склонировать прототип и применить к данным переданный фильтр.
        """
        criteria = self._extract_criteria(filter) if filter is not None else []
        if not criteria:
            return prototype(self.__data)

        filtered = [
            item for item in self.__data if self._match_all_criteria(item, criteria)
        ]
        return prototype(filtered)

    def _extract_criteria(self, filter: filter_dto) -> List[filter_item_dto]:
        """
        Извлечь список активных критериев фильтрации из DTO модели.
        """
        criteria: List[filter_item_dto] = []

        raw_filters = getattr(filter, "filters", None)
        if raw_filters is None:
            raw_filters = getattr(filter, "_filter_dto__filters", None)

        if raw_filters:
            for item in raw_filters:
                if isinstance(item, filter_item_dto):
                    criteria.append(item)
                elif isinstance(item, dict):
                    criteria.append(filter_item_dto().from_dict(item))

        # Поддержка плоских полей name и unique_code в корне DTO
        name_value = getattr(filter, "name", None) or getattr(filter, "_filter_dto__name", None)
        if name_value and not any(item.field_name == "name" for item in criteria):
            criteria.append(filter_item_dto("name", filter.filter_type, name_value))

        code_value = getattr(filter, "unique_code", None) or getattr(filter, "_filter_dto__unique_code", None)
        if code_value and not any(item.field_name == "unique_code" for item in criteria):
            criteria.append(filter_item_dto("unique_code", filter_type_enum.EQUALS, code_value))

        return criteria

    def _match_all_criteria(self, item: object, criteria: List[filter_item_dto]) -> bool:
        """
        Проверить, что объект удовлетворяет всем критериям фильтра.
        """
        for criterion in criteria:
            if not self._match_single_criterion(item, criterion):
                return False
        return True

    def _match_single_criterion(self, item: object, criterion: filter_item_dto) -> bool:
        """
        Проверить соответствие объекта одному критерию фильтрации.
        """
        field_name = criterion.field_name
        filter_type = criterion.filter_type
        target_value = criterion.value

        # Явно заданный путь по вложенным свойствам (например, base.name)
        if "." in field_name:
            visited: Set[int] = {id(item)}
            return self._match_dot_notation(item, field_name, filter_type, target_value, visited)

        # Прямая проверка свойства на самом объекте
        if hasattr(item, field_name):
            value = getattr(item, field_name, None)
            if self._compare_values(value, target_value, filter_type):
                return True

        # Поиск во вложенных доменных структурах
        visited = {id(item)}
        return self._search_nested(item, field_name, filter_type, target_value, visited)

    def _match_dot_notation(
        self,
        item: object,
        field_path: str,
        filter_type: filter_type_enum,
        target_value: Any,
        visited: Set[int],
    ) -> bool:
        """
        Проверить значение по цепочке свойств, включая поиск во вложенных объектах.
        """
        if self._match_path(item, field_path.split("."), filter_type, target_value):
            return True

        for child in self._get_nested_candidates(item):
            if id(child) in visited:
                continue
            visited.add(id(child))
            if self._match_dot_notation(child, field_path, filter_type, target_value, visited):
                return True

        return False

    def _match_path(
        self,
        value: Any,
        parts: List[str],
        filter_type: filter_type_enum,
        target_value: Any,
    ) -> bool:
        """
        Рекурсивно пройти по частям пути и сравнить итоговое значение.
        """
        if not parts:
            return self._compare_values(value, target_value, filter_type)
        if value is None:
            return False

        if isinstance(value, (list, tuple)):
            return any(
                self._match_path(item, parts, filter_type, target_value)
                for item in value
            )

        part = parts[0]
        if isinstance(value, dict):
            if part not in value:
                return False
            child = value[part]
        else:
            child = getattr(value, part, self._MISSING)
            if child is self._MISSING:
                return False

        return self._match_path(child, parts[1:], filter_type, target_value)

    def _search_nested(
        self,
        entity: object,
        field_name: str,
        filter_type: filter_type_enum,
        target_value: Any,
        visited: Set[int],
    ) -> bool:
        """
        Рекурсивно проверить одноименное поле во вложенных доменных объектах.
        """
        for child in self._get_nested_candidates(entity):
            if id(child) in visited:
                continue
            visited.add(id(child))

            if hasattr(child, field_name):
                value = getattr(child, field_name, None)
                if self._compare_values(value, target_value, filter_type):
                    return True

            if self._search_nested(child, field_name, filter_type, target_value, visited):
                return True

        return False

    def _get_nested_candidates(self, entity: object) -> list:
        """
        Собрать вложенные доменные объекты через рефлексию по свойствам модели.
        """
        if not isinstance(entity, abstact_model):
            return []

        nested = []
        for field_name in common.get_fields(entity, False):
            try:
                value = getattr(entity, field_name)
            except Exception:
                continue

            if isinstance(value, abstact_model):
                nested.append(value)
            elif isinstance(value, (list, tuple)):
                nested.extend(
                    item for item in value if isinstance(item, abstact_model)
                )

        return nested

    def _compare_values(
        self,
        actual: Any,
        target: Any,
        filter_type: filter_type_enum,
    ) -> bool:
        """
        Сравнить фактическое и ожидаемое значения согласно типу фильтрации.
        """
        if target is None:
            return actual is None
        if actual is None:
            return False

        normalized_actual = self._normalize_text(str(actual))
        normalized_target = self._normalize_text(str(target))
        filter_enum = filter_type_enum.from_value(filter_type)

        if filter_enum == filter_type_enum.LIKE:
            return normalized_target in normalized_actual

        return normalized_actual == normalized_target

    def _normalize_text(self, text: str) -> str:
        """
        Привести строку к единому виду для сравнения без учета регистра.
        """
        return text.strip().lower()

    def __getattr__(self, name: str) -> object:
        """
        Поддержка обращений к исходному набору данных по имени __data.
        """
        if name in ("__data", "_prototype__data"):
            return self.__data
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
