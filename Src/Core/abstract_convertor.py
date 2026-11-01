from abc import ABC, abstractmethod
from Src.Core.validator import validator

"""
Абстрактный конвертор
"""
class abstract_convertor(ABC):
    # Сообщение об ошибке
    __error_text:str = ""

    """
    Выполнить сериализацию
    """
    @abstractmethod 
    def serialize(self, field: str, object:any) -> dict:
        validator.validate(field, str)
        pass

    """
    Выполнить десериализацию
    """  
    @abstractmethod   
    def deserialize(self, source: dict ) -> object:
        pass

    """
    Сообщение об ошибке
    """    
    @property    
    def error_text(self) -> str:
        return self.__error_text

    @error_text.setter
    def error_text(self, value:str)-> None:
        validator.validate (value, str)
        self.__error_text = value.strip()

    """
    Метод для загрузки и обработки исключений
    """
    def set_exception(self, ex: Exception):
        self.__error_text = f"Ошибка! Исключение {ex}"
    

