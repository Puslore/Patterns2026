from Src.Models.company_model import company_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания организации
"""
class company_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # ИНН
    __inn: str = ""

    # БИК
    __bik: str = ""

    # Корреспондентский счет
    __corr_account: str = ""

    # Банковский счет
    __account: str = ""

    # Вид собственности
    __ownership: str = ""

    """
    Код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = value.strip()

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value.strip()

    """
    ИНН
    """
    @property
    def inn(self) -> str:
        return self.__inn

    @inn.setter
    def inn(self, value: str) -> None:
        self.__inn = value.strip()

    """
    БИК
    """
    @property
    def bik(self) -> str:
        return self.__bik

    @bik.setter
    def bik(self, value: str) -> None:
        self.__bik = value.strip()

    """
    Корреспондентский счет
    """
    @property
    def corr_account(self) -> str:
        return self.__corr_account

    @corr_account.setter
    def corr_account(self, value: str) -> None:
        self.__corr_account = value.strip()

    """
    Банковский счет
    """
    @property
    def account(self) -> str:
        return self.__account

    @account.setter
    def account(self, value: str) -> None:
        self.__account = value.strip()

    """
    Вид собственности
    """
    @property
    def ownership(self) -> str:
        return self.__ownership

    @ownership.setter
    def ownership(self, value: str) -> None:
        self.__ownership = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: company_model) -> "company_dto":
        validator.validate(source, company_model)
        
        dto = company_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.inn = str(source.inn)
        dto.bik = source.bik
        dto.corr_account = str(source.corr_account)
        dto.account = str(source.account)
        dto.ownership = source.ownership
        
        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache:dict) -> company_model:
        super().mapping(cache)

        domain = company_model()
        domain.unique_code = self.unique_code
        domain.name = self.name
        domain.inn = self.inn
        domain.bik = self.bik
        domain.corr_account = self.corr_account
        domain.account = self.account
        domain.ownership = self.ownership
        cache[ domain.unique_code ] = domain

        return domain

    """
    Фабричный метод создания DTO из словаря
    """
    def from_dict(self, source: dict) -> "company_dto":
        validator.validate(source, dict)

        dto = company_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)
        dto.inn = self.try_get_value("inn", source)
        dto.bik = self.try_get_value("bik", source)
        dto.corr_account = self.try_get_value("corr_account", source)
        dto.ownership = self.try_get_value("ownership", source)
        dto.account = self.try_get_value("account", source)

        return dto