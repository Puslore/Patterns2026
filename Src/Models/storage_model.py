from typing import Optional

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.unit_model import NAME_MAX_LENGTH
from Src.Models.organization_model import organization_model


class storage_model(abstract_model):
    """
    Модель `Склад`.

    Доменная сущность, описывающая место хранения продукции.
    Каждый склад связан с организацией-владельцем (ассоциация).

    Правила:
        - Наименование склада - обычное, ограничено 50 символами.
        - Адрес склада необязателен, но при указании должен быть непустой строкой.
        - Организация-владелец обязана быть экземпляром organization_model.
    """

    # Адрес расположения склада.
    _address: Optional[str] = None

    # Организация, которой принадлежит склад.
    _organization: Optional[organization_model] = None

    def __init__(self, name: str, address: Optional[str] = None,
                 organization: Optional[organization_model] = None,
                 id: Optional[str] = None) -> None:
        """
        Инициализация склада.
        :param name: Наименование склада (не длиннее 50 символов)
        :param address: Адрес склада, необязательный
        :param organization: Организация-владелец склада
        :param id: Необязательный идентификатор сущности
        """
        self.name = name
        if address is not None:
            self.address = address
        if organization is not None:
            self.organization = organization
        if id is not None:
            self.id = id

    @property
    def address(self) -> Optional[str]:
        """
        Возвращает адрес склада.
        """
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        """
        Установка адреса склада. Значение обязано быть непустой строкой.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception('Адрес склада должен быть непустой строкой', 'address')
        self._address = value.strip()

    @property
    def organization(self) -> Optional[organization_model]:
        """
        Возвращает организацию-владельца склада.
        """
        return self._organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        """
        Установка организации-владельца. Значение обязано быть экземпляром organization_model.
        """
        if not isinstance(value, organization_model):
            raise arguments_exception(
                'Организация должна быть экземпляром organization_model', 'organization')
        self._organization = value

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает наименование склада.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования. Обычное ограничение поля `наименование` - 50 символов.
        """
        super(storage_model, type(self)).name.fset(self, value)
        if len(self._name) > NAME_MAX_LENGTH:
            raise arguments_exception(
                f'Наименование не может быть длиннее {NAME_MAX_LENGTH} символов', 'name')
