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
        if value is None or str(value).strip() == "":
            self.__error_text = ""
            return
        self.__error_text = str(value).strip()

    """
    Очистить ошибку
    """
    def clear_error(self) -> None:
        self.__error_text = ""

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