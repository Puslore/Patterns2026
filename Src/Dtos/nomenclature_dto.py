from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_dto import abstract_dto

"""
Dto для описания номенклатуры
"""
class nomenclature_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Код группы
    __group_code: str = ""

    # Код единицы измерения
    __range_code: str = ""

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
    Код группы
    """
    @property
    def group_code(self) -> str:
        return self.__group_code

    @group_code.setter
    def group_code(self, value: str) -> None:
        self.__group_code = value.strip()

    """
    Код единицы измерения
    """
    @property
    def range_code(self) -> str:
        return self.__range_code

    @range_code.setter
    def range_code(self, value: str) -> None:
        self.__range_code = value.strip()

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: nomenclature_model) -> "nomenclature_dto":
        validator.validate(source, nomenclature_model)
        
        dto = nomenclature_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        
        if source.group is not None:
            dto.group_code = source.group.unique_code
            
        if source.range is not None:
            dto.range_code = source.range.unique_code
            
        return dto


    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache:dict) -> nomenclature_model:
        super().mapping(cache)

        domain = nomenclature_model()
        domain.unique_code = self.unique_code
        domain.name = self.unique_code

        if self.group_code not in cache.keys():
            raise operation_exception(f"Невозможно получить объект с кодом {self.group_code} из хранилища. Тип {type(domain.group)}.")

        domain.group = cache[ self.group_code ]

        if self.range_code not in cache.keys():
            raise operation_exception(f"Невозможно получить объект с кодом {self.range_code} из хранилища. Тип {type(domain.range)}.")

        domain.range = cache[ self.range_code ]
        cache[ domain.unique_code ] = domain

        return domain


    """
    Фабричный метод для создания DTO на основе словаря
    """
    def from_dict(self, source: dict) -> "nomenclature_dto":
        validator.validate(source, dict)

        dto = nomenclature_dto()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)
        dto.range_code = self.try_get_value("range_code", source)
        dto.group_code = self.try_get_value("group_code", source)

        return dto
    

