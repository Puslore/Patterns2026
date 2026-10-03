from abc import ABC
from Src.Core.validator import validator

"""
Абстрактный класс для реализации загрузки и обработки данных
"""
class abstract_manager(ABC):
# Флаг. Загрузка и обработка завершена успешно
    __is_loaded:bool = False
   
    """
    Загрузить данные
    """
    def load(self, file_name:str = "") -> None:
        pass

    """
    Обработать загруженные данные
    """    
    def build(self) -> bool:
        pass

    """
    Флаг. Данные подготовлены
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded   

    @is_loaded.setter
    def is_loaded(self, value:bool) -> None:
        validator.validate(value, bool)
        self.__is_loaded = value
         

