from __future__ import annotations

import re
from enum import Enum
from typing import Optional, Union

from Src.Core.abstract_model import abstract_model
from Src.Core.exception import arguments_exception
from Src.Models.unit_model import NAME_MAX_LENGTH


class ownership_form(str, Enum):
    """
    Перечисление форм собственности организации.
    """
    STATE = 'государственная'
    MUNICIPAL = 'муниципальная'
    PRIVATE = 'частная'
    JOINT_STOCK_COMPANY = 'акционерное общество'
    LIMITED_LIABILITY_COMPANY = 'общество с ограниченной ответственностью'
    PUBLIC = 'общественная'
    OTHER = 'иная'


class organization_model(abstract_model):
    """
    Модель `Организация`.

    Доменная сущность, описывающая юридическое лицо (или ИП) с обязательными
    реквизитами: ИНН, БИК, расчетный счет и форма собственности.

    Правила:
        - ИНН юридического лица - 10 цифр, ИНН индивидуального предпринимателя - 12 цифр.
        - БИК - 9 цифр.
        - Номер расчетного счета - 20 цифр.
        - Форма собственности задается значением перечисления ownership_form.
    """

    # Идентификационный номер налогоплательщика.
    _inn: Optional[str] = None

    # Банковский идентификационный код.
    _bik: Optional[str] = None

    # Номер расчетного счета.
    _account: Optional[str] = None

    # Форма собственности организации.
    _ownership_form: Optional[ownership_form] = None

    def __init__(self, name: str, inn: str, bik: str, account: str,
                 ownership_form_value: Union['ownership_form', str],
                 id: Optional[str] = None) -> None:
        """
        Инициализация организации.
        :param name: Наименование организации (не длиннее 50 символов)
        :param inn: ИНН (10 или 12 цифр)
        :param bik: БИК (9 цифр)
        :param account: Расчетный счет (20 цифр)
        :param ownership_form_value: Форма собственности (значение перечисления или его строка)
        :param id: Необязательный идентификатор сущности
        """
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_form = ownership_form_value
        if id is not None:
            self.id = id

    @property
    def inn(self) -> Optional[str]:
        """
        Возвращает ИНН организации.
        """
        return self._inn

    @inn.setter
    def inn(self, value: str) -> None:
        """
        Установка ИНН. Допускаются только 10 (юрлицо) или 12 (ИП) цифр.
        """
        if not isinstance(value, str) or not re.fullmatch(r'\d{10}|\d{12}', value.strip()):
            raise arguments_exception('ИНН должен содержать 10 или 12 цифр', 'inn')
        self._inn = value.strip()

    @property
    def bik(self) -> Optional[str]:
        """
        Возвращает БИК организации.
        """
        return self._bik

    @bik.setter
    def bik(self, value: str) -> None:
        """
        Установка БИК. Допускаются только 9 цифр.
        """
        if not isinstance(value, str) or not re.fullmatch(r'\d{9}', value.strip()):
            raise arguments_exception('БИК должен содержать 9 цифр', 'bik')
        self._bik = value.strip()

    @property
    def account(self) -> Optional[str]:
        """
        Возвращает номер расчетного счета организации.
        """
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        """
        Установка номера расчетного счета. Допускаются только 20 цифр.
        """
        if not isinstance(value, str) or not re.fullmatch(r'\d{20}', value.strip()):
            raise arguments_exception('Номер счета должен содержать 20 цифр', 'account')
        self._account = value.strip()

    @property
    def ownership_form(self) -> Optional[ownership_form]:
        """
        Возвращает форму собственности организации.
        """
        return self._ownership_form

    @ownership_form.setter
    def ownership_form(self, value: Union['ownership_form', str]) -> None:
        """
        Установка формы собственности.
        Допускается значение перечисления ownership_form либо его строковое представление.
        """
        if isinstance(value, ownership_form):
            self._ownership_form = value
            return
        if isinstance(value, str):
            for form in ownership_form:
                if value.strip().lower() == form.value:
                    self._ownership_form = form
                    return
        raise arguments_exception('Некорректная форма собственности организации', 'ownership_form')

    @property
    def name(self) -> Optional[str]:
        """
        Возвращает наименование организации.
        """
        return getattr(self, '_name', None)

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования. Обычное ограничение поля `наименование` - 50 символов.
        """
        super(organization_model, type(self)).name.fset(self, value)
        if len(self._name) > NAME_MAX_LENGTH:
            raise arguments_exception(
                f'Наименование не может быть длиннее {NAME_MAX_LENGTH} символов', 'name')
