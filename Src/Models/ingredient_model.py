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

    @property
    def nomenclature(self):
        """Номенклатура, на которой основан ингредиент (если задана)."""
        return getattr(self, "_ingredient_model__nomenclature", None)

    @nomenclature.setter
    def nomenclature(self, value):
        self.__nomenclature = value

    def get_references(self) -> list:
        """Вернуть зависимости ингредиента (базовый ингредиент, группа, единица, номенклатура)."""
        refs = super().get_references()
        if self.base is not None:
            refs.append(self.base)
        nom = getattr(self, "_ingredient_model__nomenclature", None)
        if nom is not None:
            refs.append(nom)
        return refs

    def update_from(self, source):
        """Обновить состояние ингредиента из валидированного объекта."""
        super().update_from(source)
        self.base = source.base
        self.brutto = source.brutto
        self.netto = source.netto
        if hasattr(source, "nomenclature"):
            self.nomenclature = source.nomenclature