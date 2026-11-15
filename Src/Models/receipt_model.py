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
        if value is None:
            self.__comments = ""
            return
        if not isinstance(value, str):
            raise argument_exception("Некорректный тип для комментария!")
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
    def add(self, ingredient) -> None:
        from Src.Models.nomenclature_model import nomenclature_model
        if not isinstance(ingredient, (ingredient_model, nomenclature_model)):
            validator.validate(ingredient, ingredient_model)
        self.__items.append( ingredient )
        self.__refresh()

    """
    Удалить из состава ингредиент
    """
    def delete(self, ingredient) -> None:
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
            self.__brutto += getattr(item, "brutto", 0)
            self.__netto += getattr(item, "netto", 0)      

    def get_references(self) -> list:
        """Вернуть все сущности, от которых зависит рецепт и его ингредиенты."""
        refs = super().get_references()
        for item in self.items:
            if item is not None:
                refs.append(item)
                if hasattr(item, "get_references"):
                    refs.extend(item.get_references())
        unique_refs = []
        for r in refs:
            if r is not None and r not in unique_refs:
                unique_refs.append(r)
        return unique_refs

    def update_from(self, source):
        """Обновить состояние рецепта данными из валидированного объекта."""
        super().update_from(source)
        self.comments = source.comments
        self.items.clear()
        for item in source.items:
            self.add(item)