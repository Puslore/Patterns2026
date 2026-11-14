from Src.Core.entity_model import entity_model
from Src.Core.validator import validator, argument_exception

"""
Модель единицы измерения
"""
class range_model(entity_model):
    """Единица измерения с коэффициентом пересчета в базовую единицу."""

    __value:int = 1
    __base:'range_model' = None

    def __init__(self):
        super().__init__()
        
    """
    Значение коэффициента пересчета
    """
    @property
    def value(self) -> int:
        return self.__value
    
    @value.setter
    def value(self, value: int):
        validator.validate(value, int)
        if value <= 0:
             raise argument_exception("Некорректный аргумент!")
        self.__value = value


    """
    Базовая единица измерения
    """
    @property
    def base(self):
        return self.__base
    
    @base.setter
    def base(self, value):
        self.__base = value

    """
    Фабричный метод - создать киллограмм
    """
    @staticmethod
    def create_killogramm() -> "range_model":
        gramm  =     range_model()
        gramm.name = "Грамм"

        result = range_model()
        result.value = 1000
        result.base = gramm
        result.name = "Коллограмм"

        return result

    @staticmethod
    def create_gram() -> "range_model":
        """Создать базовую единицу измерения массы — грамм."""
        result = range_model()
        result.name = "Грамм"
        return result

    @staticmethod
    def create_piece() -> "range_model":
        """Создать единицу измерения количества — штуку."""
        result = range_model()
        result.name = "Штука"
        return result

    @staticmethod
    def create_milliliter() -> "range_model":
        """Создать единицу измерения объема — миллилитр."""
        result = range_model()
        result.name = "Миллилитр"
        return result

    @staticmethod
    def create_litr() -> "range_model":
        """Фабричный метод - создать литр."""
        ml = range_model.create_milliliter()

        result = range_model()
        result.value = 1000
        result.base = ml
        result.name = "Литр" 

        return result

    @staticmethod
    def create_thing() -> "range_model":
        """Фабричный метод - создать штуки."""
        result = range_model()
        result.name = "Штуки"
        return result


    
   

    