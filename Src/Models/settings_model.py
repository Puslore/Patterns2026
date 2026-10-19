from Src.Core.abstract_model import abstact_model
from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Dtos.report_type_enum import report_type_enum


class settings_model(abstact_model):
    # Карточка организации
    __company:company_model = None
    # Наименование директора
    __boss_name:str = ""
    # Наименование главного бухгалтера
    __account_name:str = ""
    # Первый старт
    __first_start:bool = True
    # Формат по умолчанию
    __report_type:report_type_enum = report_type_enum.TXT

    def __init__(self):
        super().__init__()
        
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
        validator.validate (value, str, 255)
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
    Формат отчетов по умолчанию
    """
    @property
    def default_report_type(self) -> report_type_enum:
        return self.__report_type

    @default_report_type.setter
    def default_report_type(self, value:int)-> None:
        validator.validate(value, int)
        self.__report_type = report_type_enum(value)