from Src.Models.storage_model import storage_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания склада
"""
class storage_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Адрес
    __address: str = ""

    """
    Код
    """
    @property
    def unique_code(self) -> str:
        return self.__unique_code

    @unique_code.setter
    def unique_code(self, value: str) -> None:
        self.__unique_code = str(value).strip() if value is not None else ""

    """
    Наименование
    """
    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = str(value).strip() if value is not None else ""

    """
    Адрес
    """
    @property
    def address(self) -> str:
        return self.__address

    @address.setter
    def address(self, value: str) -> None:
        self.__address = str(value).strip() if value is not None else ""

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: storage_model) -> "storage_dto":
        validator.validate(source, storage_model)
        
        dto = storage_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.address = source.address
        
        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache: dict) -> storage_model:
        super().mapping(cache)

        domain = storage_model()
        if self.unique_code and self.unique_code.strip() != "":
            domain.unique_code = self.unique_code
        domain.name = self.name
        domain.address = self.address
        cache[ domain.unique_code ] = domain

        return domain


    """
    Фабричный метод создания DTO из словаря
    """
    def from_dict(self, source: dict) -> "storage_dto":
        validator.validate(source, dict)

        dto = storage_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)
        dto.address = self.try_get_value("address", source)

        return dto

        
     