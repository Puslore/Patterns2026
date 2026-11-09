from abc import ABC, abstractmethod
from Src.Core.abstract_model import abstact_model
from Src.Core.validator import validator


"""
Абстрактный класс для работы с Dto структурами
"""
class abstract_dto(ABC):

     """
     Фабричный метод для создания Dto
     """
     @abstractmethod 
     def from_domain_model(self, source: abstact_model) -> "abstract_dto":
          pass

     """
     Выполнить маппинг в доменную модель
     """     
     def mapping(self, cache:dict) -> "abstact_model":
          validator.validate(cache, dict)     
          pass

     """
     Фабричный метод для создания Dto
     """
     @abstractmethod 
     def from_dict(self, source:dict) -> "abstract_dto":
          pass

     """ Полное название класса (включая модули) """ 
     @property 
     def type(self) -> str:
          return f"{self.__class__.__module__}.{self.__class__.__qualname__}"
     
     @type.setter
     def type(self, value:str):
          pass

     """
     Получить указанное свойство из словаря безопасно
     """     
     def try_get_value(self, key:str, source:dict) -> object:
          validator.validate(key, str)
          validator.validate(source, dict)

          if key in source.keys():
               return source[ key ]
          else:
               return None
          
               
