from Src.Models.ingredient_model import ingredient_model
from Src.Core.validator import validator, operation_exception
from Src.Core.abstract_dto import abstract_dto


"""
Dto для описания ингредиента
"""
class ingredient_dto (abstract_dto):
    # Код
    __unique_code: str = ""

    # Наименование
    __name: str = ""

    # Код базового ингредиента
    __base_code: str = ""

    # Вес брутто
    __brutto: int = 0

    # Вес нетто
    __netto: int = 0

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
    Код базового ингредиента
    """
    @property
    def base_code(self) -> str:
        return self.__base_code

    @base_code.setter
    def base_code(self, value: str) -> None:
        self.__base_code = value.strip()

    """
    Вес брутто
    """
    @property
    def brutto(self) -> int:
        return self.__brutto

    @brutto.setter
    def brutto(self, value: int) -> None:
        self.__brutto = value

    """
    Вес нетто
    """
    @property
    def netto(self) -> int:
        return self.__netto

    @netto.setter
    def netto(self, value: int) -> None:
        self.__netto = value

    """
    Фабричный метод создания DTO из доменной модели
    """
    def from_domain_model(self, source: ingredient_model) -> "ingredient_dto":
        validator.validate(source, ingredient_model)
        
        dto = ingredient_dto()
        dto.unique_code = source.unique_code
        dto.name = source.name
        dto.brutto = source.brutto
        dto.netto = source.netto
        
        if source.base is not None:
            dto.base_code = source.base.unique_code
            
        return dto

    """
    Выполнить маппинг в доменную модель
    """
    def mapping(self, cache:dict) -> ingredient_model:
        super().mapping(cache)

        domain = ingredient_model()
        domain.unique_code = self.unique_code
        domain.name = self.name
        domain.brutto = self.brutto
        domain.netto = self.netto

        # Добавляем основу
        if self.base_code not in cache.keys():
            raise operation_exception(f"Невозможно получить объект с кодом {self.base_code} из хранилища. Тип {type(domain.base)}.")
        
        domain.base = cache[ self.base_code ]
        cache[ domain.unique_code ] = domain

        return domain

    def from_dict(self, source:dict) -> "ingredient_dto":
        validator.validate(source, dict)

        dto = ingredient_model()
        dto.unique_code = self.try_get_value("unique_code", source)
        dto.name = self.try_get_value("name", source)
        dto.range = self.try_get_value("range", source)
        dto.group = self.try_get_value("group", source)
        dto.netto = self.try_get_value("netto", source)
        dto.brutto = self.try_get_value("brutto", source)
        dto.base = self.try_get_value("base", source)

        return dto