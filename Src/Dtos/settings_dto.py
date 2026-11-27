from Src.Models.settings_model import settings_model
from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto
from Src.Dtos.report_type_enum import report_type_enum

"""
Dto для описания настроек приложения
"""
class settings_dto(abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование директора
    __boss_name: str = ""

    # Наименование главного бухгалтера
    __account_name: str = ""

    # Флаг первого старта
    __first_start: bool = True

    # Формат отчетов по умолчанию
    __default_report_type: int = 1

    # Поля организации
    __company_name: str = ""
    __company_inn: str = ""
    __company_bik: str = ""
    __company_account: str = ""
    __company_corr_account: str = ""
    __company_ownership: str = ""

    """
    Уникальный код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = str(value).strip() if value else ""

    """
    Руководитель
    """
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        self.__boss_name = str(value).strip() if value else ""

    """
    Главный бухгалтер
    """
    @property
    def account_name(self) -> str:
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        self.__account_name = str(value).strip() if value else ""

    """
    Первый старт
    """
    @property
    def first_start(self) -> bool:
        return self.__first_start

    @first_start.setter
    def first_start(self, value: bool) -> None:
        self.__first_start = bool(value)

    """
    Формат отчета по умолчанию
    """
    @property
    def default_report_type(self) -> int:
        return self.__default_report_type

    @default_report_type.setter
    def default_report_type(self, value: int) -> None:
        self.__default_report_type = int(value) if value is not None else 1

    """
    Наименование организации
    """
    @property
    def company_name(self) -> str:
        return self.__company_name

    @company_name.setter
    def company_name(self, value: str) -> None:
        self.__company_name = str(value).strip() if value else ""

    """
    ИНН организации
    """
    @property
    def company_inn(self) -> str:
        return self.__company_inn

    @company_inn.setter
    def company_inn(self, value: str) -> None:
        self.__company_inn = str(value).strip() if value else ""

    """
    БИК банка
    """
    @property
    def company_bik(self) -> str:
        return self.__company_bik

    @company_bik.setter
    def company_bik(self, value: str) -> None:
        self.__company_bik = str(value).strip() if value else ""

    """
    Банковский счет
    """
    @property
    def company_account(self) -> str:
        return self.__company_account

    @company_account.setter
    def company_account(self, value: str) -> None:
        self.__company_account = str(value).strip() if value else ""

    """
    Корреспондентский счет
    """
    @property
    def company_corr_account(self) -> str:
        return self.__company_corr_account

    @company_corr_account.setter
    def company_corr_account(self, value: str) -> None:
        self.__company_corr_account = str(value).strip() if value else ""

    """
    Форма собственности
    """
    @property
    def company_ownership(self) -> str:
        return self.__company_ownership

    @company_ownership.setter
    def company_ownership(self, value: str) -> None:
        self.__company_ownership = str(value).strip() if value else ""

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: settings_model) -> "settings_dto":
        validator.validate(source, settings_model)

        dto = settings_dto()
        dto.unique_code = source.unique_code
        dto.boss_name = source.boss_name
        dto.account_name = source.account_name
        dto.first_start = source.first_start

        if hasattr(source.default_report_type, "value"):
            dto.default_report_type = source.default_report_type.value
        else:
            dto.default_report_type = int(source.default_report_type)

        if source.company is not None:
            dto.company_name = source.company.name
            dto.company_inn = str(source.company.inn)
            dto.company_bik = source.company.bik
            dto.company_account = source.company.account
            dto.company_corr_account = source.company.corr_account
            dto.company_ownership = source.company.ownership

        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache: dict) -> settings_model:
        super().mapping(cache)

        domain = settings_model()
        if self.unique_code:
            domain.unique_code = self.unique_code
        if self.boss_name:
            domain.boss_name = self.boss_name
        if self.account_name:
            domain.account_name = self.account_name
        domain.first_start = self.first_start
        domain.default_report_type = self.default_report_type

        company = company_model()
        if self.company_name:
            company.name = self.company_name
        if self.company_inn:
            company.inn = int(self.company_inn)
        if self.company_bik:
            company.bik = self.company_bik
        if self.company_account:
            company.account = self.company_account
        if self.company_corr_account:
            company.corr_account = self.company_corr_account
        if self.company_ownership:
            company.ownership = self.company_ownership

        domain.company = company
        cache[domain.unique_code] = domain
        return domain

    """
    Фабричный метод создания DTO из словаря
    """
    def from_dict(self, source: dict) -> "settings_dto":
        validator.validate(source, dict)

        dto = settings_dto()
        dto.unique_code = str(self.try_get_value("unique_code", source) or "")
        dto.boss_name = str(self.try_get_value("boss_name", source) or "")
        dto.account_name = str(self.try_get_value("account_name", source) or "")
        first_start = self.try_get_value("first_start", source)
        if first_start is not None:
            dto.first_start = bool(first_start)

        report_type = self.try_get_value("default_report_type", source)
        if report_type is not None:
            dto.default_report_type = int(report_type)

        dto.company_name = str(self.try_get_value("company_name", source) or "")
        inn = self.try_get_value("company_inn", source)
        if inn is not None:
            dto.company_inn = str(inn)

        dto.company_bik = str(self.try_get_value("company_bik", source) or "")
        dto.company_account = str(self.try_get_value("company_account", source) or "")
        dto.company_corr_account = str(self.try_get_value("company_corr_account", source) or "")
        dto.company_ownership = str(self.try_get_value("company_ownership", source) or "")

        return dto
