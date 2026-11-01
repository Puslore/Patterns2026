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