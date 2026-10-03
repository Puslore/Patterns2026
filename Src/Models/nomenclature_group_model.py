from typing import List, Optional

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH


class nomenclature_group_model(abstract_model):
    """
    Модель `Группа номенклатуры`.

    Доменная сущность, объединяющая похожие позиции номенклатуры
    (например: `Молочные продукты`, `Мясные продукты`).

    Правила:
        - Наименование группы - обычное, ограничено 50 символами.
        - Единицы измерения группы обязательны: список не может быть пустым.
    """

    # Список включенных в группу единиц измерения (обязателен, не пуст).
    _units: List[unit_model]

    def __init__(self, name: str, units: List[unit_model],
                 id: Optional[str] = None) -> None:
        """
        Инициализация группы номенклатуры.
        :param name: Наименование группы (не длиннее 50 символов)
        :param units: Обязательный непустой список единиц измерения группы
        :param id: Необязательный идентификатор сущности
        """
        self._units = []
        self.name = name
        self.units = units
        if id is not None:
            self.id = id

    @property
    def units(self) -> List[unit_model]:
        """
        Возвращает копию списка единиц измерения, входящих в группу.
        """
        return list(self._units)

    @units.setter
    def units(self, value: List[unit_model]) -> None:
        """
        Установка списка единиц измерения группы.
        Единицы измерения обязательны: список должен быть непустым
        и содержать только экземпляры unit_model без дубликатов.
        """
        if isinstance(value, str) or not isinstance(value, (list, tuple)):
            raise arguments_exception(
                'Единицы измерения группы должны быть заданы списком', 'units')
        if len(value) == 0:
            raise arguments_exception(
                'Группа номенклатуры должна содержать хотя бы одну единицу измерения', 'units')
        self._units = []
        for unit in value:
            self.add_unit(unit)

    def add_unit(self, unit: unit_model) -> None:
        """
        Добавляет единицу измерения в группу.
        :param unit: Экземпляр unit_model
        """
        if not isinstance(unit, unit_model):
            raise arguments_exception('В группу можно добавлять только экземпляры unit_model', 'units')
        if any(u.id == unit.id for u in self._units):
            raise arguments_exception('Такая единица измерения уже входит в группу', 'units')
        self._units.append(unit)

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает наименование группы номенклатуры.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования. Обычное ограничение поля `наименование` - 50 символов.
        """
        super(nomenclature_group_model, type(self)).name.fset(self, value)
        if len(self._name) > NAME_MAX_LENGTH:
            raise arguments_exception(
                f'Наименование не может быть длиннее {NAME_MAX_LENGTH} символов', 'name')
