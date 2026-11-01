from Src.Models.ingredient_model import ingredient_model
from Src.Core.validator import validator
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