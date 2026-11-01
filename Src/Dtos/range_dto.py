from Src.Models.range_model import range_model
from Src.Core.validator import validator
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания единицы измерения
"""
class range_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Значение коэффициента
    __value: int = 1

    # Код базовой единицы измерения
    __base_code: str = ""

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
    Значение коэффициента
    """
    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        self.__value = value

    """
    Код базовой единицы измерения
    """
    @property
    def base_code(self) -> str:
        return self.__base_code

    @base_code.setter
    def base_code(self, value: str) -> None:
        self.__base_code = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: range_model) -> "range_dto":
        validator.validate(source, range_model)
        
        dto = range_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.value = source.value
        
        # В DTO сохраняем только код базовой единицы, а не сам объект
        if source.base is not None:
            dto.base_code = source.base.unique_code
            
        return dto