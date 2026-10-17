from Src.Core.abstract_model import abstact_model
from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Models.response_format_enum import response_format_enum


class settings_model(abstact_model):
    """Настройки приложения и реквизиты организации."""

    # Карточка организации
    __company:company_model = None
    # Наименование директора
    __boss_name:str = ""
    # Наименование главного бухгалтера
    __account_name:str = ""
    # Первый старт
    __first_start:bool = True
    # Формат отчета по умолчанию
    __response_format:response_format_enum = response_format_enum.TXT

    """
    Карточка организации
    """
    @property
    def company(self) -> company_model:
        return self.__company

    @company.setter
    def company(self, value:company_model) -> None:
        validator.validate(value, company_model)
        self.__company = value

    """
    Наименование директора
    """
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value:str) -> None:
        validator.validate(value, str, 255)
        self.__boss_name = value.strip()

    """
    Главный бухгалтер
    """
    @property
    def account_name(self) -> str:
        return self.__account_name    

    @account_name.setter
    def account_name(self, value:str) -> None:
        validator.validate(value, str, 255)
        self.__account_name = value.strip()

    """
    Флаг. Первый старт
    """
    @property
    def first_start(self) -> bool:
        return self.__first_start    

    @first_start.setter
    def first_start(self, value:bool) -> None:
        validator.validate(value, bool)
        self.__first_start = value

    """
    Формат ответа по умолчанию
    """
    @property
    def response_format(self) -> response_format_enum:
        return self.__response_format

    @response_format.setter
    def response_format(self, value:response_format_enum) -> None:
        validator.validate(value, response_format_enum)
        self.__response_format = value
