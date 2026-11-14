from abc import ABC, abstractmethod
from Src.Core.validator import validator

"""
Абстрактный класс для обработки ошибки
"""
class abstract_error(ABC):
    # Сообщение об ошибке
    __error_text:str = ""


    """
    Сообщение об ошибке
    """    
    @property    
    def error_text(self) -> str:
        return self.__error_text

    @error_text.setter
    def error_text(self, value:str) -> None:
        validator.validate (value, str)
        self.__error_text = value.strip()

    """
    Флаг есть ошибка
    """
    @property
    def is_error(self) -> bool:
        if self.__error_text.strip() == "":
            return False
        else:
            return True

    """
    Метод для загрузки и обработки исключений
    """
    def set_exception(self, ex: Exception):
        self.__error_text = f"Ошибка! Исключение {ex}"