from typing import Optional

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.unit_model import unit_model, NAME_MAX_LENGTH
from Src.Models.nomenclature_group_model import nomenclature_group_model

# Максимальная длина полного наименования номенклатуры - 255 символов.
FULL_NAME_MAX_LENGTH = 255


class nomenclature_model(abstract_model):
    """
    Модель `Номенклатура`.

    Комплексная доменная сущность, описывающая учетную позицию.
    Включает в себя другие модели: группу номенклатуры и единицу измерения.

    Правила:
        - Обычное наименование (`name`) ограничено 50 символами.
        - Полное наименование (`full_name`) ограничено 255 символами.
        - Группа номенклатуры обязательна (учет ведется в разрезе групп).
        - Единица измерения обязательна и должна быть экземпляром unit_model.
    """

    # Полное наименование номенклатуры (до 255 символов).
    _full_name: Optional[str] = None

    # Группа номенклатуры, к которой относится позиция. Обязательна.
    _group: nomenclature_group_model

    # Единица измерения позиции номенклатуры. Обязательна.
    _unit: unit_model

    def __init__(self, name: str, group: nomenclature_group_model, unit: unit_model,
                 full_name: Optional[str] = None, id: Optional[str] = None) -> None:
        """
        Инициализация номенклатуры.
        :param name: Краткое наименование (не длиннее 50 символов)
        :param group: Группа номенклатуры (обязательна)
        :param unit: Единица измерения (обязательна)
        :param full_name: Полное наименование (не длиннее 255 символов), необязательное
        :param id: Необязательный идентификатор сущности
        """
        self.name = name
        self.group = group
        self.unit = unit
        if full_name is not None:
            self.full_name = full_name
        if id is not None:
            self.id = id

    @property
    def full_name(self) -> Optional[str]:
        """
        Возвращает полное наименование номенклатуры.
        """
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """
        Установка полного наименования. Ограничение - 255 символов.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception('Полное наименование должно быть непустой строкой', 'full_name')
        if len(value.strip()) > FULL_NAME_MAX_LENGTH:
            raise arguments_exception(
                f'Полное наименование не может быть длиннее {FULL_NAME_MAX_LENGTH} символов', 'full_name')
        self._full_name = value.strip()

    @property
    def group(self) -> nomenclature_group_model:
        """
        Возвращает группу номенклатуры.
        """
        return self._group

    @group.setter
    def group(self, value: nomenclature_group_model) -> None:
        """
        Установка группы номенклатуры. Значение обязано быть экземпляром nomenclature_group_model.
        """
        if not isinstance(value, nomenclature_group_model):
            raise arguments_exception(
                'Группа номенклатуры должна быть экземпляром nomenclature_group_model', 'group')
        self._group = value

    @property
    def unit(self) -> unit_model:
        """
        Возвращает единицу измерения номенклатуры.
        """
        return self._unit

    @unit.setter
    def unit(self, value: unit_model) -> None:
        """
        Установка единицы измерения. Значение обязано быть экземпляром unit_model.
        """
        if not isinstance(value, unit_model):
            raise arguments_exception('Должен быть экземпляр unit_model', 'unit')
        self._unit = value

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает краткое наименование номенклатуры.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка краткого наименования. Обычное ограничение поля `наименование` - 50 символов.
        """
        super(nomenclature_model, type(self)).name.fset(self, value)
        if len(self._name) > NAME_MAX_LENGTH:
            raise arguments_exception(
                f'Наименование не может быть длиннее {NAME_MAX_LENGTH} символов', 'name')
