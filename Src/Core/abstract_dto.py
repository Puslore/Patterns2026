from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstact_model


"""
Абстрактный класс для работы с Dto структурами
"""
class abstract_dto(ABC):

     """
     Фабричный метод для создания Dto
     """
     @abstractmethod 
     def from_domain_model(source: abstact_model) -> "abstract_dto":
          pass

     """ Полное название класса (включая модули) """ 
     @property 
     def type(self) -> str:
          return f"{self.__class__.__module__}.{self.__class__.__qualname__}"
     
     @type.setter
     def type(self, value:str):
          pass