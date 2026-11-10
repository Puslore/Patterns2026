from Src.Models.group_model import group_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания группы номенклатуры
"""
class group_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

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
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: group_model) -> "group_dto":
        validator.validate(source, group_model)
        
        dto = group_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        
        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache:dict) -> group_model:
        super().mapping(cache)

        domain = group_model()
        domain.unique_code = self.unique_code
        domain.name = self.name
        cache[ domain.unique_code ] = domain

        return domain

    """
    Фабричный метод создания DTO из словаря
    """
    def from_dict(self, source:dict) -> "group_dto":
        validator.validate( source, dict)

        dto = group_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)

        return dto
    