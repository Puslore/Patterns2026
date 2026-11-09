from abc import ABC, abstractmethod
from Src.Core.validator import validator
from Src.Core.abstract_error import abstract_error

"""
Абстрактный конвертор
"""
class abstract_convertor(abstract_error):

    def __init__(self):
        super().__init__()

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

  
    

