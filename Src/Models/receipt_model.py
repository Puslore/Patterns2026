from Src.Core.validator import validator
from Src.Core.entity_model import entity_model
from Src.Models.ingredient_model import ingredient_model

"""
Реализация модели рецепта (агрегат)
"""
class receipt_model(entity_model):
    # Состав рецепта
    __items:list[ingredient_model]
    # Вес брутто
    __brutto:int = 0
    # Вес нетто
    __netto:int = 0
    # Описание процесса приготовления
    __comments:str = ""

    def __init__(self): 
        # Инициализация пустого списка ингредиентов 
        self.__items = []
        super().__init__()

    """
    Вес брутто    
    """
    @property
    def brutto(self) -> int:
        return self.__brutto

    """
    Вес нетто
    """
    @property
    def netto(self) -> int:
        return self.__netto    

    """
    Описание процесса
    """
    @property
    def comments(self) -> str:
        return self.__comments    

    @comments.setter
    def comments(self, value:str) -> None:
        validator.validate(value, str)
        self.__comments = value.strip()

    """
    Состав рецепта
    """
    @property
    def items(self) -> list[ingredient_model]:
        return self.__items    

    """
    Добавить в состав новый ингредиент
    """
    def add(self, ingredient:ingredient_model) -> None:
        validator.validate(ingredient, ingredient_model)
        self.__items.append( ingredient )
        self.__refresh()

    """
    Удалить из состава ингредиент
    """
    def delete(self, ingredient:ingredient_model) -> None:
        validator.validate(ingredient, ingredient_model)
        if ingredient in self.__items: 
            self.__items.remove(ingredient) 
            self.__refresh()

    """
    Пересчитать вес брутто и нетто
    """
    def __refresh(self) -> None:
        self.__brutto = 0
        self.__netto = 0
        for item in self.__items:
            self.__brutto += item.brutto
            self.__netto += item.netto


    """
    Уникальный код
    """
    @property
    def unique_code(self) -> str:
        super
        return self._abstact_model__unique_code      