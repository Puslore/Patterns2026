from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.validator import validator

"""
Реализация модели ингрединета
"""
class ingredient_model(nomenclature_model):
    # Основание
    __base:"ingredient_model" = None
    __brutto:int = 0
    __netto:int = 0

    def __init__(self):
        super().__init__()

    """
    Переопределяю получение веса брутто
    """
    @property
    def brutto(self) -> int:
        result = self.__brutto
        if self.base is not None:
            result += self.base.brutto

        return result


    """
    Переопределяем получение веса нетто
    """
    @property
    def netto(self) -> int:
        result = self.__netto 
        if self.base is not None:
            result += self.base.netto

        return result    


    @brutto.setter
    def brutto(self, value:int) -> None:
        validator.validate(value, int)
        self.__brutto = value


    @netto.setter
    def netto(self, value:int) -> None:
        validator.validate(value, int)
        self.__netto = value     

    """
    Основание
    """
    @property
    def base(self ) -> "ingredient_model":
        return self.__base    

    @base.setter
    def base(self, value:"ingredient_model") -> None:
        validator.validate(value, ingredient_model)
        self.__base = value